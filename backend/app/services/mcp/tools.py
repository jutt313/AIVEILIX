"""
MCP service layer — file-centric data access functions for MCP tools.

Functions:
  fetch_file_spread     — full file: metadata + summary + chunks + images (by page)
  fetch_page_blocks     — chunks + images for one specific page (with block layout)
  fetch_file_layout     — full layout map across all pages of a file
  fetch_bucket_info     — bucket name, description, storage stats, file count
  fetch_bucket_members  — owner + team members with access, plus their permissions
  fetch_files_list      — all files in bucket with metadata
  fetch_file_summary    — AI-generated summary for a specific file
  fetch_categories      — all categories in the bucket with file counts
  fetch_chunk           — a single chunk with nearby-image metadata
  fetch_chunks_list     — all chunks for a specific file
"""

from __future__ import annotations

import logging
import re
import uuid

from qdrant_client.models import FieldCondition, Filter, MatchValue, Range
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bucket import Bucket, Category
from app.models.chunk import Chunk
from app.models.file import File
from app.models.platform import TeamBucketAccess, TeamMember
from app.models.summary import Summary
from app.models.user import Profile, User
from app.qdrant_client import get_async_qdrant_client
from app.services.outline import clean_section_outline, outline_to_markdown
from app.services.qdrant.file_indexer import IMAGE_COLLECTION, TEXT_COLLECTION

logger = logging.getLogger(__name__)


# ── fetch_files_list ──────────────────────────────────────────────────────────

async def fetch_files_list(db: AsyncSession, bucket_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(File)
        .where(File.bucket_id == bucket_id, File.status == "ready")
        .order_by(File.created_at.desc())
    )
    files = result.scalars().all()
    return [
        {
            "file_id": str(f.id),
            "name": f.name,
            "type": f.type,
            "size": f.size,
            "page_count": f.page_count,
            "image_count": f.image_count,
            "status": f.status,
            "is_agent_written": f.is_agent_written,
            "created_at": f.created_at.isoformat(),
        }
        for f in files
    ]


# ── fetch_file_stats ──────────────────────────────────────────────────────────

async def fetch_file_stats(
    db: AsyncSession, bucket_id: uuid.UUID, file_id: uuid.UUID
) -> dict | None:
    """
    Returns the asset manifest for a file: page_count, image_count, and the
    section outline. Authoritative source for structural questions ("how many
    images?", "what sections are in this doc?", "what page is X on?").
    """
    result = await db.execute(
        select(
            File.id, File.name, File.page_count, File.image_count, File.section_outline
        ).where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = result.one_or_none()
    if row is None:
        return None
    # Clean at serve time too, so files ingested before the cleaner shipped
    # still return a tidy, structured outline (idempotent on already-clean data).
    outline = clean_section_outline(row.section_outline or [])
    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "page_count": row.page_count,
        "image_count": row.image_count,
        "image_count_note": (
            "image_count = rendered images/figures only. The visual stage also "
            "reads text regions; call list_visuals for total_visuals "
            "(= image_count + text_block_count)."
        ),
        "section_count": len(outline),
        "section_outline": outline,
        "outline_markdown": outline_to_markdown(outline),
    }


# ── fetch_file_spread ─────────────────────────────────────────────────────────

