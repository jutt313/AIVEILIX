from __future__ import annotations

import asyncio
import logging
import math
import re
import uuid
from dataclasses import dataclass, replace as dc_replace
from urllib.parse import urlparse

from qdrant_client.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchAny,
    MatchValue,
    Prefetch,
    SparseVector,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.bucket import Bucket
from app.models.chunk import Chunk
from app.models.file import File
from app.models.summary import Summary
from app.qdrant_client import get_async_qdrant_client
from app.services.agent.llamaindex_retrieval import (
    llamaindex_available,
    search_bucket_documents_with_llamaindex,
)
from app.services.processing_v3.embedding import embed_query as _voyage_embed_query
from app.services.qdrant.file_indexer import (
    IMAGE_COLLECTION,
    TEXT_COLLECTION,
    TEXT_COLLECTION_LITE,
)

logger = logging.getLogger(__name__)

CONVERSATION_COLLECTION = "conversation_chunks"
NO_SOURCES_LABEL = "No document or web sources were used."


@dataclass(slots=True)
class RetrievedDocumentChunk:
    chunk_id: uuid.UUID
    file_id: uuid.UUID
    file_name: str
    page: int
    content: str
    score: float
    block_id: str = ""
    is_summary: bool = False
    chunk_index: int = -1  # position in document order; -1 = unknown (pre-v2 or summaries)


@dataclass(slots=True)
class RetrievedMemoryChunk:
    id: uuid.UUID
    message_id: uuid.UUID
    role: str
    content: str
    score: float


@dataclass(slots=True)
class RetrievedWebResult:
    title: str
    url: str
    snippet: str
    score: float


@dataclass(slots=True)
class QueryEmbedding:
    dense: list[float]
    sparse: SparseVector | None = None


import time as _time

_QUERY_EMBED_CACHE: dict[tuple[str, bool], tuple[float, QueryEmbedding]] = {}
_QUERY_EMBED_CACHE_TTL = 60.0  # seconds
_QUERY_EMBED_CACHE_MAX = 64

# Per-bucket tier cache so the hot retrieval path doesn't repeat the SELECT.
_BUCKET_TIER_CACHE: dict[uuid.UUID, tuple[float, str]] = {}
_BUCKET_TIER_TTL = 60.0


async def _bucket_processing_tier(db: AsyncSession, bucket_id: uuid.UUID) -> str:
    """Return 'lite' or 'full' for the bucket, cached for ~60s."""
    now = _time.monotonic()
    cached = _BUCKET_TIER_CACHE.get(bucket_id)
    if cached and (now - cached[0]) < _BUCKET_TIER_TTL:
        return cached[1]
    tier = await db.scalar(
        select(Bucket.processing_tier).where(Bucket.id == bucket_id)
    )
    tier = (tier or "full").lower()
    _BUCKET_TIER_CACHE[bucket_id] = (now, tier)
    return tier


def _text_collection_for(tier: str) -> str:
    return TEXT_COLLECTION_LITE if tier == "lite" else TEXT_COLLECTION


async def _embed_query_text(query: str, lite: bool = False) -> QueryEmbedding:
    """
    Embed a query with Voyage. Default voyage-3-large (1024-dim) matches the
    standard `text_chunks` collection. lite=True swaps to voyage-3-lite
    (512-dim) for the MCP/lite tier's `text_chunks_lite` collection.

    A tiny TTL cache dedupes repeat embeds inside a single turn (e.g. when both
    `search_bucket_documents` and `search_bucket_documents_for_files` run).
    """
    now = _time.monotonic()
    cache_key = (query, lite)
    cached = _QUERY_EMBED_CACHE.get(cache_key)
    if cached and (now - cached[0]) < _QUERY_EMBED_CACHE_TTL:
        return cached[1]

    dense = await _voyage_embed_query(query, lite=lite)
    result = QueryEmbedding(dense=[float(value) for value in dense], sparse=None)

    if len(_QUERY_EMBED_CACHE) >= _QUERY_EMBED_CACHE_MAX:
        # Drop the oldest entry — cheap eviction
        oldest_key = min(_QUERY_EMBED_CACHE, key=lambda k: _QUERY_EMBED_CACHE[k][0])
        _QUERY_EMBED_CACHE.pop(oldest_key, None)
    _QUERY_EMBED_CACHE[cache_key] = (now, result)
    return result


async def _embed_conversation_query(query: str) -> QueryEmbedding:
    """
    Conversation memory is a separate feature with its own `conversation_chunks`
    collection, embedded by app.services.embeddings (BGE-M3 / hash fallback).
    It keeps that model so existing memory vectors stay queryable — only the
    document pipeline moved to Voyage.
    """
    try:
        from app.services.embeddings.service import can_use_semantic_embeddings
        from app.services.embeddings.text_embeddings import embed_text

        if can_use_semantic_embeddings():
            embedded = await embed_text(query)
            return QueryEmbedding(
                dense=[float(value) for value in embedded["dense"]],
                sparse=None,
            )
    except Exception:
        pass

    from app.services.embeddings.service import embed_texts as embed_dense_texts

    dense = embed_dense_texts([query])[0]
    return QueryEmbedding(dense=[float(value) for value in dense], sparse=None)


async def get_conversation_file_scope(db: AsyncSession, conversation_id: uuid.UUID) -> list[uuid.UUID] | None:
    """Return the file_ids the conversation is scoped to.

    None  -> unscoped (full bucket access, including future files).
    []    -> scoped to nothing (user hid every file; no document context).
    [...] -> scoped to that subset.
    """
    from sqlalchemy import text as sql_text
    active = await db.scalar(
        sql_text("SELECT file_scope_active FROM conversations WHERE id = :cid"),
        {"cid": conversation_id},
    )
    if not active:
        return None
    result = await db.execute(
        sql_text("SELECT file_id FROM conversation_file_scope WHERE conversation_id = :cid"),
        {"cid": conversation_id},
    )
    return [row[0] for row in result.fetchall()]


