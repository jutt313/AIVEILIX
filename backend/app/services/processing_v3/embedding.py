"""
Voyage embedding adapter for pipeline v3.

Ported from Aiveilix-pipline app/adapters/embedding.py.
voyage-3-large → 1024-dim dense vectors (matches the existing Qdrant
text_chunks collection size). Dense-only: no sparse vector is produced, so
the retrieval side queries dense-only too (see agent/retrieval.py).
"""

import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)

_EMBED_BATCH_SIZE = 64
_VOYAGE_MAX_RETRIES = 3
_VOYAGE_TIMEOUT_SECONDS = 60

VOYAGE_MODEL = "voyage-3-large"
VOYAGE_DIM = 1024


def _client():
    import voyageai

    return voyageai.Client(
        api_key=settings.voyage_api_key,
        max_retries=_VOYAGE_MAX_RETRIES,
        timeout=_VOYAGE_TIMEOUT_SECONDS,
    )


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed document texts. Returns one 1024-dim vector per input text."""
    if not texts:
        return []

    client = _client()
    logger.info("voyage_embed_documents_start count=%s", len(texts))

    def _embed_batch(batch: list[str]) -> list[list[float]]:
        result = client.embed(batch, model=VOYAGE_MODEL, input_type="document")
        return result.embeddings

    vectors: list[list[float]] = []
    for start in range(0, len(texts), _EMBED_BATCH_SIZE):
        batch = texts[start:start + _EMBED_BATCH_SIZE]
        vectors.extend(await asyncio.to_thread(_embed_batch, batch))

    if len(vectors) != len(texts):
        raise RuntimeError(f"Voyage returned {len(vectors)} vectors for {len(texts)} texts")
    logger.info("voyage_embed_documents_done count=%s", len(vectors))
    return vectors


async def embed_query(text: str) -> list[float]:
    """Embed a single query string. Returns one 1024-dim vector."""
    client = _client()

    def _embed() -> list[float]:
        result = client.embed([text], model=VOYAGE_MODEL, input_type="query")
        return result.embeddings[0]

    return await asyncio.to_thread(_embed)