async def fetch_file_spread(db: AsyncSession, bucket_id: uuid.UUID, file_id: uuid.UUID) -> dict | None:
    """
    Returns full file data: metadata + summary + all chunks grouped by page
    + all images grouped by page. File must belong to bucket and be ready.
    """
    file_result = await db.execute(
        select(File).where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    file = file_result.scalar_one_or_none()
    if file is None:
        return None

    # Summary
    summary_result = await db.execute(
        select(Summary.content)
        .where(Summary.file_id == file_id)
        .order_by(Summary.created_at.desc())
        .limit(1)
    )
    summary = summary_result.scalar_one_or_none() or ""

    # Chunks from Postgres grouped by page
    chunks_result = await db.execute(
        select(Chunk)
        .where(Chunk.file_id == file_id, Chunk.status == "embedded")
        .order_by(Chunk.page.asc(), Chunk.chunk_index.asc() if hasattr(Chunk, "chunk_index") else Chunk.id)
    )
    chunks = chunks_result.scalars().all()

    chunks_by_page: dict[int, list[dict]] = {}
    for chunk in chunks:
        page = chunk.page
        if page not in chunks_by_page:
            chunks_by_page[page] = []
        chunks_by_page[page].append({
            "chunk_id": str(chunk.id),
            "block_id": chunk.block_id,
            "content": chunk.content,
            "token_count": chunk.token_count,
            "nearby_image_id": chunk.nearby_image_id,
        })

    images_by_page = await _fetch_images_for_file_unified(db, file_id)
    returned_images = sum(len(v) for v in images_by_page.values())

    return {
        "file_id": str(file.id),
        "name": file.name,
        "type": file.type,
        "size": file.size,
        "page_count": file.page_count,
        "image_count": file.image_count,
        "status": file.status,
        "is_agent_written": file.is_agent_written,
        "created_at": file.created_at.isoformat(),
        "summary": summary,
        "chunks_by_page": {str(k): v for k, v in chunks_by_page.items()},
        "images_by_page": {str(k): v for k, v in images_by_page.items()},
        "total_chunks": len(chunks),
        "total_images": file.image_count,
        "returned_images": returned_images,
    }


# ── fetch_page_blocks ─────────────────────────────────────────────────────────

async def fetch_page_blocks(db: AsyncSession, bucket_id: uuid.UUID, file_id: uuid.UUID, page: int) -> dict | None:
    """
    Returns all text chunks + images for a specific page of a file.
    Gives the agent a structural view of one page including block positions context.
    """
    file_result = await db.execute(
        select(File.id, File.name, File.page_count)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = file_result.one_or_none()
    if row is None:
        return None

    # Text chunks for this page
    chunks_result = await db.execute(
        select(Chunk)
        .where(Chunk.file_id == file_id, Chunk.page == page, Chunk.status == "embedded")
        .order_by(Chunk.id)
    )
    chunks = chunks_result.scalars().all()

    images_by_page = await _fetch_images_for_file_unified(db, file_id, page_filter=page)

    return {
        "file_id": str(file_id),
        "file_name": row.name,
        "page": page,
        "total_pages": row.page_count,
        "blocks": [
            {
                "type": "text",
                "chunk_id": str(chunk.id),
                "block_id": chunk.block_id,
                "content": chunk.content,
                "token_count": chunk.token_count,
                "nearby_image_id": chunk.nearby_image_id,
            }
            for chunk in chunks
        ],
        "images": images_by_page.get(page, []),
    }


# ── fetch_bucket_info ─────────────────────────────────────────────────────────

async def fetch_bucket_info(db: AsyncSession, bucket_id: uuid.UUID) -> dict | None:
    bucket_result = await db.execute(select(Bucket).where(Bucket.id == bucket_id))
    bucket = bucket_result.scalar_one_or_none()
    if bucket is None:
        return None

    files_count_result = await db.execute(
        select(func.count()).where(File.bucket_id == bucket_id, File.status == "ready")
    )
    files_count = files_count_result.scalar_one()

    storage_result = await db.execute(
        select(func.coalesce(func.sum(File.size), 0)).where(File.bucket_id == bucket_id, File.status == "ready")
    )
    storage_used = storage_result.scalar_one()

    return {
        "bucket_id": str(bucket.id),
        "name": bucket.name,
        "description": bucket.description or "",
        "color": bucket.color,
        "files_count": files_count,
        "storage_used": storage_used,
        "created_at": bucket.created_at.isoformat(),
    }


# ── fetch_bucket_members ──────────────────────────────────────────────────────

async def fetch_bucket_members(db: AsyncSession, bucket_id: uuid.UUID) -> dict | None:
    """Who can access this bucket: the workspace owner plus every accepted team
    member granted access, each with their permissions. Names + permissions
    only — no emails, so this is safe to expose to external MCP clients too."""
    bucket_result = await db.execute(select(Bucket).where(Bucket.id == bucket_id))
    bucket = bucket_result.scalar_one_or_none()
    if bucket is None:
        return None

    # Owner — the bucket's user. Prefer their profile name, fall back to email.
    owner_row = await db.execute(
        select(User.email, Profile.full_name)
        .outerjoin(Profile, Profile.user_id == User.id)
        .where(User.id == bucket.user_id)
    )
    owner = owner_row.first()
    owner_name = (
        (owner.full_name if owner and owner.full_name else None)
        or (owner.email if owner else None)
        or "Owner"
    )

    # Team members with an access grant on this bucket (accepted invites only).
    rows = await db.execute(
        select(TeamMember, TeamBucketAccess)
        .join(TeamBucketAccess, TeamBucketAccess.team_member_id == TeamMember.id)
        .where(
            TeamBucketAccess.bucket_id == bucket_id,
            TeamMember.status == "accepted",
        )
        .order_by(TeamMember.display_name)
    )
    members: list[dict] = []
    for tm, access in rows.all():
        members.append({
            "team_member_id": str(tm.id),
            "name": tm.display_name or "(unnamed member)",
            "role": tm.role,
            "permissions": {
                "can_upload_files": access.can_upload_files,
                "can_download_files": access.can_download_files,
                "can_delete_files": access.can_delete_files,
                "can_use_mcp": access.can_use_mcp,
                "can_see_other_members": access.can_see_other_members,
            },
        })

    return {
        "bucket_id": str(bucket.id),
        "bucket_name": bucket.name,
        "owner": {"name": owner_name, "is_owner": True},
        "members": members,
        "member_count": len(members),
        "total_people": len(members) + 1,  # owner + members with access
    }


# ── internal: image fetch (layout JSON, Qdrant fallback) ─────────────────────

def _visual_as_image_entry(visual: dict, *, include_page: bool = False) -> dict:
    entry = {
        "image_id": str(visual.get("element_id") or ""),
        "description": visual.get("description") or "",
        "text_inside": visual.get("text_inside") or "",
        "type": visual.get("type"),
        "asset_type": visual.get("asset_type"),
        "index": visual.get("index"),
        "asset_uri": visual.get("asset_uri"),
        "bbox": visual.get("bbox"),
        "confidence": visual.get("confidence"),
    }
    # Ingestion-cleanup / audit fields — passed through only when present so
    # get_file/get_pages/get_section match list_visuals/get_visual.
    if visual.get("dup_count"):
        entry["dup_count"] = visual["dup_count"]
    if visual.get("duplicate_snapshots"):
        entry["duplicate_snapshots"] = visual["duplicate_snapshots"]
    if visual.get("name_conflict"):
        entry["name_conflict"] = visual["name_conflict"]
    if include_page:
        entry["page"] = visual["page"]
    return entry


def _group_visuals_by_page(visuals: list[dict]) -> dict[int, list[dict]]:
    images_by_page: dict[int, list[dict]] = {}
    for visual in visuals:
        page = int(visual["page"])
        images_by_page.setdefault(page, []).append(_visual_as_image_entry(visual))
    return images_by_page


async def _load_file_visuals(db: AsyncSession, file_id: uuid.UUID) -> list[dict]:
    """Visual elements from pipeline v3 layout JSON (empty if unavailable)."""
    result = await db.execute(
        select(File.layout_json_path).where(File.id == file_id)
    )
    row = result.one_or_none()
    if row is None or not row.layout_json_path:
        return []
    layout = await _load_layout(row.layout_json_path)
    return _enumerate_visuals(layout)


async def _fetch_images_for_file_unified(
    db: AsyncSession,
    file_id: uuid.UUID,
    page_filter: int | None = None,
) -> dict[int, list[dict]]:
    """Layout JSON first (v3), legacy Qdrant IMAGE_COLLECTION as fallback."""
    visuals = await _load_file_visuals(db, file_id)
    if visuals:
        if page_filter is not None:
            visuals = [v for v in visuals if v["page"] == page_filter]
        return _group_visuals_by_page(visuals)
    return await _fetch_images_for_file(file_id, page_filter=page_filter)


async def _fetch_images_for_file(
    file_id: uuid.UUID,
    page_filter: int | None = None,
) -> dict[int, list[dict]]:
    """
    Scrolls Qdrant IMAGE_COLLECTION filtering by file_id (and optionally page).
    Returns dict keyed by page number.
    """
    client = get_async_qdrant_client()

    must_conditions = [
        FieldCondition(key="file_id", match=MatchValue(value=str(file_id))),
        FieldCondition(key="status", match=MatchValue(value="active")),
    ]
    if page_filter is not None:
        must_conditions.append(
            FieldCondition(key="page", match=MatchValue(value=page_filter))
        )

    try:
        scroll_result, _ = await client.scroll(
            collection_name=IMAGE_COLLECTION,
            scroll_filter=Filter(must=must_conditions),
            limit=200,
            with_payload=["page", "image_id", "description", "text_inside", "nearby_text_id"],
        )
    except Exception as exc:
        logger.warning("Qdrant image scroll failed for file %s: %s", file_id, exc)
        return {}

    images_by_page: dict[int, list[dict]] = {}
    for point in scroll_result:
        payload = point.payload or {}
        page = int(payload.get("page") or 0)
        if page not in images_by_page:
            images_by_page[page] = []
        images_by_page[page].append({
            "image_id": str(payload.get("image_id") or point.id),
            "description": payload.get("description") or "",
            "text_inside": payload.get("text_inside") or "",
            "nearby_text_id": payload.get("nearby_text_id"),
        })

    return images_by_page


# ── fetch_file_layout ─────────────────────────────────────────────────────────

def _layout_block_from_element(elem: dict, chunk_by_block: dict[str, Chunk]) -> dict:
    """Map one raw layout element to a layout block, preserving the structural
    fields (bbox, source, sort_order, image_uri, metadata) the raw layout
    carries. Text elements are enriched with their chunk_id/token_count so the
    block stays linkable to retrieval; visual elements keep asset_type/text_inside."""
    meta = elem.get("metadata") or {}
    is_visual = elem.get("source") == "visual_understanding"
    block: dict = {
        "type": "image" if is_visual else "text",
        "id": elem.get("id"),
        "layout_type": elem.get("type"),
        "source": elem.get("source"),
        "sort_order": int(elem.get("sort_order") or 0),
        "bbox": elem.get("bbox"),
        "confidence": elem.get("confidence"),
        "content": (elem.get("content") or ""),
        "image_uri": meta.get("asset_uri") or elem.get("image_uri"),
        "metadata": meta or None,
    }
    if is_visual:
        block["asset_type"] = meta.get("asset_type")
        block["text_inside"] = (meta.get("visible_text") or "")
    else:
        chunk = chunk_by_block.get(elem.get("id"))
        if chunk is not None:
            block["chunk_id"] = str(chunk.id)
            block["token_count"] = chunk.token_count
            block["nearby_image_id"] = chunk.nearby_image_id
    return block


async def fetch_file_layout(db: AsyncSession, bucket_id: uuid.UUID, file_id: uuid.UUID) -> dict | None:
    """
    Returns the full layout map for a file: every page with its blocks in true
    reading order (sort_order), each carrying its raw layout fields — bbox,
    source, sort_order, image_uri and metadata. Served from the stored layout
    JSON (pipeline v3); falls back to a Postgres-chunk + Qdrant-image
    reconstruction for legacy files that have no layout JSON.
    """
    file_result = await db.execute(
        select(File.id, File.name, File.page_count, File.layout_json_path)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = file_result.one_or_none()
    if row is None:
        return None

    chunks_result = await db.execute(
        select(Chunk)
        .where(Chunk.file_id == file_id, Chunk.status == "embedded")
        .order_by(Chunk.page.asc(), Chunk.id)
    )
    chunks = chunks_result.scalars().all()
    chunk_by_block = {c.block_id: c for c in chunks if c.block_id}

    pages: dict[int, list[dict]] = {}
    doc_conflicts: list = []

    if row.layout_json_path:
        # Preferred path: serve the raw layout map with all structural fields.
        layout = await _load_layout(row.layout_json_path)
        doc_conflicts = layout.get("name_conflicts") or []
        for page_obj in layout.get("pages", []):
            page_num = int(page_obj.get("page") or 0)
            elements = sorted(
                page_obj.get("elements", []),
                key=lambda e: e.get("sort_order", 0),
            )
            pages[page_num] = [
                _layout_block_from_element(elem, chunk_by_block) for elem in elements
            ]
    else:
        # Legacy fallback: reconstruct from chunks + images (no bbox/sort_order).
        images_by_page = await _fetch_images_for_file_unified(db, file_id)
        for chunk in chunks:
            pages.setdefault(chunk.page, []).append({
                "type": "text",
                "id": chunk.block_id,
                "chunk_id": str(chunk.id),
                "content": chunk.content,
                "token_count": chunk.token_count,
                "nearby_image_id": chunk.nearby_image_id,
            })
        for page, images in images_by_page.items():
            for img in images:
                pages.setdefault(page, []).append({
                    "type": "image",
                    "id": img.get("image_id"),
                    "description": img.get("description"),
                    "text_inside": img.get("text_inside"),
                    "nearby_text_id": img.get("nearby_text_id"),
                })

    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "total_pages": row.page_count,
        "layout_source": "layout_json" if row.layout_json_path else "reconstructed",
        "name_conflicts": doc_conflicts,
        "pages": [
            {"page": p, "blocks": pages[p]}
            for p in sorted(pages.keys())
        ],
    }


# ── fetch_file_summary ────────────────────────────────────────────────────────

async def fetch_file_summary(db: AsyncSession, bucket_id: uuid.UUID, file_id: uuid.UUID) -> dict | None:
    file_result = await db.execute(
        select(File.id, File.name)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = file_result.one_or_none()
    if row is None:
        return None

    summary_result = await db.execute(
        select(Summary.content)
        .where(Summary.file_id == file_id)
        .order_by(Summary.created_at.desc())
        .limit(1)
    )
    summary = summary_result.scalar_one_or_none() or ""

    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "summary": summary,
    }


# ── fetch_categories ──────────────────────────────────────────────────────────

async def fetch_categories(db: AsyncSession, bucket_id: uuid.UUID) -> list[dict]:
    cat_result = await db.execute(
        select(Category).where(Category.bucket_id == bucket_id).order_by(Category.created_at.asc())
    )
    categories = cat_result.scalars().all()

    count_result = await db.execute(
        select(File.category_id, func.count())
        .where(File.bucket_id == bucket_id, File.status == "ready")
        .group_by(File.category_id)
    )
    counts = {cid: cnt for cid, cnt in count_result.all()}

    return [
        {
            "category_id": str(c.id),
            "name": c.name,
            "color": c.color,
            "files_count": counts.get(c.id, 0),
        }
        for c in categories
    ]


# ── fetch_chunk ───────────────────────────────────────────────────────────────

async def fetch_chunk(db: AsyncSession, bucket_id: uuid.UUID, chunk_id: uuid.UUID) -> dict | None:
    result = await db.execute(
        select(Chunk, File.name)
        .join(File, File.id == Chunk.file_id)
        .where(Chunk.id == chunk_id, Chunk.bucket_id == bucket_id)
    )
    row = result.one_or_none()
    if row is None:
        return None
    chunk, file_name = row

    nearby_image = None
    if chunk.nearby_image_id:
        images_by_page = await _fetch_images_for_file_unified(db, chunk.file_id, page_filter=chunk.page)
        for img in images_by_page.get(chunk.page, []):
            if str(img.get("image_id")) == str(chunk.nearby_image_id):
                nearby_image = img
                break

    return {
        "chunk_id": str(chunk.id),
        "file_id": str(chunk.file_id),
        "file_name": file_name,
        "page": chunk.page,
        "block_id": chunk.block_id,
        "content": chunk.content,
        "token_count": chunk.token_count,
        "nearby_image": nearby_image,
    }


# ── fetch_chunks_list ─────────────────────────────────────────────────────────

async def fetch_chunks_list(db: AsyncSession, bucket_id: uuid.UUID, file_id: uuid.UUID) -> dict | None:
    file_result = await db.execute(
        select(File.id, File.name)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = file_result.one_or_none()
    if row is None:
        return None

    # Deterministic, stable order. NOTE: chunks carry no true reading-order
    # column (no chunk_index), so within a page we can only sort by created_at
    # (ingest order, often identical for a bulk insert) then id as a stable
    # tiebreaker. This guarantees the SAME order every call, but within-page
    # order is approximate. A real chunk_index at ingest is the proper fix.
    chunks_result = await db.execute(
        select(Chunk)
        .where(Chunk.file_id == file_id, Chunk.status == "embedded")
        .order_by(Chunk.page.asc(), Chunk.created_at.asc(), Chunk.id.asc())
    )
    chunks = chunks_result.scalars().all()

    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": str(c.id),
                "page": c.page,
                "block_id": c.block_id,
                "content": c.content,
                "token_count": c.token_count,
                "nearby_image_id": c.nearby_image_id,
            }
            for c in chunks
        ],
    }