async def _resolve_file_names(db: AsyncSession, file_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
    if not file_ids:
        return {}
    result = await db.execute(select(File.id, File.name, File.status).where(File.id.in_(file_ids)))
    return {
        file_id: name
        for file_id, name, status in result.all()
        if status == "ready"
    }


async def _resolve_file_summaries(db: AsyncSession, file_ids: list[uuid.UUID]) -> dict[uuid.UUID, Summary]:
    if not file_ids:
        return {}
    result = await db.execute(
        select(Summary).where(Summary.file_id.in_(file_ids)).order_by(Summary.created_at.desc())
    )
    summaries: dict[uuid.UUID, Summary] = {}
    for row in result.scalars():
        if row.file_id and row.file_id not in summaries:
            summaries[row.file_id] = row
    return summaries


async def _prioritize_file_summaries(
    db: AsyncSession,
    results: list[RetrievedDocumentChunk],
    *,
    limit: int,
) -> list[RetrievedDocumentChunk]:
    if not results:
        return results

    ordered_file_ids: list[uuid.UUID] = []
    for chunk in results:
        if chunk.file_id not in ordered_file_ids:
            ordered_file_ids.append(chunk.file_id)

    summaries = await _resolve_file_summaries(db, ordered_file_ids)
    output: list[RetrievedDocumentChunk] = []

    for file_id in ordered_file_ids:
        file_chunks = [chunk for chunk in results if chunk.file_id == file_id]
        if not file_chunks:
            continue

        existing_summary = next((chunk for chunk in file_chunks if chunk.is_summary), None)
        if existing_summary is not None:
            output.append(existing_summary)
            output.extend(chunk for chunk in file_chunks if chunk is not existing_summary)
            continue

        summary_row = summaries.get(file_id)
        if summary_row and summary_row.content.strip():
            first_chunk = file_chunks[0]
            output.append(
                RetrievedDocumentChunk(
                    chunk_id=summary_row.id,
                    file_id=file_id,
                    file_name=first_chunk.file_name,
                    page=1,
                    content=summary_row.content,
                    score=first_chunk.score,
                    block_id="doc_summary",
                    is_summary=True,
                )
            )
        output.extend(file_chunks)

    return output[:limit]


def _build_bucket_must(bucket_id: uuid.UUID, allowed_file_ids: list[uuid.UUID] | None) -> list:
    conds = [
        FieldCondition(key="bucket_id", match=MatchValue(value=str(bucket_id))),
        FieldCondition(key="status", match=MatchValue(value="active")),
    ]
    if allowed_file_ids:
        conds.append(FieldCondition(key="file_id", match=MatchAny(any=[str(f) for f in allowed_file_ids])))
    return conds


async def _dense_bucket_search(
    *,
    bucket_id: uuid.UUID,
    query_embedding: QueryEmbedding,
    limit: int,
    allowed_file_ids: list[uuid.UUID] | None = None,
    collection_name: str = TEXT_COLLECTION,
) -> list:
    client = get_async_qdrant_client()
    response = await client.query_points(
        collection_name=collection_name,
        query=query_embedding.dense,
        using="",
        query_filter=Filter(must=_build_bucket_must(bucket_id, allowed_file_ids)),
        limit=limit,
        with_payload=["file_id", "page", "content", "block_id", "is_summary", "chunk_index"],
    )
    return response.points


async def _hybrid_bucket_search(
    *,
    bucket_id: uuid.UUID,
    query_embedding: QueryEmbedding,
    limit: int,
    allowed_file_ids: list[uuid.UUID] | None = None,
    collection_name: str = TEXT_COLLECTION,
) -> list:
    client = get_async_qdrant_client()
    prefetch_limit = max(limit * 8, 24)
    must = _build_bucket_must(bucket_id, allowed_file_ids)
    response = await client.query_points(
        collection_name=collection_name,
        prefetch=[
            Prefetch(query=query_embedding.dense, using="", filter=Filter(must=must), limit=prefetch_limit),
            Prefetch(query=query_embedding.sparse, using="text_sparse", filter=Filter(must=must), limit=prefetch_limit),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=limit,
        with_payload=["file_id", "page", "content", "block_id", "is_summary", "chunk_index"],
    )
    return response.points


# ── Fix 4: Multi-query expansion ───────────────────────────────────────────────

async def _generate_query_rephrasings(query: str) -> list[str]:
    """
    Generate 2 alternative rephrasings of the query using the fastest available LLM.
    Runs with a 4-second timeout; returns [] on any failure so retrieval is never blocked.
    """
    if not settings.query_expansion_enabled:
        return []

    prompt = (
        "Rephrase this question in exactly 2 alternative ways that capture different search angles. "
        "Output only the 2 rephrasings, one per line, no numbering, no extra text.\n\n"
        f"Question: {query}"
    )

    try:
        if settings.anthropic_api_key and not settings.anthropic_api_key.startswith("your-"):
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            resp = await asyncio.wait_for(
                client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=4.0,
            )
            text = resp.content[0].text.strip()
            return [line.strip() for line in text.split("\n") if line.strip()][:2]

        if settings.gemini_api_key:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            model_g = genai.GenerativeModel("gemini-1.5-flash")
            resp = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: model_g.generate_content(prompt)
                ),
                timeout=4.0,
            )
            text = resp.text.strip()
            return [line.strip() for line in text.split("\n") if line.strip()][:2]

        if settings.openai_api_key and not settings.openai_api_key.startswith("your-"):
            from openai import AsyncOpenAI
            client_oai = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await asyncio.wait_for(
                client_oai.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=4.0,
            )
            text = resp.choices[0].message.content.strip()
            return [line.strip() for line in text.split("\n") if line.strip()][:2]

        if settings.deepseek_api_key and not settings.deepseek_api_key.startswith("your-"):
            from openai import AsyncOpenAI
            client_ds = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            resp = await asyncio.wait_for(
                client_ds.chat.completions.create(
                    model="deepseek-chat",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=4.0,
            )
            text = resp.choices[0].message.content.strip()
            return [line.strip() for line in text.split("\n") if line.strip()][:2]

    except Exception as exc:
        logger.debug("Query expansion failed (non-critical, continuing): %s", exc)

    return []


# ── Fix 2: Image collection search ─────────────────────────────────────────────

async def search_bucket_images(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    query: str,
    *,
    limit: int = 3,
) -> list[RetrievedDocumentChunk]:
    """
    Search the image_chunks Qdrant collection using CLIP's text encoder.
    Returns the top matching image chunks as RetrievedDocumentChunk objects
    (content = Gemini image description + text_inside).
    """
    if not settings.image_search_enabled:
        return []

    try:
        from app.services.embeddings.image_embeddings import embed_query_text_for_images
        query_vec = await embed_query_text_for_images(query)
    except Exception as exc:
        logger.debug("Image query embedding failed: %s", exc)
        return []

    client = get_async_qdrant_client()
    try:
        response = await client.query_points(
            collection_name=IMAGE_COLLECTION,
            query=query_vec,
            query_filter=Filter(
                must=[
                    FieldCondition(key="bucket_id", match=MatchValue(value=str(bucket_id))),
                    FieldCondition(key="status", match=MatchValue(value="active")),
                ]
            ),
            limit=limit,
            with_payload=["file_id", "page", "image_id", "description", "text_inside"],
        )
    except Exception as exc:
        logger.debug("Image collection search failed: %s", exc)
        return []

    points = response.points
    if not points:
        return []

    file_ids: set[uuid.UUID] = set()
    for point in points:
        fid = (point.payload or {}).get("file_id")
        if fid:
            try:
                file_ids.add(uuid.UUID(str(fid)))
            except Exception:
                pass

    file_names = await _resolve_file_names(db, file_ids)
    results: list[RetrievedDocumentChunk] = []
    for point in points:
        payload = point.payload or {}
        fid_raw = payload.get("file_id")
        if not fid_raw:
            continue
        try:
            fid = uuid.UUID(str(fid_raw))
        except Exception:
            continue
        fname = file_names.get(fid)
        if fname is None:
            continue

        desc = (payload.get("description") or "").strip()
        text_in = (payload.get("text_inside") or "").strip()
        parts = []
        if desc:
            parts.append(desc)
        if text_in:
            parts.append(f"Text in image: {text_in}")
        content = "\n".join(parts) if parts else "(image — no description available)"

        results.append(
            RetrievedDocumentChunk(
                chunk_id=uuid.UUID(str(point.id)),
                file_id=fid,
                file_name=fname,
                page=int(payload.get("page") or 0),
                content=content,
                score=float(point.score or 0.0),
                block_id=str(payload.get("image_id") or ""),
                is_summary=False,
                chunk_index=-1,
            )
        )

    return results


# ── Fix 3: Context-window expansion ────────────────────────────────────────────

async def _expand_with_context(
    results: list[RetrievedDocumentChunk],
    collection_name: str = TEXT_COLLECTION,
) -> list[RetrievedDocumentChunk]:
    """
    For each non-summary chunk with a known chunk_index, fetch its ±window neighbors
    from Qdrant and prepend/append them as context so the LLM sees the full passage.
    Chunks without chunk_index (old documents, summaries) are returned unchanged.
    """
    window = settings.context_window_size
    if window < 1 or not results:
        return results

    # Group chunks that have a valid chunk_index by file_id
    expandable = [c for c in results if not c.is_summary and c.chunk_index >= 0]
    if not expandable:
        return results

    # Collect which neighbor indexes we need per file
    needed_by_file: dict[uuid.UUID, set[int]] = {}
    for c in expandable:
        fid = c.file_id
        if fid not in needed_by_file:
            needed_by_file[fid] = set()
        for delta in range(1, window + 1):
            if c.chunk_index - delta >= 0:
                needed_by_file[fid].add(c.chunk_index - delta)
            needed_by_file[fid].add(c.chunk_index + delta)

    # Fetch neighbors from Qdrant (one query per file_id)
    client = get_async_qdrant_client()
    neighbors_by_file: dict[uuid.UUID, dict[int, str]] = {}

    for fid, indexes in needed_by_file.items():
        valid = sorted(indexes)
        if not valid:
            continue
        try:
            scroll_result, _ = await client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="file_id", match=MatchValue(value=str(fid))),
                        FieldCondition(key="chunk_index", match=MatchAny(any=valid)),
                        FieldCondition(key="status", match=MatchValue(value="active")),
                    ]
                ),
                limit=len(valid) + 4,  # small buffer for safety
                with_payload=["chunk_index", "content"],
            )
            neighbors_by_file[fid] = {
                int(p.payload["chunk_index"]): str(p.payload.get("content", ""))
                for p in scroll_result
                if p.payload and p.payload.get("chunk_index") is not None
            }
        except Exception as exc:
            logger.debug("Context window fetch failed for file %s: %s", fid, exc)

    # Expand each eligible chunk
    expanded: list[RetrievedDocumentChunk] = []
    for chunk in results:
        if chunk.is_summary or chunk.chunk_index < 0:
            expanded.append(chunk)
            continue

        neighbors = neighbors_by_file.get(chunk.file_id, {})
        prev_parts = [
            neighbors[chunk.chunk_index - d]
            for d in range(window, 0, -1)
            if (chunk.chunk_index - d) in neighbors
        ]
        next_parts = [
            neighbors[chunk.chunk_index + d]
            for d in range(1, window + 1)
            if (chunk.chunk_index + d) in neighbors
        ]

        if not prev_parts and not next_parts:
            expanded.append(chunk)
            continue

        parts: list[str] = []
        if prev_parts:
            parts.append("[Previous context]\n" + " ".join(prev_parts))
        parts.append(chunk.content)
        if next_parts:
            parts.append("[Following context]\n" + " ".join(next_parts))

        expanded.append(dc_replace(chunk, content="\n\n".join(parts)))

    return expanded


