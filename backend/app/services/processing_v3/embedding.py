"""
Voyage embedding adapter for pipeline v3.

Two tiers:
  * voyage-3-large → 1024-dim (the existing `text_chunks` collection).
  * voyage-3-lite  → 512-dim  (the lite `text_chunks_lite` collection used by
    the MCP plan). Same API; the `lite=True` flag swaps the model.

Dense-only: no sparse vector is produced. Retrieval queries dense-only too
(see agent/retrieval.py).
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

VOYAGE_LITE_MODEL = "voyage-3-lite"
VOYAGE_LITE_DIM = 512


def _client():
    import voyageai

    return voyageai.Client(
        api_key=settings.voyage_api_key,
        max_retries=_VOYAGE_MAX_RETRIES,
        timeout=_VOYAGE_TIMEOUT_SECONDS,
    )


def _model_name(lite: bool) -> str:
    if lite:
        return getattr(settings, "voyage_lite_model", None) or VOYAGE_LITE_MODEL
    return VOYAGE_MODEL


async def embed_texts(texts: list[str], lite: bool = False) -> list[list[float]]:
    """Embed document texts. Returns one vector per input text.

    Vector dimension depends on the tier:
      * lite=False → 1024-dim voyage-3-large (default).
      * lite=True  → 512-dim  voyage-3-lite (MCP / lite pipeline).
    """
    if not texts:
        return []

    client = _client()
    model = _model_name(lite)
    logger.info("voyage_embed_documents_start count=%s model=%s", len(texts), model)

    def _embed_batch(batch: list[str]) -> list[list[float]]:
        result = client.embed(batch, model=model, input_type="document")
        return result.embeddings

    batches = [
        texts[start:start + _EMBED_BATCH_SIZE]
        for start in range(0, len(texts), _EMBED_BATCH_SIZE)
    ]
    # Embed batches concurrently, bounded so a large file can't blow Voyage's rate
    # limit. gather preserves order, so vectors stay aligned with the inputs.
    semaphore = asyncio.Semaphore(settings.embed_concurrency)

    async def _run(batch: list[str]) -> list[list[float]]:
        async with semaphore:
            return await asyncio.to_thread(_embed_batch, batch)

    batch_vectors = await asyncio.gather(*(_run(b) for b in batches))
    vectors: list[list[float]] = []
    for bv in batch_vectors:
        vectors.extend(bv)

    if len(vectors) != len(texts):
        raise RuntimeError(f"Voyage returned {len(vectors)} vectors for {len(texts)} texts")
    logger.info("voyage_embed_documents_done count=%s model=%s", len(vectors), model)
    return vectors


async def embed_query(text: str, lite: bool = False) -> list[float]:
    """Embed a single query string. Returns one vector (1024 or 512-dim)."""
    client = _client()
    model = _model_name(lite)

    def _embed() -> list[float]:
        result = client.embed([text], model=model, input_type="query")
        return result.embeddings[0]

    return await asyncio.to_thread(_embed)