# ── fetch_section ─────────────────────────────────────────────────────────────

def _normalize_heading(text: str) -> str:
    """Collapse whitespace so `Report \\nhighlights` matches `report highlights`."""
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


async def fetch_section(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    heading: str,
) -> dict | None:
    """
    Locate a section by heading and return its full body.

    Uses files.section_outline (the ordered list of {heading, page} produced
    at ingest) to compute the section's page range — start = the matched
    section's page, end = the next section's page − 1 (or file.page_count
    for the last section). Then assembles every chunk on those pages in
    reading order from Postgres. Image descriptions for the same range are
    appended so the agent sees the whole section, text + visuals.

    Matching is case-insensitive and whitespace-tolerant. The first heading
    that contains the query as a substring wins; ties are broken by document
    order. Returns None if the file isn't found, an empty `matched_heading`
    if nothing matches.
    """
    result = await db.execute(
        select(File.id, File.name, File.page_count, File.section_outline)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = result.one_or_none()
    if row is None:
        return None

    # Clean so the matchable headings are the same tidy set get_file_stats shows.
    outline: list[dict] = clean_section_outline(row.section_outline or [])
    needle = _normalize_heading(heading)
    if not needle or not outline:
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "query": heading,
            "matched_heading": None,
            "page_start": None,
            "page_end": None,
            "chunks": [],
            "images": [],
        }

    # Find the first outline entry whose heading contains the query.
    match_idx: int | None = None
    for idx, entry in enumerate(outline):
        if needle in _normalize_heading(entry.get("heading", "")):
            match_idx = idx
            break

    if match_idx is None:
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "query": heading,
            "matched_heading": None,
            "page_start": None,
            "page_end": None,
            "chunks": [],
            "images": [],
        }

    page_start = int(outline[match_idx]["page"])
    # Find the next outline entry whose page is strictly greater — that
    # marks where this section ends. Skip continuation headings sharing
    # the same page so multi-heading pages don't collapse to zero width.
    page_end = row.page_count
    for entry in outline[match_idx + 1:]:
        next_page = int(entry["page"])
        if next_page > page_start:
            page_end = next_page - 1
            break

    chunks = await _fetch_chunks_in_page_range(db, file_id, page_start, page_end)
    images = await _fetch_images_in_page_range(db, file_id, page_start, page_end)
    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "query": heading,
        "matched_heading": outline[match_idx]["heading"],
        "page_start": page_start,
        "page_end": page_end,
        "chunks": chunks,
        "images": images,
        "total_chunks": len(chunks),
        "total_images": len(images),
    }


