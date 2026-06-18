"""
Neutral tool registry.

Each tool is declared ONCE here and is a thin wrapper around code that
already exists (retrieval, structural fetchers, web, file fns). No
retrieval / pipeline logic is rewritten. The model picks tools, the
harness runs them.

Each tool returns a `ToolResult` whose `summary` is what the model sees
as the observation, and whose `pending_docs` / `pending_web` go into
the mechanical source pool.
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent.harness.contract import TurnInput
from app.services.agent.harness.state import AgentState
from app.services.mcp import tools as bucket_data
from app.services.agent import retrieval as retrieval_mod
from app.services.agent import tools as legacy_tools
from app.services.agent import web as web_mod

logger = logging.getLogger(__name__)

# Below this best-match score, whole-bucket retrieval is treated as off-topic and
# the model is told NOT to answer from it (it should read the file or say
# "not covered"). Mirrors service._WEAK_RETRIEVAL_MIN_SCORE on the query path —
# the guard the standalone query() has and the harness was missing.
_WEAK_RETRIEVAL_MIN_SCORE = 0.40


# ─────────────────────────────────────────────────────── result + tool model ──

@dataclass(slots=True)
class ToolResult:
    """What a tool returns. `summary` is the observation the model reads."""
    summary: str
    pending_docs: list[dict[str, object]] = field(default_factory=list)
    pending_web: list[dict[str, object]] = field(default_factory=list)
    active_file_update: uuid.UUID | None = None  # the tool found / confirmed this file
    web_off_reply: str | None = None             # tool refused because web is off
    user_visible_label: str | None = None        # short narration hint for the UI
    used_memory: bool = False
    error: str | None = None
    success: bool = True


ToolFn = Callable[[AgentState, TurnInput, AsyncSession, dict[str, object]], Awaitable[ToolResult]]


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    params_schema: dict[str, object]   # JSON Schema for the function arguments
    fn: ToolFn
    web_only: bool = False             # hidden when web is off + override is not True


# ─────────────────────────────────────────────────────────── helper utilities ──

def _uuid(value: object) -> uuid.UUID | None:
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except Exception:
        return None


def _resolve_file_uuid(
    raw: object,
    bucket_files: list,  # list[BucketFile]
) -> uuid.UUID | None:
    """Accept either a UUID string or a (case-insensitive) file name.

    Only resolves to a file the thread is allowed to use: `bucket_files` is
    already filtered to the thread's scope, so a raw UUID for a blocked (or
    cross-bucket) file returns None instead of leaking it.
    """
    if not raw:
        return None
    allowed = {f.file_id for f in bucket_files}
    direct = _uuid(raw)
    if direct is not None:
        return direct if direct in allowed else None
    needle = str(raw).strip().lower()
    if not needle:
        return None
    for f in bucket_files:
        if f.name.lower() == needle or f.name.lower().split(".")[0] == needle:
            return f.file_id
    return None


def _truncate(text: str, limit: int = 2400) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + " …"


def _doc_source_payload(chunk) -> dict[str, object]:
    label = (
        f"[doc] {chunk.file_name} — Overview"
        if chunk.is_summary
        else f"[doc] {chunk.file_name} — Page {chunk.page}"
    )
    return {
        "kind": "document",
        "label": label,
        "file_id": str(chunk.file_id),
        "chunk_id": str(chunk.chunk_id),
        "page": chunk.page,
        "is_summary": chunk.is_summary,
        "score": round(float(chunk.score or 0.0), 4),
    }


def _web_source_payload(result) -> dict[str, object]:
    from urllib.parse import urlparse
    parsed = urlparse(result.url)
    label = f"[web] {parsed.netloc}{parsed.path or ''}"
    return {
        "kind": "web",
        "label": label,
        "url": result.url,
        "title": result.title,
        "score": round(float(result.score or 0.0), 4),
    }


# ───────────────────────────────────────────────────────────────────── tools ──
#
# Each tool function: async def t(state, turn, db, args) -> ToolResult


async def _t_list_files(state, turn, db, args):
    # Use the thread's scoped file list (already filtered), never the raw bucket,
    # so blocked files are not exposed to the agent.
    items = turn.bucket_files
    if not items:
        return ToolResult(summary="(no files are available to this thread)")
    lines = []
    for f in items:
        marker = " [agent-written]" if f.is_agent_written else ""
        lines.append(f"- {f.name} (id={f.file_id}, status={f.status}){marker}")
    return ToolResult(summary="Files available to this thread:\n" + "\n".join(lines))


async def _t_list_bucket_members(state, turn, db, args):
    """Who can access this bucket — the workspace owner plus every team member
    with an access grant, and each member's permissions."""
    data = await bucket_data.fetch_bucket_members(db, turn.bucket_id)
    if data is None:
        return ToolResult(summary="Could not load members — bucket not found.", success=False)
    members = data["members"]
    lines = [
        f"This bucket is accessible to {data['total_people']} "
        f"{'person' if data['total_people'] == 1 else 'people'}:",
        f"- {data['owner']['name']} — workspace owner (full access)",
    ]
    if members:
        for m in members:
            granted = [
                k[len("can_"):].replace("_", " ")
                for k, v in m["permissions"].items()
                if v
            ]
            perm_str = ", ".join(granted) if granted else "view & chat only"
            lines.append(f"- {m['name']} — team member ({perm_str})")
    else:
        lines.append("- (no team members have been granted access — owner only)")
    return ToolResult(summary="\n".join(lines))


