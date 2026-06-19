"""
Pipeline v3 orchestrator.

Runs the ported document-processing chain as a FastAPI background task and
writes its output into the main backend's existing schema:

    files.status / files.layout_json_path / files.page_count
    chunks rows
    summaries row
    Qdrant text_chunks collection (dense-only Voyage vectors)

Replaces app/services/pipeline_v2/orchestrator.py. The agent / MCP retrieval
read these same tables and collection unchanged.

Stages:
    cleanup        → deprecate old vectors + delete old chunk/summary rows
    download       → raw bytes from R2
    render         → page screenshots (PyMuPDF / Pillow)
    native_text    → selectable PDF text
    mistral_ocr    → OCR for weak/scanned/image pages
    layout         → text ElementRecords
    visual         → cropped + Kimi-described visual ElementRecords
    summary        → Gemini document summary
    layout_upload  → export JSON to R2 (files.layout_json_path)
    chunking       → section-aware chunks
    voyage_embed   → dense text embeddings
    qdrant_upsert  → write text vectors
    persist        → chunks + summary rows
    finalize       → files.status = ready + user notification

An advisory lock prevents duplicate concurrent runs for the same file.
"""

import asyncio
import json
import logging
import traceback
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter

from sqlalchemy import delete, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.chunk import Chunk
from app.models.error_log import ErrorLog
from app.models.file import File
from app.models.investigation_event import InvestigationEvent
from app.models.summary import Summary
from app.services.notifications import create_notification
from app.services.outline import clean_section_outline
from app.services.storage.r2 import download_file, upload_json, build_layout_key
from app.services.qdrant.file_indexer import (
    deprecate_file_vectors,
    ensure_collections,
    upsert_text_chunks,
)

from app.services.processing_v3.normalize import detect_file_type, FileType, preprocess_text_bytes
from app.services.processing_v3.render import render_pages, RenderedPage
from app.services.processing_v3.native_text import extract_native_text, is_page_text_weak
from app.services.processing_v3.layout import build_elements, ElementRecord
from app.services.processing_v3.visual_elements import (
    VISUAL_CONCURRENCY,
    extract_pdf_chart_regions,
    extract_pdf_image_regions,
    extract_visual_elements,
)
from app.services.processing_v3.chunking import PageMeta, build_chunks, build_export_json
from app.services.processing_v3.summary import summarise
from app.services.processing_v3.storage import get_storage_adapter
from app.services.processing_v3.ocr import get_ocr_provider
from app.services.processing_v3.visual import get_visual_understanding_provider
from app.services.processing_v3.embedding import embed_texts
from app.services.processing_v3.dedup import dedupe_elements
from app.services.processing_v3.reconcile import reconcile_names
from app.config import settings

logger = logging.getLogger(__name__)


class PipelineStageError(RuntimeError):
    def __init__(self, stage: str, message: str):
        self.stage = stage
        super().__init__(f"pipeline_v3:{stage}: {message}")


@dataclass
class TraceContext:
    file_id: uuid.UUID
    trace_run_id: str
    trigger_source: str
    sequence: int = 0


# ── public entry point ────────────────────────────────────────────────────────

async def process_file(
    file_id: str,
    trace_run_id: str | None = None,
    trigger_source: str = "background_task",
) -> None:
    """Entry point called by FastAPI background tasks. Opens its own DB session."""
    trace = TraceContext(
        file_id=uuid.UUID(file_id),
        trace_run_id=trace_run_id or str(uuid.uuid4()),
        trigger_source=trigger_source,
    )
    await _trace(trace, "pipeline_v3_run_started", "started", "pipeline_run")

    async with AsyncSessionLocal() as db:
        if not await _try_acquire_file_lock(db, file_id):
            logger.info("[v3] Skipping duplicate run for file %s", file_id)
            await _trace(trace, "pipeline_v3_run_skipped", "failed", "pipeline_run",
                         {"reason": "duplicate_lock"})
            return
        try:
            await _run_pipeline(db, file_id, trace)
            await _trace(trace, "pipeline_v3_run_completed", "completed", "pipeline_run")
        except Exception as exc:
            logger.error("[v3] Pipeline failed for file %s: %s", file_id, exc)
            await db.rollback()
            failed_stage = exc.stage if isinstance(exc, PipelineStageError) else "unknown"
            async with AsyncSessionLocal() as fail_db:
                await _mark_failed(fail_db, file_id, str(exc), traceback.format_exc(),
                                   stage=failed_stage, trace=trace)
        finally:
            await _release_file_lock(db, file_id)