# ── Multi-query RRF merge ───────────────────────────────────────────────────────

def _rrf_merge(point_lists: list[list], *, limit: int, k: int = 60) -> list:
    """
    Reciprocal Rank Fusion across multiple Qdrant result lists.
    Deduplicates by point id; the point object with the highest RRF score is kept.
    """
    scores: dict[str, float] = {}
    point_by_id: dict[str, object] = {}

    for ranked_list in point_lists:
        for rank, point in enumerate(ranked_list):
            pid = str(point.id)
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + rank + 1)
            if pid not in point_by_id:
                point_by_id[pid] = point

    sorted_ids = sorted(scores.keys(), key=lambda pid: scores[pid], reverse=True)
    return [point_by_id[pid] for pid in sorted_ids[:limit]]


async def _search_with_text(
    query_text: str,
    bucket_id: uuid.UUID,
    limit: int,
    allowed_file_ids: list[uuid.UUID] | None = None,
    tier: str = "full",
) -> list:
    """Embed query_text and run hybrid/dense search. Returns [] on any error."""
    try:
        emb = await _embed_query_text(query_text, lite=(tier == "lite"))
        collection = _text_collection_for(tier)
        if emb.sparse is not None:
            return await _hybrid_bucket_search(
                bucket_id=bucket_id, query_embedding=emb, limit=limit,
                allowed_file_ids=allowed_file_ids, collection_name=collection,
            )
        return await _dense_bucket_search(
            bucket_id=bucket_id, query_embedding=emb, limit=limit,
            allowed_file_ids=allowed_file_ids, collection_name=collection,
        )
    except Exception:
        return []