async def _t_get_file_summary(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None:
        return ToolResult(summary="error: file_id is required and must match a real file.", success=False)
    result = await legacy_tools.get_file_summary(db, file_id=file_id)
    if not result.found:
        return ToolResult(summary=f"No stored summary for '{result.file_name or file_id}'.", success=False)
    summary = _truncate(result.summary, limit=2000)
    return ToolResult(
        summary=f"Summary of {result.file_name}:\n{summary}",
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {result.file_name} — Overview",
            "file_id": str(file_id),
            "is_summary": True,
        }],
    )


async def _t_read_file(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None:
        return ToolResult(summary="error: file_id is required and must match a real file.", success=False)
    result = await legacy_tools.read_file(db, bucket_id=turn.bucket_id, file_id=file_id)
    if not result.success:
        return ToolResult(summary=f"Could not read file: {result.error or 'unknown error'}", success=False)
    content = _truncate(result.content, limit=4000)
    return ToolResult(
        summary=f"Content of {result.file_name}:\n{content}",
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {result.file_name} — Full file",
            "file_id": str(file_id),
            "is_summary": False,
        }],
    )


async def _t_search_documents(state, turn, db, args):
    query = (args.get("query") or "").strip()
    if not query:
        return ToolResult(summary="error: query is required.", success=False)

    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    # Preserve the 3 states: None = full bucket, [] = no files, [...] = subset.
    scope = turn.scope_file_ids

    if file_id is not None:
        chunks = await retrieval_mod.search_bucket_documents_for_files(
            db, turn.bucket_id, query, [file_id], limit=6,
        )
        active_update = file_id
    else:
        chunks = await retrieval_mod.search_bucket_documents_with_file_coverage(
            db, turn.bucket_id, query, limit=6, allowed_file_ids=scope,
        )
        active_update = chunks[0].file_id if chunks else None

    if not chunks:
        return ToolResult(
            summary=f"No matches for '{query}' in the bucket.",
            success=False,
        )

    # Weak-retrieval guard (whole-bucket searches only). If the best match is
    # below the trust threshold, the hits are almost certainly off-topic — do NOT
    # let the model summarize from them or guess from the file name. A file-scoped
    # search (file_id given) is exempt: the user explicitly named that file.
    best_score = max((float(c.score or 0.0) for c in chunks), default=0.0)
    if file_id is None and best_score < _WEAK_RETRIEVAL_MIN_SCORE:
        return ToolResult(
            summary=(
                f"Weak retrieval for '{query}' (best match {best_score:.2f}, below the trust "
                f"threshold {_WEAK_RETRIEVAL_MIN_SCORE:.2f}). These snippets are probably off-topic. "
                f"Do NOT summarize or answer from them, and do NOT guess from the file name. "
                f"Either open the relevant file directly with get_file_summary / get_page, or tell "
                f"the user plainly that this isn't covered in the bucket."
            ),
            success=False,
        )

    lines = []
    pending = []
    for idx, c in enumerate(chunks, start=1):
        label = f"#{idx} {c.file_name} (page {c.page})" if not c.is_summary else f"#{idx} {c.file_name} (overview)"
        lines.append(f"{label}\n{_truncate(c.content, 2400)}")
        pending.append(_doc_source_payload(c))
    return ToolResult(
        summary=f"Search results for '{query}':\n\n" + "\n\n".join(lines),
        pending_docs=pending,
        active_file_update=active_update,
    )