# ── fetch_pages ───────────────────────────────────────────────────────────────

async def fetch_pages(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    page_start: int,
    page_end: int,
) -> dict | None:
    """
    Deterministic page-range reader. Returns every chunk + image on pages
    [page_start, page_end] (inclusive), assembled in reading order. Lets the
    agent drill into a known region of a long document without going through
    similarity search — critical for flat docs with no section structure.

    Clamps the range to [1, file.page_count] so callers can pass loose
    bounds. Returns None when the file isn't accessible.
    """
    result = await db.execute(
        select(File.id, File.name, File.page_count)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = result.one_or_none()
    if row is None:
        return None

    lo = max(1, min(int(page_start), int(page_end)))
    hi = min(row.page_count, max(int(page_start), int(page_end)))
    if hi < lo:
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "page_start": lo,
            "page_end": hi,
            "total_pages_in_file": row.page_count,
            "chunks": [],
            "images": [],
            "total_chunks": 0,
            "total_images": 0,
        }

    chunks = await _fetch_chunks_in_page_range(db, file_id, lo, hi)
    images = await _fetch_images_in_page_range(db, file_id, lo, hi)
    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "page_start": lo,
        "page_end": hi,
        "total_pages_in_file": row.page_count,
        "chunks": chunks,
        "images": images,
        "total_chunks": len(chunks),
        "total_images": len(images),
    }


