"""
Steps 09 + 10 — export JSON building and section-aware RAG chunking.

Refactored from Aiveilix-pipline so it operates on in-memory ElementRecord /
PageMeta objects instead of DocumentElement / DocumentPage DB rows (those
tables are not part of the integrated schema).
"""

import uuid
from dataclasses import dataclass, field

from app.services.processing_v3.layout import ElementRecord


@dataclass
class PageMeta:
    page_number: int
    width: int
    height: int
    page_id: str
    screenshot_uri: str | None = None
    ocr_status: str = "skipped_native_text"
    raw_ocr_uri: str | None = None


@dataclass
class ChunkRecord:
    id: str
    page_start: int
    page_end: int
    element_ids: list[str]
    text: str
    chunk_type: str
    metadata: dict = field(default_factory=dict)


# ── Step 09: structured export JSON ───────────────────────────────────────────

def _element_to_dict(elem: ElementRecord) -> dict:
    meta = elem.metadata or {}
    out: dict = {
        "id": elem.id,
        "type": elem.type,
        "content": elem.content,
        "bbox": elem.bbox,
        "source": elem.source,
        "confidence": elem.confidence,
        "metadata": meta,
        "sort_order": elem.sort_order,
        "image_uri": meta.get("asset_uri"),
    }
    if "asset_uri" in meta:
        out["asset_uri"] = meta["asset_uri"]
    return out


def build_export_json(
    doc_meta: dict,
    pages: list[PageMeta],
    elements: list[ElementRecord],
) -> dict:
    """doc_meta: {schema_version, doc_id, filename, mime_type, source_file_uri, page_count}"""
    elements_by_page: dict[int, list[ElementRecord]] = {}
    for elem in elements:
        elements_by_page.setdefault(elem.page_number, []).append(elem)

    pages_out = []
    for page in sorted(pages, key=lambda p: p.page_number):
        page_elements = sorted(
            elements_by_page.get(page.page_number, []),
            key=lambda e: e.sort_order,
        )
        pages_out.append({
            "page": page.page_number,
            "width": page.width,
            "height": page.height,
            "screenshot_uri": page.screenshot_uri,
            "ocr_status": page.ocr_status,
            "raw_ocr_uri": page.raw_ocr_uri,
            "elements": [_element_to_dict(elem) for elem in page_elements],
        })

    return {
        "schema_version": doc_meta.get("schema_version", "1.0"),
        "doc_id": doc_meta["doc_id"],
        "filename": doc_meta.get("filename", ""),
        "mime_type": doc_meta.get("mime_type", ""),
        "source_file_uri": doc_meta.get("source_file_uri", ""),
        "page_count": doc_meta.get("page_count", len(pages_out)),
        "pages": pages_out,
    }


# ── Step 10: section-aware chunking ───────────────────────────────────────────

# Tuning knobs (token counts; ~4 chars/token heuristic).
# Target chunk size is ~200-400 tokens. Sections under _TARGET_MAX_TOKENS are
# kept whole; larger ones are split between elements; chunks under
# _FRAGMENT_TOKENS are merged into a neighbour.
_TARGET_MAX_TOKENS = 400      # split sections that grow beyond this
_FRAGMENT_TOKENS = 60         # anything below this is merged into a neighbour