async def _t_get_file_stats(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    stats = await bucket_data.fetch_file_stats(db, turn.bucket_id, file_id)
    if stats is None:
        return ToolResult(summary="No stats available — file not found or not ready.", success=False)
    outline = stats.get("section_outline") or []
    outline_preview = "\n".join(f"  p.{s['page']}: {s['heading']}" for s in outline[:25])
    extra = f"\n  … {len(outline) - 25} more sections" if len(outline) > 25 else ""
    summary = (
        f"File: {stats['file_name']}\n"
        f"  pages: {stats['page_count']}, images: {stats['image_count']}, sections: {stats['section_count']}\n"
        f"Outline (first 25):\n{outline_preview}{extra}"
    )
    return ToolResult(
        summary=summary,
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {stats['file_name']} — Structure",
            "file_id": str(file_id),
            "is_summary": True,
        }],
    )


async def _t_read_outline(state, turn, db, args):
    """Return the COMPLETE section outline (every heading + its page) — the
    document's table of contents. Use for 'list all headings / headlines /
    sections'. Paged at 200 headings per call via `offset` for huge docs."""
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    try:
        offset = max(0, int(args.get("offset") or 0))
    except (TypeError, ValueError):
        offset = 0

    PAGE = 200
    stats = await bucket_data.fetch_file_stats(db, turn.bucket_id, file_id)
    if stats is None:
        return ToolResult(summary="No outline — file not found or not ready.", success=False)
    outline = stats.get("section_outline") or []
    total = len(outline)
    if total == 0:
        return ToolResult(
            summary=f"{stats['file_name']} has no detected section headings (no outline).",
            success=False,
        )
    window = outline[offset:offset + PAGE]
    lines = [f"  {i}. p.{s.get('page')}: {s.get('heading')}" for i, s in enumerate(window, start=offset + 1)]
    next_offset = offset + len(window)
    footer = (
        f"\n— {total - next_offset} more headings. Call read_outline again with offset={next_offset}."
        if next_offset < total else
        f"\n— END. All {total} headings listed."
    )
    return ToolResult(
        summary=(
            f"OUTLINE — {stats['file_name']} (headings {offset + 1}–{next_offset} of {total}):\n"
            + "\n".join(lines) + footer
        ),
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {stats['file_name']} — Outline",
            "file_id": str(file_id),
            "is_summary": True,
        }],
    )


async def _t_get_page(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    try:
        ps = int(args.get("start") or args.get("page") or 1)
        pe = int(args.get("end") or args.get("page") or ps)
    except (TypeError, ValueError):
        return ToolResult(summary="error: start/end must be integers.", success=False)
    pages = await bucket_data.fetch_pages(db, turn.bucket_id, file_id, ps, pe)
    if pages is None:
        return ToolResult(summary="No pages found — file not ready.", success=False)
    page_chunks = pages.get("chunks", [])
    chunk_lines = [f"  p.{c['page']:>3}  {_truncate(c['content'], 1200)}" for c in page_chunks[:30]]
    more = f"\n  … {len(page_chunks) - 30} more chunks on this range — narrow start/end to read them." if len(page_chunks) > 30 else ""
    summary = (
        f"File: {pages['file_name']}\n"
        f"Pages {pages['page_start']}–{pages['page_end']} (of {pages['total_pages_in_file']}):\n"
        + "\n".join(chunk_lines) + more
    )
    return ToolResult(
        summary=summary,
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {pages['file_name']} — Pages {pages['page_start']}–{pages['page_end']}",
            "file_id": str(file_id),
            "page": pages["page_start"],
            "is_summary": False,
        }],
    )