def _build_chunk_from_point(point, file_names: dict[uuid.UUID, str]) -> RetrievedDocumentChunk | None:
    payload = point.payload or {}
    file_id_raw = payload.get("file_id")
    if not file_id_raw:
        return None
    try:
        file_id = uuid.UUID(str(file_id_raw))
    except Exception:
        return None
    file_name = file_names.get(file_id)
    if file_name is None:
        return None
    return RetrievedDocumentChunk(
        chunk_id=uuid.UUID(str(point.id)),
        file_id=file_id,
        file_name=file_name,
        page=int(payload.get("page") or 0),
        content=str(payload.get("content") or ""),
        score=float(point.score or 0.0),
        block_id=str(payload.get("block_id") or ""),
        is_summary=bool(payload.get("is_summary", False)),
        chunk_index=int(payload.get("chunk_index", -1)),
    )


async def search_bucket_documents(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    query: str,
    *,
    limit: int = 5,
    candidate_limit: int = 200,
    allowed_file_ids: list[uuid.UUID] | None = None,
) -> list[RetrievedDocumentChunk]:
    # When a thread scope is set but empty, return nothing (user picked no files).
    if allowed_file_ids is not None and len(allowed_file_ids) == 0:
        return []

    # Image search runs in parallel with everything else, on both the fast and
    # escalated path.
    image_task: asyncio.Task = asyncio.ensure_future(
        search_bucket_images(db, bucket_id, query, limit=3)
    )

    # ── Tier routing ───────────────────────────────────────────────────────────
    tier = await _bucket_processing_tier(db, bucket_id)
    is_lite = tier == "lite"
    text_collection = _text_collection_for(tier)

    # ── Main query embedding ───────────────────────────────────────────────────
    query_embedding = await _embed_query_text(query, lite=is_lite)

    # ── LlamaIndex path ────────────────────────────────────────────────────────
    # Skip LlamaIndex when a scope is set; native path supports file filtering.
    # Skip LlamaIndex for lite buckets — its bootstrap targets the 1024-dim
    # collection, so it would query the wrong dimension/index.
    if not is_lite and allowed_file_ids is None and settings.llamaindex_enabled and llamaindex_available():
        try:
            llama_results = await search_bucket_documents_with_llamaindex(
                db,
                bucket_id=bucket_id,
                query=query,
                query_embedding=query_embedding.dense,
                limit=limit,
                candidate_limit=candidate_limit,
                resolve_file_names=_resolve_file_names,
                retrieved_chunk_cls=RetrievedDocumentChunk,
            )
            if llama_results:
                results = await _prioritize_file_summaries(db, llama_results, limit=candidate_limit)
                results = await _expand_with_context(results, collection_name=text_collection)
                if settings.reranker_enabled:
                    from app.services.agent.reranker import rerank_chunks

                    results = await rerank_chunks(query, results, limit=limit)
                image_results = await image_task
                return _merge_image_results(results, image_results)
        except Exception:
            pass

    # ── Helpers shared by the fast and escalated paths ─────────────────────────
    async def _run_main_search(search_limit: int) -> list:
        try:
            if query_embedding.sparse is not None:
                return await _hybrid_bucket_search(
                    bucket_id=bucket_id, query_embedding=query_embedding,
                    limit=search_limit, allowed_file_ids=allowed_file_ids,
                    collection_name=text_collection,
                )
            return await _dense_bucket_search(
                bucket_id=bucket_id, query_embedding=query_embedding,
                limit=search_limit, allowed_file_ids=allowed_file_ids,
                collection_name=text_collection,
            )
        except Exception:
            try:
                return await _dense_bucket_search(
                    bucket_id=bucket_id, query_embedding=query_embedding,
                    limit=search_limit, allowed_file_ids=allowed_file_ids,
                    collection_name=text_collection,
                )
            except Exception:
                return []

    async def _assemble(points: list) -> list[RetrievedDocumentChunk]:
        file_ids: set[uuid.UUID] = set()
        for point in points:
            fid = (point.payload or {}).get("file_id")
            if fid:
                try:
                    file_ids.add(uuid.UUID(str(fid)))
                except Exception:
                    pass
        file_names = await _resolve_file_names(db, file_ids)
        built: list[RetrievedDocumentChunk] = []
        for point in points:
            chunk = _build_chunk_from_point(point, file_names)
            if chunk is not None:
                built.append(chunk)
            if len(built) >= candidate_limit:
                break
        # 1. Summaries to top  2. Neighbor expansion  3. Cross-encoder rerank
        built = await _prioritize_file_summaries(db, built, limit=limit)
        built = await _expand_with_context(built, collection_name=text_collection)
        if settings.reranker_enabled:
            from app.services.agent.reranker import rerank_chunks

            built = await rerank_chunks(query, built, limit=limit)
        return built

    # ── Fast pass ──────────────────────────────────────────────────────────────
    # Most questions are answered straight from the documents. Do the cheap thing
    # first — one dense search over a small candidate set — and return immediately
    # when the result is confident. This skips the query-rephrasing LLM call and
    # the wide multi-query sweep for the common, easy case.
    if settings.retrieval_adaptive_enabled:
        fast_limit = max(limit, settings.retrieval_fast_candidate_limit)
        fast_points = await _run_main_search(fast_limit)
        fast_results = await _assemble(fast_points)
        if high_confidence_bucket_match(fast_results):
            image_results = await image_task
            return _merge_image_results(fast_results, image_results)

    # ── Escalation (also the path when adaptive retrieval is disabled) ──────────
    # The fast pass was weak — search harder. Widen the candidate net and add LLM
    # query rephrasings, fusing all hits with reciprocal-rank fusion before the
    # rerank. Nothing is capped away: a weak match triggers *more* retrieval.
    search_limit = max(limit, candidate_limit)
    point_lists = [await _run_main_search(search_limit)]

    rephrasings = await _generate_query_rephrasings(query)
    if rephrasings:
        extra_searches = await asyncio.gather(
            *[_search_with_text(r, bucket_id, search_limit, allowed_file_ids=allowed_file_ids, tier=tier) for r in rephrasings],
            return_exceptions=True,
        )
        point_lists.extend(p for p in extra_searches if isinstance(p, list))

    merged_points = (
        _rrf_merge(point_lists, limit=search_limit)
        if len(point_lists) > 1
        else point_lists[0]
    )
    results = await _assemble(merged_points)
    image_results = await image_task
    return _merge_image_results(results, image_results)


