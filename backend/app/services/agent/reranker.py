"""
Cross-encoder reranker — Voyage rerank-2.5 (replaces local BGE-Reranker-v2-m3).

Summary chunks are always pinned at the top regardless of rerank score.
Falls back to original Qdrant score order on API error.
"""

from __future__ import annotations

import logging
from dataclasses import replace as dc_replace

from app.config import settings
from app.services.processing_v3.text_sim import bucket_key, normalize_text, similarity

logger = logging.getLogger(__name__)

_RERANK_MODEL = "rerank-2.5"


def _dedupe_by_content(chunks: list, threshold: float) -> list:
    """Drop near-identical chunks, keeping the first (highest-ranked) occurrence.

    Backstop for the ingestion-time dedup: collapses repeated quotes/reviews that
    still slip through (e.g. legacy files not yet reprocessed, or cross-document
    near-duplicates) so the answer layer isn't fed the same passage twice.
    """
    kept: list = []
    seen_norm: set[str] = set()
    buckets: dict[str, list[int]] = {}
    for c in chunks:
        text = getattr(c, "content", "") or ""
        norm = normalize_text(text)
        if not norm:
            kept.append(c)
            continue
        if norm in seen_norm:
            continue
        bk = bucket_key(text)
        if any(similarity(text, kept[j].content or "") >= threshold for j in buckets.get(bk, [])):
            continue
        seen_norm.add(norm)
        buckets.setdefault(bk, []).append(len(kept))
        kept.append(c)
    return kept


async def rerank_chunks(
    query: str,
    chunks: list,
    *,
    limit: int,
) -> list:
    """
    Rerank a list of RetrievedDocumentChunk using Voyage rerank-2.5.

    Summary chunks are pinned at the top — they are document-level overviews
    and must always reach the LLM regardless of per-passage rerank score.
    Falls back to original score order when the API is unavailable.
    """
    if not chunks:
        return chunks

    if not settings.reranker_enabled:
        out = _dedupe_by_content(chunks, settings.retrieval_dedup_threshold) \
            if settings.retrieval_dedup_enabled else chunks
        return out[:limit]

    summaries = [c for c in chunks if c.is_summary]
    regular = [c for c in chunks if not c.is_summary]

    if not regular:
        return chunks[:limit]

    try:
        import voyageai

        client = voyageai.AsyncClient(api_key=settings.voyage_api_key)
        # Rerank ALL candidates (top_k doesn't change Voyage cost), so that after
        # dropping near-duplicates we can still fill `limit` with unique passages.
        result = await client.rerank(
            query=query,
            documents=[c.content for c in regular],
            model=_RERANK_MODEL,
            top_k=len(regular),
        )
        reranked = [
            dc_replace(regular[r.index], score=r.relevance_score)
            for r in result.results
        ]
        combined = summaries + reranked
        if settings.retrieval_dedup_enabled:
            combined = _dedupe_by_content(combined, settings.retrieval_dedup_threshold)
        return combined[:limit]

    except Exception as exc:
        logger.warning("[reranker] Voyage rerank failed — keeping original order: %s", exc)
        fallback = summaries + regular
        if settings.retrieval_dedup_enabled:
            fallback = _dedupe_by_content(fallback, settings.retrieval_dedup_threshold)
        return fallback[:limit]