async def _t_get_visual(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    try:
        index = int(args.get("index"))
    except (TypeError, ValueError):
        return ToolResult(summary="error: index must be an integer.", success=False)
    payload = await bucket_data.fetch_visual(db, turn.bucket_id, file_id, index)
    if payload is None or payload.get("visual") is None:
        msg = payload.get("error") if payload else "visual not found"
        return ToolResult(summary=f"Could not get visual #{index}: {msg}", success=False)
    v = payload["visual"]
    sect = payload.get("enclosing_section") or {}
    sect_line = f"  enclosing section: {sect.get('heading')!r} (p.{sect.get('page')})" if sect else ""
    summary = (
        f"File: {payload['file_name']}\n"
        f"Visual #{payload['requested_index']} of {payload['total_visuals']}:\n"
        f"  page: {v['page']}, type: {v.get('type')}, asset_type: {v.get('asset_type')}\n"
        f"  description: {v.get('description')}\n"
        f"  text_inside: {v.get('text_inside') or '(none)'}\n"
        f"{sect_line}"
    )
    return ToolResult(
        summary=summary,
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {payload['file_name']} — Visual #{payload['requested_index']}",
            "file_id": str(file_id),
            "page": v["page"],
            "is_summary": False,
        }],
    )


async def _t_list_visuals(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    page = args.get("page")
    type_filter = args.get("type")
    try:
        offset = max(0, int(args.get("offset") or 0))
    except (TypeError, ValueError):
        offset = 0
    BATCH = 80
    listing = await bucket_data.fetch_visual_list(
        db, turn.bucket_id, file_id,
        page=int(page) if page is not None and str(page).isdigit() else None,
        type_filter=str(type_filter) if type_filter else None,
        limit=BATCH,
        offset=offset,
    )
    if listing is None:
        return ToolResult(summary="No visual list — file not ready.", success=False)
    visuals = listing.get("visuals", [])
    head_lines = [
        f"  #{v['index']:>3}  p.{v['page']:>3}  type={v.get('type','?'):<12}  {(v.get('description') or '')[:160]}"
        for v in visuals
    ]
    filtered_count = int(listing.get("filtered_count") or len(visuals))
    next_offset = offset + len(visuals)
    shown_range = f"{offset + 1}–{next_offset}" if visuals else "0"
    extra = (
        f"\n  … {filtered_count - next_offset} more visuals. Call list_visuals again with offset={next_offset}."
        if next_offset < filtered_count else
        f"\n  — END. All {filtered_count} matching visuals listed."
    )
    filt = []
    if type_filter:
        filt.append(f"type={type_filter}")
    if page is not None:
        filt.append(f"page={page}")
    filt_line = (" (" + ", ".join(filt) + ")") if filt else ""
    summary = (
        f"File: {listing['file_name']}\n"
        f"Total visuals: {listing.get('total_visuals')}{filt_line}; showing {shown_range} of {filtered_count}\n"
        + "\n".join(head_lines) + extra
    )
    return ToolResult(
        summary=summary,
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {listing['file_name']} — Visuals manifest",
            "file_id": str(file_id),
            "is_summary": True,
        }],
    )


async def _t_get_section(state, turn, db, args):
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    heading = (args.get("heading") or "").strip()
    if not heading:
        return ToolResult(summary="error: heading is required.", success=False)
    payload = await bucket_data.fetch_section(db, turn.bucket_id, file_id, heading)
    if payload is None:
        return ToolResult(summary="No section data — file not ready.", success=False)
    if not payload.get("matched_heading"):
        return ToolResult(
            summary=f"No section matched '{heading}' in {payload.get('file_name')}.",
            success=False,
        )
    chunk_lines = [f"  p.{c['page']:>3}  {_truncate(c['content'], 1200)}" for c in payload.get("chunks", [])[:40]]
    extra = (
        f"\n  … {payload['total_chunks'] - 40} more chunks in this section — read the whole file with read_all_chunks if you need them all"
        if payload.get("total_chunks", 0) > 40 else ""
    )
    summary = (
        f"File: {payload['file_name']}\n"
        f"Matched section: {payload['matched_heading']!r}\n"
        f"Pages {payload['page_start']}–{payload['page_end']}\n"
        + "\n".join(chunk_lines) + extra
    )
    return ToolResult(
        summary=summary,
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {payload['file_name']} — Section '{payload['matched_heading']}'",
            "file_id": str(file_id),
            "page": payload["page_start"],
            "is_summary": False,
        }],
    )