def _merge_image_results(
    text_results: list[RetrievedDocumentChunk],
    image_results: list[RetrievedDocumentChunk],
) -> list[RetrievedDocumentChunk]:
    """
    Append image results that scored above 0.5 and don't duplicate an existing
    text result on the same page of the same file.
    Capped at 2 image results to avoid overwhelming the text context.
    """
    if not image_results:
        return text_results

    from app.services.processing_v3.text_sim import similarity

    seen: set[tuple[uuid.UUID, int]] = {(c.file_id, c.page) for c in text_results}
    existing_texts: list[str] = [c.content or "" for c in text_results]
    added = 0
    for img in image_results:
        if img.score < 0.5:
            continue
        if added >= 2:
            break
        key = (img.file_id, img.page)
        if key in seen:
            continue
        # Skip an image whose text duplicates a passage already selected (e.g. a
        # magazine-quote screenshot repeating a quote that's already in a chunk).
        img_text = img.content or ""
        if settings.retrieval_dedup_enabled and img_text and any(
            similarity(img_text, t) >= settings.retrieval_dedup_threshold
            for t in existing_texts
        ):
            continue
        text_results.append(img)
        seen.add(key)
        existing_texts.append(img_text)
        added += 1

    return text_results


async def search_bucket_documents_for_files(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    query: str,
    file_ids: list[uuid.UUID],
    *,
    limit: int = 5,
) -> list[RetrievedDocumentChunk]:
    """Search only within specific files (for @mentioned files priority search)."""
    if not file_ids:
        return []

    tier = await _bucket_processing_tier(db, bucket_id)
    is_lite = tier == "lite"
    text_collection = _text_collection_for(tier)
    query_embedding = await _embed_query_text(query, lite=is_lite)
    file_id_strings = [str(fid) for fid in file_ids]

    must_conditions = [
        FieldCondition(key="bucket_id", match=MatchValue(value=str(bucket_id))),
        FieldCondition(key="status", match=MatchValue(value="active")),
        FieldCondition(key="file_id", match=MatchAny(any=file_id_strings)),
    ]

    client = get_async_qdrant_client()
    try:
        if query_embedding.sparse is not None:
            prefetch_limit = max(limit * 8, 24)
            response = await client.query_points(
                collection_name=text_collection,
                prefetch=[
                    Prefetch(
                        query=query_embedding.dense,
                        using="",
                        filter=Filter(must=must_conditions),
                        limit=prefetch_limit,
                    ),
                    Prefetch(
                        query=query_embedding.sparse,
                        using="text_sparse",
                        filter=Filter(must=must_conditions),
                        limit=prefetch_limit,
                    ),
                ],
                query=FusionQuery(fusion=Fusion.RRF),
                limit=limit,
                with_payload=["file_id", "page", "content", "block_id", "is_summary", "chunk_index"],
            )
        else:
            response = await client.query_points(
                collection_name=text_collection,
                query=query_embedding.dense,
                using="",
                query_filter=Filter(must=must_conditions),
                limit=limit,
                with_payload=["file_id", "page", "content", "block_id", "is_summary", "chunk_index"],
            )
        points = response.points
    except Exception:
        return []

    file_names = await _resolve_file_names(db, set(file_ids))
    results: list[RetrievedDocumentChunk] = []
    for point in points:
        chunk = _build_chunk_from_point(point, file_names)
        if chunk is not None:
            results.append(chunk)
    return results


_CROSS_DOC_TRIGGERS = (
    "compare", "comparison", "versus", " vs ", " vs.", "between", "both",
    " with ", " and ",
    "each document", "each doc", "each paper", "across documents",
    "across all documents", "across docs", "cross-doc", "cross document", "which mentions",
    "which one", "differences", "similarities",
)

_ALL_DOC_TRIGGERS = (
    "all documents", "all docs", "all files", "all papers",
    "every document", "every doc", "every file", "every paper",
    "each document", "each doc", "each file", "each paper",
    "entire bucket", "whole bucket",
)

_COLLECTION_WIDE_TRIGGERS = _ALL_DOC_TRIGGERS + (
    "any document", "any documents", "any doc", "any docs",
    "any file", "any files", "any paper", "any papers",
    "the documents", "the docs", "the files", "the papers",
    "this bucket", "the bucket",
)

_COLLECTION_AUDIT_TOPICS = (
    "risks", "limitations", "caveats", "drawbacks", "concerns",
    "uncertainties", "weaknesses", "assumptions", "failure modes",
    "open questions", "future work",
)

_FIELD_EXTRACTION_OPENERS = (
    "tell me", "show me", "give me", "list", "extract", "find",
    "get", "what is", "what are", "what was", "what were",
    "how much", "how many",
)