# ── internal: page-range helpers ──────────────────────────────────────────────

async def _fetch_chunks_in_page_range(
    db: AsyncSession,
    file_id: uuid.UUID,
    page_start: int,
    page_end: int,
) -> list[dict]:
    chunks_result = await db.execute(
        select(Chunk)
        .where(
            and_(
                Chunk.file_id == file_id,
                Chunk.status == "embedded",
                Chunk.page >= page_start,
                Chunk.page <= page_end,
            )
        )
        .order_by(Chunk.page.asc(), Chunk.id)
    )
    chunks = chunks_result.scalars().all()
    return [
        {
            "chunk_id": str(c.id),
            "page": c.page,
            "block_id": c.block_id,
            "content": c.content,
            "token_count": c.token_count,
            "nearby_image_id": c.nearby_image_id,
        }
        for c in chunks
    ]


# ── visual element index (reads layout.json) ──────────────────────────────────

_LAYOUT_CACHE: dict[str, dict] = {}


async def _load_layout(file_layout_path: str) -> dict:
    """Download + parse the structured layout JSON. Cached by R2 key so a
    burst of visual lookups for the same file doesn't re-download."""
    import json as _json

    from app.services.storage.r2 import download_file

    cached = _LAYOUT_CACHE.get(file_layout_path)
    if cached is not None:
        return cached
    raw = await asyncio.to_thread(download_file, file_layout_path)
    parsed = _json.loads(raw.decode("utf-8"))
    _LAYOUT_CACHE[file_layout_path] = parsed
    return parsed