async def _t_read_all_chunks(state, turn, db, args):
    """Deterministic WHOLE-DOCUMENT reader. Returns every chunk of a file,
    grouped by page (within-page order is approximate — no chunk_index exists),
    batched by `offset` so large docs are paged through (map-reduce). This is the
    exhaustive path — use it for 'extract all / list every / summarize the whole
    file', NOT semantic search (which caps and undercounts). Completeness, not
    order, is what this guarantees."""
    file_id = _resolve_file_uuid(args.get("file_id"), turn.bucket_files)
    if file_id is None and len(turn.bucket_files) == 1:
        file_id = turn.bucket_files[0].file_id
    if file_id is None:
        return ToolResult(summary="error: file_id is required.", success=False)
    try:
        offset = max(0, int(args.get("offset") or 0))
    except (TypeError, ValueError):
        offset = 0

    BATCH = 40  # chunks per call — page through with offset for the rest
    payload = await bucket_data.fetch_chunks_list(db, turn.bucket_id, file_id)
    if payload is None:
        return ToolResult(summary="No content — file not found or not ready.", success=False)
    chunks = payload.get("chunks", [])
    total = payload.get("total_chunks", len(chunks))
    window = chunks[offset:offset + BATCH]
    if not window:
        return ToolResult(
            summary=f"No chunks at offset {offset} — the file has {total} chunks total.",
            success=False,
        )

    lines = [
        f"[chunk {i}/{total}] p.{c.get('page')}\n{_truncate(c.get('content', ''), 1500)}"
        for i, c in enumerate(window, start=offset + 1)
    ]
    next_offset = offset + len(window)
    if next_offset < total:
        footer = (
            f"\n\n— {total - next_offset} chunks still unread. To finish the FULL scan, "
            f"call read_all_chunks again with offset={next_offset}. Do not answer an "
            f"'all/every' question until you have read to the end."
        )
    else:
        footer = f"\n\n— END OF DOCUMENT. All {total} chunks have now been read."

    return ToolResult(
        summary=(
            f"FULL DOCUMENT SCAN — {payload['file_name']} "
            f"(chunks {offset + 1}–{next_offset} of {total}, grouped by page):\n\n"
            + "\n\n".join(lines)
            + footer
        ),
        active_file_update=file_id,
        pending_docs=[{
            "kind": "document",
            "label": f"[doc] {payload['file_name']} — Full scan",
            "file_id": str(file_id),
            "is_summary": False,
        }],
    )


async def _t_search_web(state, turn, db, args):
    # Web user-toggle: bucket_only blocks search outright.
    web_blocked = (
        turn.web_override is False
        or (turn.web_override is None and turn.web_mode == "bucket_only")
    )
    if web_blocked:
        reply = (
            "Your web mode is off — turn it on from the icon in the input bar, "
            "then ask me again."
        )
        return ToolResult(
            summary="Web mode is OFF. Tell the user exactly: " + json.dumps(reply),
            web_off_reply=reply,
            success=False,
        )
    query = (args.get("query") or "").strip()
    if not query:
        return ToolResult(summary="error: query is required.", success=False)
    results = await web_mod.search_web(query, max_results=5)
    if not results:
        return ToolResult(summary=f"No web results for '{query}'.", success=False)
    lines = []
    pending = []
    for idx, r in enumerate(results, start=1):
        lines.append(f"#{idx} {r.title}\n  {r.url}\n  {_truncate(r.snippet, 400)}")
        pending.append(_web_source_payload(r))
    return ToolResult(
        summary=f"Web results for '{query}':\n\n" + "\n\n".join(lines),
        pending_web=pending,
    )


async def _t_fetch_url(state, turn, db, args):
    url = (args.get("url") or "").strip()
    if not url:
        return ToolResult(summary="error: url is required.", success=False)
    result = await legacy_tools.fetch_url(url)
    if not result.success:
        return ToolResult(summary=f"Could not fetch {url}: {result.error}", success=False)
    return ToolResult(
        summary=f"Fetched {result.title or url}:\n{_truncate(result.content, 3200)}",
        pending_web=[{
            "kind": "web",
            "label": f"[web] {url}",
            "url": url,
            "title": result.title or url,
        }],
    )


async def _t_recall_memory(state, turn, db, args):
    query = (args.get("query") or "").strip()
    if not query:
        return ToolResult(summary="error: query is required.", success=False)
    chunks = await retrieval_mod.search_conversation_memory(
        db, turn.conversation_id, query, limit=5,
    )
    if not chunks:
        return ToolResult(summary=f"No relevant memory of past chat about '{query}'.", success=False)
    lines = [f"({c.role}) {_truncate(c.content, 500)}" for c in chunks]
    return ToolResult(
        summary=f"Memory of '{query}':\n\n" + "\n\n".join(lines),
        used_memory=True,
    )