_FIELD_EXTRACTION_STOPWORDS = {
    "a", "an", "and", "are", "by", "can", "do", "does", "for", "from",
    "get", "give", "how", "in", "is", "list", "me", "of", "please",
    "show", "tell", "the", "to", "was", "were", "what",
}

_METRIC_ACRONYMS = {
    "roi", "roe", "roa", "eps", "ebitda", "arr", "mrr", "nrr", "cac",
    "ltv", "cagr", "capex", "opex", "qoq", "yoy", "q1", "q2", "q3", "q4",
}

_METRIC_HINTS = {
    "amount", "balance", "cash", "cost", "costs", "debt", "ebitda",
    "expense", "expenses", "growth", "income", "margin", "metric", "metrics",
    "number", "numbers", "profit", "profits", "ratio", "revenue", "revenues",
    "roi", "sales", "score", "scores", "value", "values",
}

_STANDALONE_IMAGE_TRIGGERS = (
    " image ", " images ",
    "image file", "image files", "standalone image", "standalone images",
    "screenshot", "screenshots", "png", ".png", "jpg", ".jpg", "jpeg",
    ".jpeg", "picture", "pictures", "photo", "photos",
)

_IMAGE_COLLECTION_HINTS = (
    "all images", "all image", "three images", "3 images", "the images",
    "these images", "those images", "image files", "screenshots",
)

_SUMMARY_MATCH_STOPWORDS = {
    "about", "also", "between", "compare", "comparison", "document", "documents",
    "paper", "papers", "report", "reports", "model", "models", "largest",
    "variant", "variants", "what", "which", "with", "and", "the", "this",
    "that", "from", "does", "did", "use", "uses", "used",
}

_DOCUMENT_TYPE_HINTS = ("pdf", "doc", "word", "text", "markdown", "csv", "sheet")
_DOCUMENT_EXTENSIONS = (".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".xlsx", ".xls")
_CATEGORY_HINTS = {
    "ai": {
        "query": {"ai", "artificial", "intelligence", "machine", "learning", "neural", "transformer", "nlp"},
        "document": {
            "ai", "artificial", "intelligence", "machine", "learning", "neural",
            "transformer", "attention", "language", "translation", "nlp",
            "encoder", "decoder",
        },
    },
    "physics": {
        "query": {"physics", "physical", "particle", "qcd", "collider", "hep", "diphoton", "higgs"},
        "document": {
            "physics", "particle", "qcd", "collider", "hadron", "diphoton",
            "higgs", "tev", "lhc", "tevatron", "photon", "cross", "section",
        },
    },
    "finance": {
        "query": {"finance", "financial", "revenue", "earnings", "sales", "cash", "income"},
        "document": {
            "finance", "financial", "revenue", "earnings", "sales", "cash",
            "income", "balance", "assets", "liabilities", "shareholders",
        },
    },
}


def _match_tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) >= 2]


def _compact_match_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _file_stem(name: str) -> str:
    return re.sub(r"\.[a-z0-9]{1,8}$", "", name.lower()).replace("_", " ").replace("-", " ").strip()


def _has_cross_doc_intent(query: str) -> bool:
    lowered = f" {query.lower()} "
    return (
        _has_collection_wide_intent(query)
        or _has_standalone_image_intent(query)
        or any(trigger in lowered for trigger in _CROSS_DOC_TRIGGERS)
    )


def _has_all_document_intent(query: str) -> bool:
    lowered = f" {query.lower()} "
    return any(trigger in lowered for trigger in _ALL_DOC_TRIGGERS)


def _has_collection_wide_intent(query: str) -> bool:
    lowered = f" {query.lower()} "
    if any(trigger in lowered for trigger in _COLLECTION_WIDE_TRIGGERS):
        return True
    if any(topic in lowered for topic in _COLLECTION_AUDIT_TOPICS):
        return True
    return _has_generic_field_extraction_intent(query)


def _has_standalone_image_intent(query: str) -> bool:
    lowered = f" {query.lower()} "
    if not any(trigger in lowered for trigger in _STANDALONE_IMAGE_TRIGGERS):
        return False
    return (
        any(hint in lowered for hint in _IMAGE_COLLECTION_HINTS)
        or " file" in lowered
        or " bucket" in lowered
        or " shown " in lowered
        or " what is in " in lowered
        or " what are in " in lowered
    )


def _has_named_entity_hint(query: str) -> bool:
    for token in re.findall(r"[A-Za-z][A-Za-z0-9&.-]*", query):
        lowered = token.lower().strip(".")
        if lowered in _FIELD_EXTRACTION_STOPWORDS or lowered in _METRIC_ACRONYMS:
            continue
        if re.fullmatch(r"(q[1-4]|fy)?20\d{2}", lowered):
            continue
        if token.isupper() or (len(token) > 2 and token[0].isupper()):
            return True
    return False


def _has_generic_field_extraction_intent(query: str) -> bool:
    lowered = query.lower().strip()
    if not any(lowered.startswith(opener) or f" {opener} " in f" {lowered} " for opener in _FIELD_EXTRACTION_OPENERS):
        return False
    if _has_named_entity_hint(query):
        return False

    content_tokens = [
        token for token in _match_tokens(query)
        if token not in _FIELD_EXTRACTION_STOPWORDS
    ]
    if not content_tokens:
        return False
    if len(content_tokens) <= 4:
        return True
    return bool(set(content_tokens) & _METRIC_HINTS)


def _is_document_like_file(file_name: str | None, file_type: str | None) -> bool:
    lowered_name = (file_name or "").lower()
    lowered_type = (file_type or "").lower()
    return lowered_name.endswith(_DOCUMENT_EXTENSIONS) or any(
        hint in lowered_type for hint in _DOCUMENT_TYPE_HINTS
    )


