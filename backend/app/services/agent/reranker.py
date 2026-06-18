"""
Cross-encoder reranker — Voyage rerank-2.5 (replaces local BGE-Reranker-v2-m3).

Summary chunks are always pinned at the top regardless of rerank score.
Falls back to original Qdrant score order on API error.
"""

from __future__ import annotations

import logging
from dataclasses import replace as dc_replace

from app.config import settings

logger = logging.getLogger(__name__)

_RERANK_MODEL = "rerank-2.5"


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
        return chunks[:limit]

    summaries = [c for c in chunks if c.is_summary]
    regular = [c for c in chunks if not c.is_summary]

    if not regular:
        return chunks[:limit]

    try:
        import voyageai

        client = voyageai.AsyncClient(api_key=settings.voyage_api_key)
        result = await client.rerank(
            query=query,
            documents=[c.content for c in regular],
            model=_RERANK_MODEL,
            top_k=min(limit, len(regular)),
        )
        reranked = [
            dc_replace(regular[r.index], score=r.relevance_score)
            for r in result.results
        ]
        return (summaries + reranked)[:limit]

    except Exception as exc:
        logger.warning("[reranker] Voyage rerank failed — keeping original order: %s", exc)
        return (summaries + regular)[:limit]