async def _t_ask_user(state, turn, db, args):
    """Halt the loop and return a clarifying question to the user."""
    question = (args.get("question") or "").strip()
    options_raw = args.get("options") or []
    options = [str(o).strip() for o in options_raw if str(o).strip()][:4]
    if not question:
        return ToolResult(summary="error: question is required.", success=False)
    state.action_required = True
    state.action_type = "clarify"
    state.action_options = options or None
    state.clarifying_question = question
    return ToolResult(
        summary=f"(asked user: {question})",
        user_visible_label=question,
    )


async def _t_make_plan(state, turn, db, args):
    items_raw = args.get("items") or args.get("tasks") or []
    items = [str(t).strip() for t in items_raw if str(t).strip()][:10]
    if not items:
        return ToolResult(summary="error: items must be a non-empty list of tasks.", success=False)
    state.set_plan(items)
    return ToolResult(
        summary=f"plan set: {state.compact_plan_view()}",
    )


async def _t_update_plan(state, turn, db, args):
    try:
        item_id = int(args.get("id"))
    except (TypeError, ValueError):
        return ToolResult(summary="error: id must be an integer.", success=False)
    status = str(args.get("status") or "").strip().lower()
    if status not in ("pending", "in_progress", "done", "blocked"):
        return ToolResult(summary="error: status must be pending|in_progress|done|blocked.", success=False)
    state.update_plan_item(item_id, status)  # type: ignore[arg-type]
    return ToolResult(summary=f"plan: {state.compact_plan_view()}")


# ───────────────────────────────────────────────────── public registry build ──

