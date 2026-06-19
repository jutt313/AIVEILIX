#!/usr/bin/env python
"""
Backfill: re-apply pipeline-v3 ingestion cleanup (dedup + name reconciliation)
to files that were processed before the fix.

Modes
-----
rederive (default, cheap)
    Load each file's stored layout JSON from R2, re-run dedupe_elements +
    reconcile_names on the already-captured elements, rebuild the layout JSON
    and chunks, re-embed, and replace the Qdrant vectors + Postgres chunk/summary
    rows. NO OCR/visual re-run. Fixes the dedup padding (list_visuals) and the
    rule-based name corrections/flags from the text that's already stored — it
    cannot re-read a pixel the visual model misread (that needs `full`).

full (expensive)
    Re-run the entire pipeline via process_file (re-OCR + re-visual). Use this
    only if you change the OCR/visual model.

Usage
-----
    # See what would change, touch nothing:
    python -m scripts.reprocess_files --mode rederive --dry-run

    # Re-derive one bucket, a few files at a time:
    python -m scripts.reprocess_files --mode rederive --bucket <uuid> --limit 5

    # Re-derive a single file:
    python -m scripts.reprocess_files --mode rederive --file <uuid>

    # Full reprocess (re-OCR) a single file:
    python -m scripts.reprocess_files --mode full --file <uuid>

Run from the backend/ directory. Validate on ONE file before a bulk run.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import uuid

from sqlalchemy import delete, select, update

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.chunk import Chunk
from app.models.file import File
from app.models.summary import Summary
from app.services.processing_v3.chunking import PageMeta, build_chunks, build_export_json
from app.services.processing_v3.dedup import dedupe_elements
from app.services.processing_v3.embedding import embed_texts
from app.services.processing_v3.layout import ElementRecord
from app.services.processing_v3.reconcile import reconcile_names
from app.services.processing_v3.summary import summarise
from app.services.processing_v3.orchestrator import (
    _assign_sort_order,
    _compute_file_manifest,
    _embed_text,
    process_file,
)
from app.services.qdrant.file_indexer import (
    deprecate_file_vectors,
    ensure_collections,
    upsert_text_chunks,
)
from app.services.storage.r2 import build_layout_key, download_file, upload_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("reprocess")


def _elements_from_layout(layout: dict, file_id: str) -> tuple[list[PageMeta], list[ElementRecord]]:
    """Reconstruct PageMeta + ElementRecord objects from a stored layout JSON."""
    pages_meta: list[PageMeta] = []
    elements: list[ElementRecord] = []
    for p in layout.get("pages", []):
        page = int(p.get("page") or 0)
        page_id = p.get("page_id") or f"{file_id}-p{page}"
        pages_meta.append(PageMeta(
            page_number=page,
            width=int(p.get("width") or 0),
            height=int(p.get("height") or 0),
            page_id=page_id,
            screenshot_uri=p.get("screenshot_uri"),
            ocr_status=p.get("ocr_status") or "skipped_native_text",
            raw_ocr_uri=p.get("raw_ocr_uri"),
        ))
        for e in p.get("elements", []):
            elements.append(ElementRecord(
                id=e.get("id") or str(uuid.uuid4()),
                doc_id=file_id,
                page_id=page_id,
                page_number=page,
                type=e.get("type") or "paragraph",
                content=e.get("content") or "",
                bbox=e.get("bbox"),
                source=e.get("source") or "native_text",
                confidence=e.get("confidence"),
                metadata=e.get("metadata") or {},
                sort_order=int(e.get("sort_order") or 0),
            ))
    return pages_meta, elements


def _qdrant_payload(file_id: str, bucket_id, *, point_id, page, content,
                    block_id, is_summary, chunk_index, dense) -> dict:
    return {
        "id": point_id,
        "file_id": file_id,
        "bucket_id": str(bucket_id),
        "page": page,
        "content": content,
        "block_id": block_id,
        "is_summary": is_summary,
        "nearby_image_id": None,
        "image_description": "",
        "image_text_inside": "",
        "chunk_index": chunk_index,
        "dense": dense,
        "sparse": None,
        "status": "active",
    }


async def _rederive_one(db, row, *, dry_run: bool) -> tuple[str, str]:
    fid = row.id
    file_id = str(fid)
    if not row.layout_json_path:
        return ("skip", "no layout_json (legacy) — use --mode full")

    raw = await asyncio.to_thread(download_file, row.layout_json_path)
    layout = json.loads(raw)
    pages_meta, elements = _elements_from_layout(layout, file_id)
    before = len(elements)

    if settings.ingest_dedup_enabled:
        elements, _ = dedupe_elements(elements, threshold=settings.ingest_dedup_threshold)
    name_conflicts: list[dict] = []
    if settings.name_reconcile_enabled:
        elements, name_conflicts = reconcile_names(
            elements,
            min_occurrences=settings.name_canonicalize_min_occurrences,
            canonicalize_ratio=settings.name_canonicalize_ratio,
            variant_min_ratio=settings.name_variant_min_ratio,
        )
    elements = _assign_sort_order(elements)
    after = len(elements)

    if dry_run:
        return ("dry", f"elements {before}->{after} (-{before - after}), conflicts={len(name_conflicts)}")

    doc_meta = {
        "schema_version": layout.get("schema_version", "1.0"),
        "doc_id": file_id,
        "filename": layout.get("filename") or row.name,
        "mime_type": layout.get("mime_type") or "",
        "source_file_uri": layout.get("source_file_uri") or (row.r2_path or ""),
        "page_count": layout.get("page_count") or len(pages_meta),
    }
    export = build_export_json(doc_meta, pages_meta, elements, name_conflicts=name_conflicts)
    layout_key = build_layout_key(file_id)
    await asyncio.to_thread(upload_json, json.dumps(export, ensure_ascii=False), layout_key)
    image_count, section_outline = _compute_file_manifest(elements)

    # Reuse the existing summary text (avoid an LLM call); regenerate only if missing.
    existing = (await db.execute(select(Summary).where(Summary.file_id == fid))).scalars().first()
    summary_text = existing.content if existing else await summarise(doc_meta["filename"], elements)

    chunk_records = build_chunks(elements, pages_meta)
    summary_id = uuid.uuid4()
    texts = [summary_text] + [_embed_text(cr.text, cr.page_start) for cr in chunk_records]
    vectors = await embed_texts(texts)
    if len(vectors) != len(texts):
        return ("error", "embedding count mismatch")
    summary_vector, chunk_vectors = vectors[0], vectors[1:]

    qdrant_docs = [_qdrant_payload(
        file_id, row.bucket_id, point_id=str(summary_id), page=1, content=summary_text,
        block_id="doc_summary", is_summary=True, chunk_index=-1, dense=summary_vector,
    )]
    for idx, (cr, vec) in enumerate(zip(chunk_records, chunk_vectors)):
        qdrant_docs.append(_qdrant_payload(
            file_id, row.bucket_id, point_id=cr.id, page=cr.page_start, content=cr.text,
            block_id=cr.chunk_type, is_summary=False, chunk_index=idx, dense=vec,
        ))

    await ensure_collections()
    await deprecate_file_vectors(file_id)
    await upsert_text_chunks(qdrant_docs)

    await db.execute(delete(Chunk).where(Chunk.file_id == fid))
    await db.execute(delete(Summary).where(Summary.file_id == fid))
    db.add(Summary(id=summary_id, file_id=fid, content=summary_text))
    for cr in chunk_records:
        db.add(Chunk(
            id=uuid.UUID(cr.id), file_id=fid, bucket_id=row.bucket_id, page=cr.page_start,
            content=cr.text, block_id=cr.chunk_type, nearby_image_id=None,
            token_count=max(1, len(cr.text) // 4), status="embedded", retry_count=0,
        ))
    await db.execute(update(File).where(File.id == fid).values(
        layout_json_path=layout_key, image_count=image_count, section_outline=section_outline,
    ))
    await db.commit()
    return ("ok", f"elements {before}->{after} (-{before - after}), "
                  f"chunks={len(chunk_records)}, conflicts={len(name_conflicts)}")


async def _full_one(row) -> tuple[str, str]:
    # process_file skips files whose status is already 'ready' — flip it first.
    async with AsyncSessionLocal() as db:
        await db.execute(update(File).where(File.id == row.id).values(status="processing"))
        await db.commit()
    await process_file(str(row.id), str(uuid.uuid4()), "reprocess")
    return ("ok", "full reprocess complete")


async def main(args: argparse.Namespace) -> None:
    cols = (File.id, File.name, File.bucket_id, File.r2_path, File.layout_json_path)
    async with AsyncSessionLocal() as db:
        if args.file:
            q = select(*cols).where(File.id == uuid.UUID(args.file))
        else:
            q = select(*cols).where(File.status == args.status)
            if args.bucket:
                q = q.where(File.bucket_id == uuid.UUID(args.bucket))
            if args.limit:
                q = q.limit(args.limit)
        rows = (await db.execute(q)).all()

    logger.info("mode=%s files=%s dry_run=%s", args.mode, len(rows), args.dry_run)
    ok = skipped = errored = 0
    for row in rows:
        try:
            if args.mode == "rederive":
                async with AsyncSessionLocal() as db:
                    try:
                        status, msg = await _rederive_one(db, row, dry_run=args.dry_run)
                    except Exception:
                        await db.rollback()
                        raise
            else:
                if args.dry_run:
                    status, msg = ("dry", "would full-reprocess (re-OCR)")
                else:
                    status, msg = await _full_one(row)
        except Exception as exc:  # noqa: BLE001 — keep the batch going
            status, msg = ("error", repr(exc))

        ok += status in ("ok", "dry")
        skipped += status == "skip"
        errored += status == "error"
        logger.info("[%s] %s — %s", status.upper(), row.name, msg)
        if args.sleep:
            await asyncio.sleep(args.sleep)

    logger.info("done: ok/dry=%s skipped=%s errored=%s", ok, skipped, errored)


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Re-apply ingestion cleanup to existing files.")
    p.add_argument("--mode", choices=["rederive", "full"], default="rederive")
    p.add_argument("--bucket", help="restrict to one bucket UUID")
    p.add_argument("--file", help="process a single file UUID")
    p.add_argument("--status", default="ready", help="file status to select (default: ready)")
    p.add_argument("--limit", type=int, default=0, help="max files (0 = all)")
    p.add_argument("--sleep", type=float, default=0.0, help="seconds to wait between files")
    p.add_argument("--dry-run", action="store_true", help="report changes, write nothing")
    return p.parse_args()


if __name__ == "__main__":
    asyncio.run(main(_parse()))
