"""
Text embedding service using BGE-M3 (FlagEmbedding).

Produces:
- dense_vector:  list[float] — 1024 dimensions
- sparse_vector: dict[int, float] — BM25 lexical weights for hybrid search
"""

import logging
from typing import Any

from app.services.pipeline.retry import with_retry

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is False:
        raise RuntimeError("BGE-M3 model is unavailable in this environment")
    if _model is None:
        from FlagEmbedding import BGEM3FlagModel
        logger.info("Loading BGE-M3 model (first call — may take a moment)...")
        try:
            _model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
        except Exception as exc:
            _model = False
            logger.warning("BGE-M3 model unavailable, semantic query embedding will fall back: %s", exc)
            raise RuntimeError("BGE-M3 model is unavailable in this environment") from exc
        logger.info("BGE-M3 model loaded.")
    return _model


@with_retry("text_embedding")
async def embed_texts(texts: list[str]) -> list[dict[str, Any]]:
    """
    Embed a list of texts.
    Returns a list of dicts: { "dense": list[float], "sparse": dict[int, float] }
    Order matches input list.
    """
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(None, _embed_sync, texts)


def _embed_sync(texts: list[str]) -> list[dict[str, Any]]:
    model = _get_model()
    output = model.encode(
        texts,
        return_dense=True,
        return_sparse=True,
        return_colbert_vecs=False,
        batch_size=12,
    )

    dense_vecs = output["dense_vecs"]
    lexical_weights = output["lexical_weights"]

    results = []
    for dense, sparse in zip(dense_vecs, lexical_weights):
        results.append({
            "dense": dense.tolist(),
            "sparse": {int(k): float(v) for k, v in sparse.items()},
        })

    logger.debug("BGE-M3 encoded %d texts", len(texts))
    return results


@with_retry("single_text_embedding")
async def embed_text(text: str) -> dict[str, Any]:
    """Convenience wrapper to embed a single text."""
    results = await embed_texts([text])
    return results[0]