def build_registry() -> dict[str, ToolDefinition]:
    """Single source of truth for what the brain can call."""
    defs: list[ToolDefinition] = [
        ToolDefinition(
            name="list_files",
            description=(
                "List every file in the current bucket with its status. "
                "Call ONCE per turn when you need to know what's available."
            ),
            params_schema={"type": "object", "properties": {}, "required": []},
            fn=_t_list_files,
        ),
        ToolDefinition(
            name="list_bucket_members",
            description=(
                "List the people who can access this bucket — the workspace owner plus "
                "every team member granted access, with each member's permissions. Use "
                "for 'who has access', 'how many users/people are in this bucket', "
                "'who's on this bucket', 'list the team members'. This is about PEOPLE, "
                "not files."
            ),
            params_schema={"type": "object", "properties": {}, "required": []},
            fn=_t_list_bucket_members,
        ),
        ToolDefinition(
            name="get_file_summary",
            description="Return the pre-computed AI summary of one file.",
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File UUID or exact file name."},
                },
                "required": ["file_id"],
            },
            fn=_t_get_file_summary,
        ),
        ToolDefinition(
            name="read_file",
            description=(
                "Read the raw content of a file (best for short agent-written .md files). "
                "For large documents, prefer search_documents or get_page."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File UUID or exact file name."},
                },
                "required": ["file_id"],
            },
            fn=_t_read_file,
        ),
        ToolDefinition(
            name="search_documents",
            description=(
                "Semantic search inside the bucket. Pass file_id to scope to ONE file "
                "(use this for 'in this file', 'in @name'). Leave file_id empty to search the whole bucket."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The thing you are looking for, in plain words."},
                    "file_id": {"type": "string", "description": "Optional. File UUID or exact name to scope to."},
                },
                "required": ["query"],
            },
            fn=_t_search_documents,
        ),
        ToolDefinition(
            name="get_file_stats",
            description=(
                "Get the structural stats of a file: page_count, image_count, section_count, "
                "and outline. Use for 'how many pages', 'what sections are there'."
            ),
            params_schema={
                "type": "object",
                "properties": {"file_id": {"type": "string"}},
                "required": ["file_id"],
            },
            fn=_t_get_file_stats,
        ),
        ToolDefinition(
            name="read_outline",
            description=(
                "List the COMPLETE table of contents — every section heading and its page. "
                "Use for 'list all headings / headlines / sections', or to navigate before "
                "opening a section. Unlike get_file_stats (which previews only the first 25), "
                "this returns ALL headings, 200 per call — page with `offset` until END."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File UUID or exact name."},
                    "offset": {"type": "integer", "description": "Heading offset to start from (0 first call)."},
                },
                "required": ["file_id"],
            },
            fn=_t_read_outline,
        ),
        ToolDefinition(
            name="get_page",
            description="Return the chunks on a specific page or page range of a file.",
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string"},
                    "start": {"type": "integer", "description": "First page (1-based)."},
                    "end": {"type": "integer", "description": "Last page (inclusive). Defaults to start."},
                },
                "required": ["file_id", "start"],
            },
            fn=_t_get_page,
        ),
        ToolDefinition(
            name="get_visual",
            description=(
                "Return the Nth image / figure / chart in a file (1-based). "
                "Use for 'the 3rd image', 'figure 4', 'visual #12'."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string"},
                    "index": {"type": "integer", "description": "1-based visual index."},
                },
                "required": ["file_id", "index"],
            },
            fn=_t_get_visual,
        ),
        ToolDefinition(
            name="list_visuals",
            description=(
                "List visuals in a file. Optional 'type' filter (chart, logo, icon, product_image, "
                "review_screenshot, cta_button, before_after_image), 'page' filter, and 'offset' "
                "for paging through long visual manifests."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string"},
                    "type": {"type": "string"},
                    "page": {"type": "integer"},
                    "offset": {"type": "integer", "description": "Visual offset to start from (0 first call; use the offset the previous call told you)."},
                },
                "required": ["file_id"],
            },
            fn=_t_list_visuals,
        ),
        ToolDefinition(
            name="get_section",
            description=(
                "Return the chunks of a named section / chapter / appendix from a file. "
                "Heading match is case-insensitive substring against the outline."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string"},
                    "heading": {"type": "string"},
                },
                "required": ["file_id", "heading"],
            },
            fn=_t_get_section,
        ),
        ToolDefinition(
            name="read_all_chunks",
            description=(
                "Read the ENTIRE document — every embedded chunk, grouped by page in a "
                "deterministic order. Within-page order is approximate until chunks have a "
                "stored chunk_index. This is the exhaustive full-scan path. Use it (NOT "
                "search_documents) whenever the user wants completeness: 'extract all', "
                "'list every', 'all the X', 'summarize the whole file'. Semantic search caps "
                "results and WILL miss items; this does not. Returns 40 chunks per call — if "
                "the footer says chunks remain, call again with the given `offset` until you "
                "reach END OF DOCUMENT before answering."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File UUID or exact name."},
                    "offset": {"type": "integer", "description": "Chunk offset to start from (0 first call; use the offset the previous call told you)."},
                },
                "required": ["file_id"],
            },
            fn=_t_read_all_chunks,
        ),
        ToolDefinition(
            name="search_web",
            description=(
                "Search the public web. The user controls whether web is on. If it's off, the "
                "tool returns a polite message you should pass to the user."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, in natural language."},
                },
                "required": ["query"],
            },
            fn=_t_search_web,
        ),
        ToolDefinition(
            name="fetch_url",
            description="Fetch and clean a webpage. Use this when the user pastes a URL.",
            params_schema={
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
            fn=_t_fetch_url,
        ),
        ToolDefinition(
            name="recall_memory",
            description=(
                "Semantic recall over long-term conversation memory. Only use when the answer "
                "really needs something said in an earlier session — not for the current chat."
            ),
            params_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            fn=_t_recall_memory,
        ),
        ToolDefinition(
            name="ask_user",
            description=(
                "Ask the user a clarifying question when you genuinely cannot decide WHICH file "
                "they mean or WHICH action they want. Do NOT use for trivial follow-ups."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional button labels (max 4).",
                    },
                },
                "required": ["question"],
            },
            fn=_t_ask_user,
        ),
        ToolDefinition(
            name="make_plan",
            description=(
                "Create a TODO when the user's request needs 2+ separate actions. "
                "Build it AFTER you have enough info (one scouting call). Use update_plan to move items."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ordered, short task lines.",
                    },
                },
                "required": ["items"],
            },
            fn=_t_make_plan,
        ),
        ToolDefinition(
            name="update_plan",
            description=(
                "Update one plan item's status. Use as you work: pending → in_progress → done. "
                "Use 'blocked' if you tried and could not finish that item."
            ),
            params_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "done", "blocked"],
                    },
                },
                "required": ["id", "status"],
            },
            fn=_t_update_plan,
        ),
    ]
    return {d.name: d for d in defs}