def _file_match_score(query: str, file_name: str, summary: str = "") -> float:
    lowered = query.lower()
    compact_query = _compact_match_text(query)
    stem = _file_stem(file_name)
    compact_stem = _compact_match_text(stem)
    stem_tokens = [t for t in _match_tokens(stem) if t not in {"pdf", "doc", "paper", "report"}]
    query_tokens = set(_match_tokens(query))

    score = 0.0
    if file_name.lower() in lowered:
        score += 8.0
    if stem and stem in lowered:
        score += 7.0
    if compact_stem and len(compact_stem) >= 4 and compact_stem in compact_query:
        score += 7.0
    if stem_tokens:
        overlap = sum(1 for token in stem_tokens if token in query_tokens)
        if overlap == len(stem_tokens):
            score += 5.0
        elif overlap:
            score += 3.0 * (overlap / len(stem_tokens))

    # First-page summaries often contain the human title ("Llama 2", "GPT-3")
    # even when the filename is abbreviated. Keep this weak to avoid dragging in
    # unrelated files from broad summary vocabulary.
    summary_tokens = set(_match_tokens(summary[:900]))
    distinctive_query_tokens = {
        token for token in query_tokens
        if len(token) >= 4 and token not in _SUMMARY_MATCH_STOPWORDS
    }
    title_overlap = len(distinctive_query_tokens & summary_tokens)
    if title_overlap >= 2:
        score += min(2.0, title_overlap / 3)
    elif title_overlap == 1:
        score += 3.0

    return score


def _category_match_score(query: str, file_name: str, summary: str = "") -> float:
    query_tokens = set(_match_tokens(query))
    doc_tokens = set(_match_tokens(f"{file_name} {summary[:1800]}"))
    score = 0.0
    for hint in _CATEGORY_HINTS.values():
        if query_tokens & hint["query"] and doc_tokens & hint["document"]:
            score += 4.0
    return score


async def _resolve_query_target_files(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    query: str,
    *,
    allowed_file_ids: list[uuid.UUID] | None = None,
    max_files: int = 4,
) -> list[uuid.UUID]:
    file_stmt = select(File.id, File.name, File.type).where(
        File.bucket_id == bucket_id,
        File.status == "ready",
    )
    if allowed_file_ids is not None:
        if not allowed_file_ids:
            return []
        file_stmt = file_stmt.where(File.id.in_(allowed_file_ids))

    files = (await db.execute(file_stmt)).all()
    if len(files) < 2:
        return []

    document_files = [
        (file_id, name)
        for file_id, name, file_type in files
        if _is_document_like_file(name, file_type)
    ]
    if len(document_files) < 2:
        return []

    summaries = await _resolve_file_summaries(db, [file_id for file_id, _ in document_files])
    scored: list[tuple[float, uuid.UUID]] = []
    for file_id, name in document_files:
        summary = summaries.get(file_id)
        summary_text = summary.content if summary else ""
        score = _file_match_score(query, name, summary_text)
        if score < 3.0:
            score += _category_match_score(query, name, summary_text)
        if score >= 3.0:
            scored.append((score, file_id))

    scored.sort(key=lambda item: item[0], reverse=True)
    target_ids = [file_id for _, file_id in scored[:max_files]]
    if len(target_ids) >= 2:
        return target_ids
    return []


async def _resolve_cross_doc_fallback_files(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    *,
    allowed_file_ids: list[uuid.UUID] | None = None,
    max_files: int = 8,
) -> list[uuid.UUID]:
    file_stmt = (
        select(File.id, File.name, File.type)
        .where(File.bucket_id == bucket_id, File.status == "ready")
        .order_by(File.created_at.asc())
    )
    if allowed_file_ids is not None:
        if not allowed_file_ids:
            return []
        file_stmt = file_stmt.where(File.id.in_(allowed_file_ids))

    rows = (await db.execute(file_stmt)).all()
    document_ids: list[uuid.UUID] = []
    for file_id, name, file_type in rows:
        if _is_document_like_file(name, file_type):
            document_ids.append(file_id)

    if len(document_ids) >= 2:
        return document_ids[:max_files]
    return []


async def search_bucket_standalone_images(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    *,
    allowed_file_ids: list[uuid.UUID] | None = None,
    max_files: int = 12,
) -> list[RetrievedDocumentChunk]:
    file_stmt = (
        select(File.id, File.name)
        .where(File.bucket_id == bucket_id, File.status == "ready", File.type == "image")
        .order_by(File.created_at.asc())
    )
    if allowed_file_ids is not None:
        if not allowed_file_ids:
            return []
        file_stmt = file_stmt.where(File.id.in_(allowed_file_ids))

    image_files = (await db.execute(file_stmt)).all()
    if not image_files:
        return []
    image_files = image_files[:max_files]
    image_ids = [file_id for file_id, _ in image_files]

    summaries = await _resolve_file_summaries(db, image_ids)
    chunks_result = await db.execute(
        select(Chunk.file_id, Chunk.id, Chunk.page, Chunk.content, Chunk.block_id)
        .where(Chunk.file_id.in_(image_ids), Chunk.status == "embedded")
        .order_by(Chunk.file_id.asc(), Chunk.page.asc(), Chunk.id.asc())
    )
    chunks_by_file: dict[uuid.UUID, list[tuple[uuid.UUID, int, str, str]]] = {}
    for file_id, chunk_id, page, content, block_id in chunks_result.all():
        chunks_by_file.setdefault(file_id, []).append((chunk_id, page, content, block_id))

    results: list[RetrievedDocumentChunk] = []
    for index, (file_id, name) in enumerate(image_files):
        parts = [f"Standalone image file: {name}"]
        summary = summaries.get(file_id)
        if summary and summary.content.strip():
            parts.append(f"Summary:\n{summary.content.strip()}")

        file_chunks = chunks_by_file.get(file_id, [])
        for _, page, content, _ in file_chunks[:4]:
            clean = (content or "").strip()
            if clean:
                parts.append(f"Page {page} extracted content:\n{clean}")

        if len(parts) == 1:
            parts.append("No extracted image description or OCR text is available.")

        first_chunk = file_chunks[0] if file_chunks else None
        results.append(
            RetrievedDocumentChunk(
                chunk_id=first_chunk[0] if first_chunk else file_id,
                file_id=file_id,
                file_name=name,
                page=first_chunk[1] if first_chunk else 1,
                content="\n\n".join(parts),
                score=1.0 - (index * 0.001),
                block_id=first_chunk[3] if first_chunk else "standalone-image",
                is_summary=False,
                chunk_index=-1,
            )
        )
    return results