import asyncio  # noqa: E402  (kept near _load_layout so the dependency is obvious)


def _enumerate_visuals(layout: dict) -> list[dict]:
    """Walk the layout JSON and return every visual element in reading order,
    with a stable 1-based index. The order = (page asc, sort_order asc) which
    matches what the human sees scrolling the PDF top-to-bottom."""
    rows: list[dict] = []
    for page_obj in sorted(layout.get("pages", []), key=lambda p: p.get("page", 0)):
        page_num = int(page_obj.get("page") or 0)
        elements = page_obj.get("elements", [])
        # Page elements are already sort_order-sorted in build_export_json, but
        # we re-sort defensively so callers can trust the ordering.
        for elem in sorted(elements, key=lambda e: e.get("sort_order", 0)):
            if elem.get("source") != "visual_understanding":
                continue
            meta = elem.get("metadata") or {}
            row = {
                "page": page_num,
                "sort_order": int(elem.get("sort_order") or 0),
                "element_id": elem.get("id"),
                "type": elem.get("type"),
                "asset_type": meta.get("asset_type"),
                "description": (elem.get("content") or "").strip(),
                "text_inside": (meta.get("visible_text") or "").strip(),
                "asset_uri": meta.get("asset_uri") or elem.get("image_uri"),
                "bbox": elem.get("bbox"),
                "confidence": elem.get("confidence"),
            }
            # Surface ingestion-cleanup signals when present.
            if meta.get("name_conflict"):
                row["name_conflict"] = meta["name_conflict"]
            if meta.get("dup_count"):
                row["dup_count"] = meta["dup_count"]
            if meta.get("duplicate_snapshots"):
                row["duplicate_snapshots"] = meta["duplicate_snapshots"]
            rows.append(row)
    for i, row in enumerate(rows, start=1):
        row["index"] = i
    return rows