def _count_tokens(text: str) -> int:
    """Cheap token estimate consistent with the orchestrator's len(text)//4."""
    return max(1, len(text) // 4)


def _visual_text(elem: ElementRecord) -> str:
    meta = elem.metadata or {}
    line = f"[Visual: {elem.type}] {elem.content}"
    if meta.get("visible_text"):
        line += f" (text visible: {meta['visible_text']})"
    return line


def _element_text(elem: ElementRecord) -> str:
    """Render an element to the text that goes into a chunk."""
    if elem.source == "visual_understanding":
        return _visual_text(elem)
    return elem.content or ""


def _make_chunk(
    page_number: int,
    elements: list[ElementRecord],
    text: str,
    chunk_type: str,
    section_heading: str | None = None,
) -> ChunkRecord:
    sources = {e.source for e in elements}
    source = next(iter(sources)) if len(sources) == 1 else "mixed"
    visual_count = sum(1 for e in elements if e.source == "visual_understanding")
    metadata = {
        "source": source,
        "page_numbers": [page_number],
        "element_count": len(elements),
        "has_visual_elements": visual_count > 0,
        "visual_count": visual_count,
        "token_count": _count_tokens(text),
    }
    if section_heading:
        metadata["section_heading"] = section_heading
    return ChunkRecord(
        id=str(uuid.uuid4()),
        page_start=page_number,
        page_end=page_number,
        element_ids=[e.id for e in elements],
        text=text,
        chunk_type=chunk_type,
        metadata=metadata,
    )


@dataclass
class _Section:
    """A heading (optional) plus the body elements that belong under it."""
    page_number: int
    heading: ElementRecord | None
    body: list[ElementRecord] = field(default_factory=list)

    @property
    def elements(self) -> list[ElementRecord]:
        return ([self.heading] if self.heading else []) + self.body

    @property
    def heading_text(self) -> str | None:
        return self.heading.content if self.heading else None

    def tokens(self) -> int:
        return sum(_count_tokens(_element_text(e)) for e in self.elements)


def _section_to_chunks(section: _Section) -> list[ChunkRecord]:
    """Turn one section into one or more sane-sized chunks, splitting only
    between elements so no sentence is ever cut."""
    elems = section.elements
    if not elems:
        return []

    heading_txt = section.heading_text
    chunk_type = "section" if section.heading else "page_text"

    # Build per-element rendered text, dropping empties but tracking the element.
    rendered: list[tuple[ElementRecord, str]] = []
    for e in elems:
        txt = _element_text(e).strip()
        if txt:
            rendered.append((e, txt))
    if not rendered:
        return []

    total_tokens = sum(_count_tokens(t) for _, t in rendered)
    if total_tokens <= _TARGET_MAX_TOKENS:
        text = "\n".join(t for _, t in rendered).strip()
        return [_make_chunk(
            section.page_number, [e for e, _ in rendered], text,
            chunk_type, heading_txt,
        )]

    # Too big: split between elements. Re-attach the heading to the first group.
    groups: list[list[tuple[ElementRecord, str]]] = []
    current: list[tuple[ElementRecord, str]] = []
    current_tokens = 0
    for elem, txt in rendered:
        t = _count_tokens(txt)
        if current and current_tokens + t > _TARGET_MAX_TOKENS:
            groups.append(current)
            current = []
            current_tokens = 0
        current.append((elem, txt))
        current_tokens += t
    if current:
        groups.append(current)

    chunks: list[ChunkRecord] = []
    for i, group in enumerate(groups):
        body_text = "\n".join(t for _, t in group).strip()
        # Repeat the heading on continuation chunks so each stays retrievable.
        if heading_txt and i > 0 and not group[0][0].type == "heading":
            text = f"{heading_txt}\n{body_text}"
        else:
            text = body_text
        chunks.append(_make_chunk(
            section.page_number, [e for e, _ in group], text,
            chunk_type, heading_txt,
        ))
    return chunks


def _merge_fragments(chunks: list[ChunkRecord], pages_order: list[int]) -> list[ChunkRecord]:
    """
    Merge any chunk below _FRAGMENT_TOKENS into an adjacent chunk on the SAME
    page (so page_start/page_end stay correct). Prefers merging forward into
    the next chunk, then backward. No content is dropped: the merged chunk
    keeps every element id and the concatenated text.
    """
    if not chunks:
        return chunks

    # Group by page to keep page boundaries intact.
    by_page: dict[int, list[ChunkRecord]] = {}
    for c in chunks:
        by_page.setdefault(c.page_start, []).append(c)

    merged_all: list[ChunkRecord] = []
    for page in pages_order:
        page_chunks = by_page.get(page)
        if not page_chunks:
            continue

        # Repeatedly merge the smallest fragment into a neighbour until none
        # remain (or only one chunk is left on the page).
        work = list(page_chunks)
        changed = True
        while changed and len(work) > 1:
            changed = False
            for i, c in enumerate(work):
                if _count_tokens(c.text) >= _FRAGMENT_TOKENS:
                    continue
                # Choose neighbour: prefer the smaller one to balance sizes.
                prev_c = work[i - 1] if i > 0 else None
                next_c = work[i + 1] if i < len(work) - 1 else None
                if prev_c is None and next_c is None:
                    break
                if next_c is None:
                    target_idx, order = i - 1, (prev_c, c)
                elif prev_c is None:
                    target_idx, order = i + 1, (c, next_c)
                elif _count_tokens(prev_c.text) <= _count_tokens(next_c.text):
                    target_idx, order = i - 1, (prev_c, c)
                else:
                    target_idx, order = i + 1, (c, next_c)

                work[target_idx] = _combine_chunks(page, order[0], order[1])
                work.pop(i)
                changed = True
                break
        merged_all.extend(work)

    return merged_all


def _combine_chunks(page: int, first: ChunkRecord, second: ChunkRecord) -> ChunkRecord:
    text = f"{first.text}\n{second.text}".strip()
    element_ids = first.element_ids + second.element_ids
    sources = set()
    for c in (first, second):
        sources.add(c.metadata.get("source", "unknown"))
    source = next(iter(sources)) if len(sources) == 1 else "mixed"
    visual_count = (
        first.metadata.get("visual_count", 0) + second.metadata.get("visual_count", 0)
    )
    heading = first.metadata.get("section_heading") or second.metadata.get("section_heading")
    chunk_type = first.chunk_type if first.chunk_type == second.chunk_type else "section"
    metadata = {
        "source": source,
        "page_numbers": [page],
        "element_count": len(element_ids),
        "has_visual_elements": visual_count > 0,
        "visual_count": visual_count,
        "token_count": _count_tokens(text),
    }
    if heading:
        metadata["section_heading"] = heading
    return ChunkRecord(
        id=str(uuid.uuid4()),
        page_start=page,
        page_end=page,
        element_ids=element_ids,
        text=text,
        chunk_type=chunk_type,
        metadata=metadata,
    )


def build_chunks(elements: list[ElementRecord], pages: list[PageMeta]) -> list[ChunkRecord]:
    """
    Section-aware chunker.

    Guarantees:
      * every element with non-empty content lands in exactly one chunk —
        nothing is dropped;
      * a heading starts a section and stays glued to the paragraphs that
        follow it (and is repeated on continuation chunks);
      * chunks target ~200-400 tokens; fragments under ~60 tokens are merged
        into a neighbour on the same page;
      * splitting only ever happens between elements, so a sentence is never
        cut in half;
      * visual elements are kept inside their surrounding section so they are
        retrievable alongside the section heading.
    """
    elements_by_page: dict[int, list[ElementRecord]] = {}
    for elem in elements:
        elements_by_page.setdefault(elem.page_number, []).append(elem)

    pages_order = [p.page_number for p in sorted(pages, key=lambda p: p.page_number)]

    raw_chunks: list[ChunkRecord] = []
    for page_number in pages_order:
        page_elements = sorted(
            elements_by_page.get(page_number, []),
            key=lambda e: e.sort_order,
        )
        # Keep only elements that contribute content; skip truly empty ones.
        page_elements = [e for e in page_elements if (e.content or "").strip()]
        if not page_elements:
            continue

        # Group elements into sections. A heading opens a new section;
        # everything else (paragraphs, OCR text, visuals) joins the current
        # section. Content before the first heading forms a headless section.
        sections: list[_Section] = []
        current: _Section | None = None
        for elem in page_elements:
            if elem.type == "heading" and elem.source != "visual_understanding":
                current = _Section(page_number=page_number, heading=elem)
                sections.append(current)
            else:
                if current is None:
                    current = _Section(page_number=page_number, heading=None)
                    sections.append(current)
                current.body.append(elem)

        for section in sections:
            raw_chunks.extend(_section_to_chunks(section))

    # Merge fragments so no tiny chunk survives.
    return _merge_fragments(raw_chunks, pages_order)
