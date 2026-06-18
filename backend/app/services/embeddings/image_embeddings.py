"""
Image embedding service using CLIP (open-clip-torch).

Produces:
- vector: list[float] — 512 dimensions (ViT-B-32)
"""

import io
import logging
from typing import Any

from app.services.pipeline.retry import with_retry

logger = logging.getLogger(__name__)

_model = None
_preprocess = None
_tokenizer = None


def _get_model():
    global _model, _preprocess, _tokenizer
    if _model is None:
        import open_clip
        import torch
        logger.info("Loading CLIP model (ViT-B-32)...")
        _model, _, _preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        _model.eval()
        logger.info("CLIP model loaded.")
    return _model, _preprocess


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        import open_clip
        _tokenizer = open_clip.get_tokenizer("ViT-B-32")
    return _tokenizer


@with_retry("image_embedding")
async def embed_images(images: list[bytes]) -> list[list[float]]:
    """
    Embed a list of raw image byte strings (PNG/JPEG).
    Returns a list of 512-dim float vectors.
    Order matches input list.
    """
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(None, _embed_sync, images)


def _embed_sync(images: list[bytes]) -> list[list[float]]:
    import torch
    from PIL import Image

    model, preprocess = _get_model()

    tensors = []
    for img_bytes in images:
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        tensors.append(preprocess(pil_img))

    batch = torch.stack(tensors)
    with torch.no_grad():
        features = model.encode_image(batch)
        features = features / features.norm(dim=-1, keepdim=True)  # normalise

    logger.debug("CLIP encoded %d images", len(images))
    return features.cpu().tolist()


@with_retry("single_image_embedding")
async def embed_image(image_bytes: bytes) -> list[float]:
    """Convenience wrapper to embed a single image."""
    results = await embed_images([image_bytes])
    return results[0]


def _embed_text_sync(text: str) -> list[float]:
    """Embed a text query with CLIP's text encoder (512-dim, same space as image vectors)."""
    import torch
    model, _ = _get_model()
    tokenizer = _get_tokenizer()
    tokens = tokenizer([text])
    with torch.no_grad():
        features = model.encode_text(tokens)
        features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu().squeeze(0).tolist()


@with_retry("text_query_for_image_embedding")
async def embed_query_text_for_images(text: str) -> list[float]:
    """
    Embed a text query with CLIP's text encoder for image similarity search.
    Returns a 512-dim vector in the same space as image embeddings.
    """
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(None, _embed_text_sync, text)