def _dedupe_document_chunks(chunks: list[RetrievedDocumentChunk]) -> list[RetrievedDocumentChunk]:
    seen: set[uuid.UUID] = set()
    output: list[RetrievedDocumentChunk] = []
    for chunk in chunks:
        if chunk.chunk_id in seen:
            continue
        seen.add(chunk.chunk_id)
        output.append(chunk)
    return output


async def search_bucket_documents_with_file_coverage(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    query: str,
    *,
    limit: int = 5,
    allowed_file_ids: list[uuid.UUID] | None = None,
) -> list[RetrievedDocumentChunk]:
    """
    Generation-oriented retrieval. For normal questions this is the standard
    bucket search. For comparison/cross-document questions, force a small search
    inside each matched file so global top-k/reranking cannot starve one side.
    """
    if allowed_file_ids is not None and len(allowed_file_ids) == 0:
        return []

    if _has_standalone_image_intent(query):
        image_chunks = await search_bucket_standalone_images(
            db, bucket_id, allowed_file_ids=allowed_file_ids
        )
        if image_chunks:
            return image_chunks

    if not _has_cross_doc_intent(query):
        return await search_bucket_documents(
            db, bucket_id, query, limit=limit, allowed_file_ids=allowed_file_ids
        )

    target_file_ids: list[uuid.UUID] = []
    if _has_collection_wide_intent(query):
        target_file_ids = await _resolve_cross_doc_fallback_files(
            db, bucket_id, allowed_file_ids=allowed_file_ids, max_files=12
        )
    if len(target_file_ids) < 2:
        target_file_ids = await _resolve_query_target_files(
            db, bucket_id, query, allowed_file_ids=allowed_file_ids
        )
    if len(target_file_ids) < 2:
        target_file_ids = await _resolve_cross_doc_fallback_files(
            db, bucket_id, allowed_file_ids=allowed_file_ids
        )
    if len(target_file_ids) < 2:
        return await search_bucket_documents(
            db, bucket_id, query, limit=limit, allowed_file_ids=allowed_file_ids
        )

    per_file_limit = 3
    per_file_results = await asyncio.gather(
        *[
            search_bucket_documents_for_files(
                db, bucket_id, query, [file_id], limit=per_file_limit
            )
            for file_id in target_file_ids
        ],
        return_exceptions=True,
    )

    covered: list[RetrievedDocumentChunk] = []
    for result in per_file_results:
        if isinstance(result, list):
            covered.extend(result[:per_file_limit])

    general_limit = max(limit, min(12, len(target_file_ids) * per_file_limit + 4))
    general = await search_bucket_documents(
        db, bucket_id, query, limit=general_limit, allowed_file_ids=target_file_ids
    )

    merged = _dedupe_document_chunks(covered + general)
    max_chunks = max(limit, min(12, len(target_file_ids) * per_file_limit + 2))
    return merged[:max_chunks]


async def search_conversation_memory(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    query: str,
    *,
    limit: int = 5,
    candidate_limit: int = 200,
) -> list[RetrievedMemoryChunk]:
    del db, candidate_limit

    client = get_async_qdrant_client()
    query_embedding = await _embed_conversation_query(query)
    try:
        response = await client.query_points(
            collection_name=CONVERSATION_COLLECTION,
            query=query_embedding.dense,
            query_filter=Filter(
                must=[
                    FieldCondition(key="conversation_id", match=MatchValue(value=str(conversation_id))),
                ]
            ),
            limit=limit,
            with_payload=["message_id", "role", "content"],
        )
    except Exception:
        return []

    results: list[RetrievedMemoryChunk] = []
    for point in response.points:
        payload = point.payload or {}
        message_id = payload.get("message_id")
        if not message_id:
            continue
        results.append(
            RetrievedMemoryChunk(
                id=uuid.UUID(str(point.id)),
                message_id=uuid.UUID(str(message_id)),
                role=str(payload.get("role") or "user"),
                content=str(payload.get("content") or ""),
                score=float(point.score or 0.0),
            )
        )
    return results


def format_sources_section(document_chunks: list[RetrievedDocumentChunk], web_results: list[RetrievedWebResult]) -> tuple[str, list[dict[str, object]]]:
    lines = ["Sources:"]
    payload: list[dict[str, object]] = []

    seen_docs: set[tuple[uuid.UUID, int, bool]] = set()
    for chunk in document_chunks:
        key = (chunk.file_id, chunk.page, chunk.is_summary)
        if key in seen_docs:
            continue
        seen_docs.add(key)
        label = (
            f"[doc] {chunk.file_name} — Overview"
            if chunk.is_summary
            else f"[doc] {chunk.file_name} — Page {chunk.page}"
        )
        lines.append(label)
        payload.append(
            {
                "kind": "document",
                "label": label,
                "file_id": str(chunk.file_id),
                "chunk_id": str(chunk.chunk_id),
                "page": chunk.page,
                "is_summary": chunk.is_summary,
                "score": round(chunk.score, 4),
            }
        )

    seen_urls: set[str] = set()
    for result in web_results:
        if result.url in seen_urls:
            continue
        seen_urls.add(result.url)
        parsed = urlparse(result.url)
        label = f"[web] {parsed.netloc}{parsed.path or ''}"
        lines.append(label)
        payload.append(
            {
                "kind": "web",
                "label": label,
                "url": result.url,
                "score": round(result.score, 4),
            }
        )

    if len(lines) == 1:
        lines.append(NO_SOURCES_LABEL)

    return "\n".join(lines), payload


def high_confidence_bucket_match(results: list[RetrievedDocumentChunk]) -> bool:
    if not results:
        return False
    if results[0].score >= 0.65:
        return True
    if len(results) >= 2 and math.isclose(results[0].score, results[1].score, rel_tol=0.08):
        return results[0].score >= 0.4
    return len(results) >= 3 and results[0].score >= 0.3


def needs_fresh_web_data(query: str) -> bool:
    return any(
        token in query.lower()
        for token in (
            "latest", "recent", "today", "current", "now", "news", "price", "pricing",
            "stock", "weather", "2026", "2027", "update", "updated", "release date",
        )
    )