# ── pipeline body ─────────────────────────────────────────────────────────────

async def _run_pipeline(db: AsyncSession, file_id: str, trace: TraceContext) -> None:
    fid = uuid.UUID(file_id)

    row = await db.get(File, fid)
    if row is None:
        raise ValueError(f"[v3] File {file_id} not found")
    if row.status == "ready":
        logger.info("[v3] File %s already ready — skipping", file_id)
        return

    await db.execute(update(File).where(File.id == fid).values(status="processing"))
    await db.flush()

    bucket_id = row.bucket_id
    filename = row.name

    # 1. Cleanup previous processing state
    started = perf_counter()
    try:
        await deprecate_file_vectors(file_id)
        await db.execute(delete(Chunk).where(Chunk.file_id == fid))
        await db.execute(delete(Summary).where(Summary.file_id == fid))
        await db.flush()
    except Exception as exc:
        raise PipelineStageError("cleanup", str(exc)) from exc
    await _trace(trace, "cleanup_completed", "completed", "cleanup",
                 {"duration_ms": _ms(started)})

    # 2. Download raw bytes
    started = perf_counter()
    try:
        file_bytes = await asyncio.to_thread(download_file, row.r2_path)
    except Exception as exc:
        raise PipelineStageError("download", str(exc)) from exc
    await _trace(trace, "download_completed", "completed", "download",
                 {"bytes": len(file_bytes), "duration_ms": _ms(started)})

    # 3. Detect type + render pages
    started = perf_counter()
    try:
        file_type = detect_file_type("application/octet-stream", filename, file_bytes)
        if file_type == FileType.TEXT:
            file_bytes = preprocess_text_bytes(file_bytes, filename)
            rendered: list[RenderedPage] = [RenderedPage(page_number=1, width=0, height=0, data=b"")]
        else:
            rendered = await asyncio.to_thread(render_pages, file_type, file_bytes)
    except Exception as exc:
        raise PipelineStageError("render", str(exc)) from exc
    if not rendered:
        raise PipelineStageError("render", "document produced no pages")
    await _trace(trace, "render_completed", "completed", "render",
                 {"pages": len(rendered), "file_type": file_type.value, "duration_ms": _ms(started)})

    # 3b. Enforce the owner's monthly page quota before the expensive OCR/visual stages.
    from app.services.quota import page_quota_status
    within, used_pages, max_pages, plan_name = await page_quota_status(
        db, row.user_id, adding_pages=len(rendered), exclude_file_id=fid
    )
    if not within:
        raise PipelineStageError(
            "page_limit",
            f"{plan_name} plan page limit reached ({used_pages}/{max_pages} pages); "
            f"this file adds {len(rendered)}. Upgrade or remove files.",
        )

    # 4. Native text
    started = perf_counter()
    try:
        native_blocks = await asyncio.to_thread(extract_native_text, file_type, file_bytes)
    except Exception as exc:
        raise PipelineStageError("native_text", str(exc)) from exc
    await _trace(trace, "native_text_completed", "completed", "native_text",
                 {"blocks": len(native_blocks), "duration_ms": _ms(started)})

    # 5. OCR weak pages + upload screenshots
    storage = get_storage_adapter()
    ocr_provider = get_ocr_provider()
    page_ids: dict[int, str] = {}
    page_ocr_status: dict[int, str] = {}
    ocr_results: dict = {}
    pages_meta: list[PageMeta] = []

    started = perf_counter()
    for rp in rendered:
        page_id = str(uuid.uuid4())
        page_ids[rp.page_number] = page_id
        if file_type == FileType.TEXT:
            page_ocr_status[rp.page_number] = "skipped"
            screenshot_uri = None
            raw_ocr_uri = None
            ocr_status_label = "skipped_text"
        else:
            try:
                screenshot_uri = await storage.upload_page_screenshot(rp.data, file_id, rp.page_number)
            except Exception as exc:
                raise PipelineStageError("render", f"screenshot upload failed: {exc}") from exc

            if is_page_text_weak(native_blocks, rp.page_number):
                if ocr_provider is None:
                    raise PipelineStageError(
                        "mistral_ocr",
                        f"page {rp.page_number} needs OCR but MISTRAL_API_KEY is not set",
                    )
                try:
                    ocr = await ocr_provider.run(rp.data, rp.page_number)
                except Exception as exc:
                    raise PipelineStageError("mistral_ocr", str(exc)) from exc
                ocr_results[rp.page_number] = ocr
                page_ocr_status[rp.page_number] = "done"
                raw_ocr_uri = None
                try:
                    raw_ocr_uri = await storage.upload_ocr_json(
                        json.dumps(ocr.raw_response).encode(), file_id, rp.page_number,
                    )
                except Exception as exc:
                    logger.warning("[v3] OCR JSON upload failed page=%s: %s", rp.page_number, exc)
                ocr_status_label = "done"
            else:
                page_ocr_status[rp.page_number] = "skipped"
                raw_ocr_uri = None
                ocr_status_label = "skipped_native_text"

        pages_meta.append(PageMeta(
            page_number=rp.page_number,
            width=rp.width,
            height=rp.height,
            page_id=page_id,
            screenshot_uri=screenshot_uri,
            ocr_status=ocr_status_label,
            raw_ocr_uri=raw_ocr_uri,
        ))
    await _trace(trace, "mistral_ocr_completed", "completed", "mistral_ocr",
                 {"ocr_pages": len(ocr_results), "duration_ms": _ms(started)})

    # 6. Layout elements
    started = perf_counter()
    try:
        text_elements = build_elements(file_id, native_blocks, ocr_results, page_ocr_status, page_ids)
    except Exception as exc:
        raise PipelineStageError("layout", str(exc)) from exc
    await _trace(trace, "layout_completed", "completed", "layout",
                 {"text_elements": len(text_elements), "duration_ms": _ms(started)})

    # 7. Visual elements
    started = perf_counter()
    visual_elements: list[ElementRecord] = []
    visual_provider = get_visual_understanding_provider()
    if file_type == FileType.TEXT:
        logger.info("[v3] text file — visual element extraction skipped")
    elif visual_provider is not None:
        try:
            visual_elements = await _extract_visuals(
                file_id, file_type, file_bytes, rendered, text_elements,
                page_ids, storage, visual_provider,
            )
        except Exception as exc:
            logger.warning("[v3] visual extraction failed (non-fatal): %s", exc)
    else:
        logger.info("[v3] KIMI_API_KEY not set — visual element extraction skipped")
    await _trace(trace, "visual_completed", "completed", "visual",
                 {"visual_elements": len(visual_elements), "duration_ms": _ms(started)})

    elements = _assign_sort_order(text_elements + visual_elements)

    # 7b. Ingestion cleanup — dedup + name reconciliation. Runs on the RAW merged
    #     elements BEFORE summary/export/chunk so the stored layout JSON (which
    #     list_visuals serves), the summary, and the chunks are all built from the
    #     cleaned, reconciled set. The summary is never used as the source of
    #     truth for names (it is generated from this cleaned input, not vice versa).
    name_conflicts: list[dict] = []
    if settings.ingest_dedup_enabled:
        started = perf_counter()
        before = len(elements)
        elements, dedup_report = dedupe_elements(
            elements, threshold=settings.ingest_dedup_threshold
        )
        elements = _assign_sort_order(elements)
        await _trace(trace, "dedup_completed", "completed", "dedup",
                     {"removed": before - len(elements), "collapsed": len(dedup_report),
                      "duration_ms": _ms(started)})
    if settings.name_reconcile_enabled:
        started = perf_counter()
        elements, name_conflicts = reconcile_names(
            elements,
            min_occurrences=settings.name_canonicalize_min_occurrences,
            canonicalize_ratio=settings.name_canonicalize_ratio,
            variant_min_ratio=settings.name_variant_min_ratio,
        )
        await _trace(trace, "reconcile_completed", "completed", "reconcile",
                     {"conflicts": len(name_conflicts), "duration_ms": _ms(started)})

    # 8. Summary
    started = perf_counter()
    summary_text = await summarise(filename, elements)
    await _trace(trace, "summary_completed", "completed", "summary",
                 {"chars": len(summary_text), "duration_ms": _ms(started)})

    # 9. Export JSON → R2
    started = perf_counter()
    doc_meta = {
        "schema_version": "1.0",
        "doc_id": file_id,
        "filename": filename,
        "mime_type": file_type.value,
        "source_file_uri": row.r2_path,
        "page_count": len(rendered),
    }
    export = build_export_json(doc_meta, pages_meta, elements, name_conflicts=name_conflicts)
    layout_key = build_layout_key(file_id)
    try:
        await asyncio.to_thread(upload_json, json.dumps(export, ensure_ascii=False), layout_key)
    except Exception as exc:
        raise PipelineStageError("layout_upload", str(exc)) from exc
    image_count, section_outline = _compute_file_manifest(elements)

    # Enforce the owner's visual (image) quota now that the count is known.
    from app.services.quota import image_quota_status
    within_img, used_img, max_img, plan_nm = await image_quota_status(
        db, row.user_id, adding_images=image_count, exclude_file_id=fid
    )
    if not within_img:
        raise PipelineStageError(
            "image_limit",
            f"{plan_nm} plan visual limit reached ({used_img}/{max_img} images); "
            f"this file adds {image_count}. Upgrade or remove files.",
        )

    await db.execute(
        update(File).where(File.id == fid).values(
            layout_json_path=layout_key,
            page_count=len(rendered),
            image_count=image_count,
            section_outline=section_outline,
        )
    )
    await db.flush()
    await _trace(trace, "layout_upload_completed", "completed", "layout_upload",
                 {"r2_key": layout_key, "duration_ms": _ms(started)})

    # 10. Chunking
    chunk_records = build_chunks(elements, pages_meta)
    await _trace(trace, "chunking_completed", "completed", "chunking",
                 {"chunks": len(chunk_records)})

    # 11. Embed (summary first, then chunks)
    started = perf_counter()
    summary_id = uuid.uuid4()
    texts_to_embed = [summary_text] + [_embed_text(cr.text, cr.page_start) for cr in chunk_records]
    try:
        vectors = await embed_texts(texts_to_embed)
    except Exception as exc:
        raise PipelineStageError("voyage_embed", str(exc)) from exc
    if len(vectors) != len(texts_to_embed):
        raise PipelineStageError("voyage_embed", "embedding count mismatch")
    summary_vector = vectors[0]
    chunk_vectors = vectors[1:]
    await _trace(trace, "voyage_embed_completed", "completed", "voyage_embed",
                 {"embedded": len(vectors), "duration_ms": _ms(started)})

    # 12. Qdrant upsert
    started = perf_counter()
    qdrant_docs: list[dict] = [{
        "id": str(summary_id),
        "file_id": file_id,
        "bucket_id": str(bucket_id),
        "page": 1,
        "content": summary_text,
        "block_id": "doc_summary",
        "is_summary": True,
        "nearby_image_id": None,
        "image_description": "",
        "image_text_inside": "",
        "chunk_index": -1,
        "dense": summary_vector,
        "sparse": None,
        "status": "active",
    }]
    for idx, (cr, vec) in enumerate(zip(chunk_records, chunk_vectors)):
        qdrant_docs.append({
            "id": cr.id,
            "file_id": file_id,
            "bucket_id": str(bucket_id),
            "page": cr.page_start,
            "content": cr.text,
            "block_id": cr.chunk_type,
            "is_summary": False,
            "nearby_image_id": None,
            "image_description": "",
            "image_text_inside": "",
            "chunk_index": idx,
            "dense": vec,
            "sparse": None,
            "status": "active",
        })
    try:
        await ensure_collections()
        await upsert_text_chunks(qdrant_docs)
    except Exception as exc:
        raise PipelineStageError("qdrant_upsert", str(exc)) from exc
    await _trace(trace, "qdrant_upsert_completed", "completed", "qdrant_upsert",
                 {"points": len(qdrant_docs), "duration_ms": _ms(started)})

    # 13. Persist chunk + summary rows
    try:
        # summaries has a CHECK constraint requiring exactly one target — file_id only.
        db.add(Summary(id=summary_id, file_id=fid, content=summary_text))
        for cr in chunk_records:
            db.add(Chunk(
                id=uuid.UUID(cr.id),
                file_id=fid,
                bucket_id=bucket_id,
                page=cr.page_start,
                content=cr.text,
                block_id=cr.chunk_type,
                nearby_image_id=None,
                token_count=max(1, len(cr.text) // 4),
                status="embedded",
                retry_count=0,
            ))
        await db.flush()
    except Exception as exc:
        raise PipelineStageError("persist", str(exc)) from exc

    # 14. Finalize
    await db.execute(update(File).where(File.id == fid).values(status="ready"))
    await create_notification(
        db, str(row.user_id), "success",
        "File processing completed",
        f'"{filename}" finished processing and is ready to use.',
    )
    await _trace(trace, "file_ready", "completed", "finalize", {"status": "ready"})
    await db.commit()
    logger.info("[v3] Pipeline complete for file %s — status=ready", file_id)

# ── visual extraction helper ──────────────────────────────────────────────────

async def _extract_visuals(
    file_id: str,
    file_type: FileType,
    file_bytes: bytes,
    rendered: list[RenderedPage],
    text_elements: list[ElementRecord],
    page_ids: dict[int, str],
    storage,
    visual_provider,
) -> list[ElementRecord]:
    semaphore = asyncio.Semaphore(VISUAL_CONCURRENCY)

    async def _page_visuals(rp: RenderedPage) -> list[ElementRecord]:
        page_text = [e for e in text_elements if e.page_number == rp.page_number]
        text_bboxes = [e.bbox for e in page_text if e.bbox]

        pdf_image_regions = None
        if file_type == FileType.PDF:
            try:
                pdf_image_regions = await asyncio.to_thread(
                    extract_pdf_image_regions, file_bytes, rp.page_number
                )
                charts = await asyncio.to_thread(
                    extract_pdf_chart_regions, file_bytes, rp.page_number
                )
                if charts:
                    pdf_image_regions = (pdf_image_regions or []) + charts
            except Exception as exc:
                logger.warning("[v3] PDF image-block detect failed page=%s: %s", rp.page_number, exc)

        return await extract_visual_elements(
            doc_id=file_id,
            page_id=page_ids[rp.page_number],
            page_number=rp.page_number,
            screenshot_data=rp.data,
            storage=storage,
            visual_provider=visual_provider,
            sort_order_start=len(page_text),
            text_bboxes=text_bboxes or None,
            pdf_image_regions=pdf_image_regions,
            semaphore=semaphore,
        )

    page_results = await asyncio.gather(*(_page_visuals(rp) for rp in rendered))
    out: list[ElementRecord] = []
    for pr in page_results:
        out.extend(pr)
    return out


def _assign_sort_order(elements: list[ElementRecord]) -> list[ElementRecord]:
    """Re-number sort_order per page, interleaving text and visual by y-position."""
    by_page: dict[int, list[ElementRecord]] = {}
    for elem in elements:
        by_page.setdefault(elem.page_number, []).append(elem)

    result: list[ElementRecord] = []
    for page_num in sorted(by_page):
        page_elems = by_page[page_num]

        def _key(item: tuple[int, ElementRecord]) -> tuple[int, float, int]:
            idx, e = item
            if e.bbox:
                return (0, e.bbox[1], idx)
            return (1, 0.0, idx)

        sorted_elems = [e for _, e in sorted(enumerate(page_elems), key=_key)]
        for j, elem in enumerate(sorted_elems):
            elem.sort_order = j
            result.append(elem)
    return result


def _embed_text(content: str, page: int) -> str:
    """Prepend a [Page N] prefix so the vector encodes structural position."""
    return f"[Page {page}] {content.strip()}"


def _ms(started: float) -> int:
    return int((perf_counter() - started) * 1000)


# Visual elements with these types don't count as "images" the user would
# expect on a page (text crops, button captures). Everything else does.
_NON_VISUAL_TYPES = {"text"}


def _compute_file_manifest(
    elements: list[ElementRecord],
) -> tuple[int, list[dict]]:
    """
    Returns (image_count, section_outline).

      image_count    — distinct visual assets the user would see (excludes
                       text crops emitted by the visual provider).
      section_outline — ordered list of {heading, page} for every layout
                       heading in document order. Powers structural queries
                       without going through the vector store.
    """
    image_count = 0
    raw_outline: list[dict] = []
    for elem in elements:
        if elem.source == "visual_understanding":
            if elem.type not in _NON_VISUAL_TYPES:
                image_count += 1
        elif elem.type == "heading":
            text = (elem.content or "").strip()
            if text:
                raw_outline.append({"heading": text, "page": elem.page_number})
    # Strip prose fragments / duplicate CTAs and attach index + level so the
    # stored outline is clean and structured (see app.services.outline).
    outline = clean_section_outline(raw_outline)
    return image_count, outline


# ── failure handler ───────────────────────────────────────────────────────────

async def _mark_failed(
    db: AsyncSession,
    file_id: str,
    error_msg: str,
    stack: str,
    stage: str,
    trace: TraceContext,
) -> None:
    fid = uuid.UUID(file_id)
    try:
        row = await db.get(File, fid)
        user_id = row.user_id if row else None
        file_name = row.name if row else f"file {file_id}"

        cleanup_error = None
        try:
            await deprecate_file_vectors(file_id)
        except Exception as exc:
            cleanup_error = str(exc)

        await db.execute(update(Chunk).where(Chunk.file_id == fid).values(status="failed"))
        await db.execute(update(File).where(File.id == fid).values(status="failed"))

        if user_id:
            await create_notification(
                db, str(user_id), "error",
                "File processing failed",
                f'"{file_name}" failed during {stage}. {error_msg[:220]}',
            )
        await db.commit()

        await _trace(trace, "pipeline_v3_failed", "failed", stage,
                     {"error": error_msg[:1000], "cleanup_error": cleanup_error})

        async with AsyncSessionLocal() as err_db:
            err_db.add(ErrorLog(
                user_id=user_id,
                file_id=fid,
                service=f"pipeline_v3:{stage}",
                error_message=error_msg[:2000],
                stack_trace=stack[:5000],
                resolved=False,
            ))
            await err_db.commit()

        logger.info("[v3] Marked file %s as failed (stage=%s)", file_id, stage)
    except Exception as inner:
        logger.error("[v3] Could not mark file %s as failed: %s", file_id, inner)


# ── tracing ───────────────────────────────────────────────────────────────────

async def _trace(
    trace: TraceContext,
    event: str,
    status: str,
    stage: str,
    metadata: dict | None = None,
) -> None:
    trace.sequence += 1
    full_meta = {
        "trace_run_id": trace.trace_run_id,
        "trigger_source": trace.trigger_source,
        "stage": stage,
        "sequence": trace.sequence,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "v3",
        **(metadata or {}),
    }
    try:
        async with AsyncSessionLocal() as tdb:
            tdb.add(InvestigationEvent(
                file_id=trace.file_id,
                event=event,
                status=status,
                event_metadata=full_meta,
            ))
            await tdb.commit()
    except Exception as exc:
        logger.warning("[v3] Could not persist trace event %s: %s", event, exc)
    (logger.error if status == "failed" else logger.info)(
        "[v3] trace file=%s event=%s stage=%s status=%s", trace.file_id, event, stage, status,
    )


# ── advisory lock ─────────────────────────────────────────────────────────────

def _lock_key(file_id: str) -> int:
    raw = int.from_bytes(uuid.UUID(file_id).bytes[:8], byteorder="big", signed=False)
    return raw - 2**64 if raw >= 2**63 else raw


async def _try_acquire_file_lock(db: AsyncSession, file_id: str) -> bool:
    result = await db.execute(
        text("SELECT pg_try_advisory_lock(:key) AS acquired"),
        {"key": _lock_key(file_id)},
    )
    return bool(result.scalar())


async def _release_file_lock(db: AsyncSession, file_id: str) -> None:
    try:
        await db.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": _lock_key(file_id)})
    except Exception:
        logger.warning("[v3] Could not release advisory lock for file %s", file_id)