def _visual_counts(visuals: list[dict]) -> tuple[int, int, int]:
    """Reconcile the visual counts so total = images + text_blocks always holds.

    The visual-understanding stage emits both rendered assets (images, charts,
    icons, logos, buttons) and pure text regions it read. `total_visuals` counts
    everything; `image_count` excludes the text regions (matching File.image_count).
    Returns (total_visuals, image_count, text_block_count).
    """
    total = len(visuals)
    text_blocks = sum(1 for v in visuals if (v.get("type") or "").lower() == "text")
    return total, total - text_blocks, text_blocks


_VISUAL_COUNTS_NOTE = (
    "total_visuals = image_count + text_block_count. image_count is rendered "
    "visuals (images, charts, icons, logos, buttons); text_block_count is text "
    "regions the visual stage read — included in total_visuals but not images."
)


async def fetch_visual_list(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    *,
    page: int | None = None,
    type_filter: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> dict | None:
    """
    Enumerate every visual element (images, charts, icons, logos, buttons —
    anything the visual-understanding stage extracted) in document order with
    a STABLE 1-based index. This is what makes "the 78th visual element" a
    real query: index 78 always points to the same element across calls.

    Optional filters narrow the listing to a single page or a single visual
    type (e.g. 'chart', 'product_image'). `limit` + `offset` page through
    long manifests so the agent can scroll without loading thousands of
    descriptions into context.
    """
    result = await db.execute(
        select(File.id, File.name, File.page_count, File.image_count, File.layout_json_path)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = result.one_or_none()
    if row is None:
        return None
    if not row.layout_json_path:
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "total_visuals": 0,
            "page_count": row.page_count,
            "image_count": row.image_count,
            "visuals": [],
            "error": "Layout JSON not available for this file.",
        }

    layout = await _load_layout(row.layout_json_path)
    visuals = _enumerate_visuals(layout)

    filtered = visuals
    if page is not None:
        filtered = [v for v in filtered if v["page"] == int(page)]
    if type_filter:
        needle = type_filter.strip().lower()
        filtered = [v for v in filtered if (v.get("type") or "").lower() == needle
                    or (v.get("asset_type") or "").lower() == needle]

    sliced = filtered[max(0, offset): max(0, offset) + max(1, limit)]
    total_visuals, image_count, text_block_count = _visual_counts(visuals)
    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "page_count": row.page_count,
        "image_count": image_count,
        "text_block_count": text_block_count,
        "total_visuals": total_visuals,
        "counts_note": _VISUAL_COUNTS_NOTE,
        "filtered_count": len(filtered),
        "page_filter": page,
        "type_filter": type_filter,
        "limit": limit,
        "offset": offset,
        "visuals": sliced,
    }


async def fetch_visual(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    index: int,
) -> dict | None:
    """
    Return the single visual element at the given 1-based index, together
    with the surrounding section/heading on its page so the agent can
    describe *what* it is and *where* it sits in the document.
    """
    result = await db.execute(
        select(File.id, File.name, File.page_count, File.section_outline, File.layout_json_path)
        .where(File.id == file_id, File.bucket_id == bucket_id, File.status == "ready")
    )
    row = result.one_or_none()
    if row is None:
        return None
    if not row.layout_json_path:
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "requested_index": index,
            "visual": None,
            "error": "Layout JSON not available for this file.",
        }

    layout = await _load_layout(row.layout_json_path)
    visuals = _enumerate_visuals(layout)
    if not visuals:
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "requested_index": index,
            "total_visuals": 0,
            "visual": None,
        }
    if index < 1 or index > len(visuals):
        return {
            "file_id": str(row.id),
            "file_name": row.name,
            "requested_index": index,
            "total_visuals": len(visuals),
            "visual": None,
            "error": f"Index {index} out of range — file has {len(visuals)} visuals.",
        }

    target = visuals[index - 1]

    # Locate the nearest preceding heading from section_outline so the agent
    # gets context like "this image sits under the 'Water' section".
    outline = row.section_outline or []
    enclosing_section = None
    for entry in outline:
        if int(entry.get("page", 0)) <= target["page"]:
            enclosing_section = entry
        else:
            break

    return {
        "file_id": str(row.id),
        "file_name": row.name,
        "requested_index": index,
        "total_visuals": len(visuals),
        "page_count": row.page_count,
        "enclosing_section": enclosing_section,
        "visual": target,
    }


async def _fetch_images_in_page_range(
    db: AsyncSession,
    file_id: uuid.UUID,
    page_start: int,
    page_end: int,
) -> list[dict]:
    """Visuals in a page range — layout JSON first, Qdrant fallback."""
    visuals = await _load_file_visuals(db, file_id)
    if visuals:
        filtered = [
            v for v in visuals if page_start <= int(v["page"]) <= page_end
        ]
        return [_visual_as_image_entry(v, include_page=True) for v in filtered]

    client = get_async_qdrant_client()
    flt = Filter(
        must=[
            FieldCondition(key="file_id", match=MatchValue(value=str(file_id))),
            FieldCondition(key="status", match=MatchValue(value="active")),
            FieldCondition(
                key="page", range=Range(gte=page_start, lte=page_end)
            ),
        ]
    )
    try:
        scroll_result, _ = await client.scroll(
            collection_name=IMAGE_COLLECTION,
            scroll_filter=flt,
            limit=500,
            with_payload=["page", "image_id", "description", "text_inside", "nearby_text_id"],
        )
    except Exception as exc:
        logger.warning("Qdrant image scroll failed for file %s pages %s-%s: %s",
                       file_id, page_start, page_end, exc)
        return []

    out: list[dict] = []
    for point in scroll_result:
        payload = point.payload or {}
        out.append({
            "page": int(payload.get("page") or 0),
            "image_id": str(payload.get("image_id") or point.id),
            "description": payload.get("description") or "",
            "text_inside": payload.get("text_inside") or "",
            "nearby_text_id": payload.get("nearby_text_id"),
        })
    out.sort(key=lambda x: x["page"])
    return out
