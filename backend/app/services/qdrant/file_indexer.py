"""
Qdrant file indexer.

Writes text_chunks and image_chunks to the existing Qdrant collections.
Uses the shared async client from app.qdrant_client.

Collection schema (must match bootstrap_collections.py exactly):
  text_chunks:
    - single unnamed dense vector, 1024-dim, COSINE
    - sparse named "text_sparse"
    - payload indexes: file_id, bucket_id, page, status, nearby_image_id

  image_chunks:
    - single unnamed dense vector, 512-dim, COSINE
    - payload indexes: file_id, bucket_id, page, image_id, nearby_text_id, status
"""

import logging
import uuid
from typing import Any

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    UpdateStatus,
    VectorParams,
)

from app.qdrant_client import get_async_qdrant_client
from app.services.pipeline.retry import with_retry

logger = logging.getLogger(__name__)

TEXT_COLLECTION = "text_chunks"
TEXT_COLLECTION_LITE = "text_chunks_lite"
IMAGE_COLLECTION = "image_chunks"

TEXT_DENSE_DIM = 1024   # voyage-3-large
TEXT_LITE_DIM = 512     # voyage-3-lite
IMAGE_DENSE_DIM = 512   # CLIP ViT-B-32


_TEXT_PAYLOAD_INDEXES: list[tuple[str, PayloadSchemaType]] = [
    ("file_id",        PayloadSchemaType.KEYWORD),
    ("bucket_id",      PayloadSchemaType.KEYWORD),
    ("page",           PayloadSchemaType.INTEGER),
    ("status",         PayloadSchemaType.KEYWORD),
    ("nearby_image_id", PayloadSchemaType.KEYWORD),
    ("chunk_index",    PayloadSchemaType.INTEGER),
]

_IMAGE_PAYLOAD_INDEXES: list[tuple[str, PayloadSchemaType]] = [
    ("file_id",       PayloadSchemaType.KEYWORD),
    ("bucket_id",     PayloadSchemaType.KEYWORD),
    ("page",          PayloadSchemaType.INTEGER),
    ("image_id",      PayloadSchemaType.KEYWORD),
    ("nearby_text_id", PayloadSchemaType.KEYWORD),
    ("status",        PayloadSchemaType.KEYWORD),
]


async def ensure_collections() -> None:
    """
    Ensure text_chunks and image_chunks collections exist with the exact same config
    as bootstrap_collections.py — including payload indexes.

    Safe to call on every startup:
    - Skips collection creation if already present.
    - Always attempts payload index creation; silently ignores duplicates
      (same behaviour as the bootstrap script).
    """
    client = get_async_qdrant_client()
    existing = {c.name for c in (await client.get_collections()).collections}

    if TEXT_COLLECTION not in existing:
        await client.create_collection(
            collection_name=TEXT_COLLECTION,
            vectors_config=VectorParams(size=TEXT_DENSE_DIM, distance=Distance.COSINE),
            sparse_vectors_config={
                "text_sparse": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            },
        )
        logger.info("Created Qdrant collection: %s", TEXT_COLLECTION)

    if TEXT_COLLECTION_LITE not in existing:
        await client.create_collection(
            collection_name=TEXT_COLLECTION_LITE,
            vectors_config=VectorParams(size=TEXT_LITE_DIM, distance=Distance.COSINE),
            sparse_vectors_config={
                "text_sparse": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            },
        )
        logger.info("Created Qdrant collection: %s", TEXT_COLLECTION_LITE)

    if IMAGE_COLLECTION not in existing:
        await client.create_collection(
            collection_name=IMAGE_COLLECTION,
            vectors_config=VectorParams(size=IMAGE_DENSE_DIM, distance=Distance.COSINE),
        )
        logger.info("Created Qdrant collection: %s", IMAGE_COLLECTION)

    # Always ensure payload indexes exist — idempotent, duplicates silently ignored
    await _ensure_payload_indexes(client, TEXT_COLLECTION, _TEXT_PAYLOAD_INDEXES)
    await _ensure_payload_indexes(client, TEXT_COLLECTION_LITE, _TEXT_PAYLOAD_INDEXES)
    await _ensure_payload_indexes(client, IMAGE_COLLECTION, _IMAGE_PAYLOAD_INDEXES)


async def _ensure_payload_indexes(
    client,
    collection_name: str,
    indexes: list[tuple[str, PayloadSchemaType]],
) -> None:
    for field_name, schema in indexes:
        try:
            await client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=schema,
                wait=True,
            )
        except Exception:
            # Qdrant rejects duplicate indexes — that is fine for idempotent startup.
            pass
    logger.debug("Payload indexes ensured for collection: %s", collection_name)


@with_retry("qdrant_text_upsert")
async def upsert_text_chunks(
    chunks_with_embeddings: list[dict[str, Any]],
    collection_name: str = TEXT_COLLECTION,
) -> None:
    """
    chunks_with_embeddings: list of dicts:
        {
          "id": str (UUID),
          "file_id": str,
          "bucket_id": str,
          "page": int,
          "content": str,
          "block_id": str,
          "is_summary": bool,
          "nearby_image_id": str | None,
          "image_description": str,
          "image_text_inside": str,
          "dense": list[float],          # 1024-dim from BGE-M3
          "sparse": dict[int, float],    # lexical weights from BGE-M3
          "status": "active" | "deprecated"
        }
    """
    client = get_async_qdrant_client()
    points: list[PointStruct] = []

    for c in chunks_with_embeddings:
        sparse = c.get("sparse")
        if sparse:
            sparse_indices = [int(k) for k in sparse.keys()]
            sparse_values = [float(v) for v in sparse.values()]
            sparse_vec: SparseVector | None = SparseVector(
                indices=sparse_indices,
                values=sparse_values,
            )
        else:
            sparse_vec = None

        # Build vector dict — include sparse only if available
        vector_dict: dict = {"": c["dense"]}
        if sparse_vec is not None:
            vector_dict["text_sparse"] = sparse_vec

        point = PointStruct(
            id=str(c["id"]),
            vector=vector_dict,
            payload={
                "file_id": str(c["file_id"]),
                "bucket_id": str(c["bucket_id"]),
                "page": c["page"],
                "content": c["content"],
                "block_id": c.get("block_id"),
                "is_summary": bool(c.get("is_summary", False)),
                "nearby_image_id": c.get("nearby_image_id"),
                "image_description": c.get("image_description", ""),
                "image_text_inside": c.get("image_text_inside", ""),
                "chunk_index": int(c.get("chunk_index", -1)),
                "status": c.get("status", "active"),
            },
        )
        points.append(point)

    result = await client.upsert(collection_name=collection_name, points=points, wait=True)
    if result.status != UpdateStatus.COMPLETED:
        raise RuntimeError(f"Qdrant text upsert returned status: {result.status}")
    logger.info("Qdrant: upserted %d text chunks into %s", len(points), collection_name)


@with_retry("qdrant_image_upsert")
async def upsert_image_chunks(image_chunks: list[dict[str, Any]]) -> None:
    """
    image_chunks: list of dicts:
        {
          "id": str (UUID),
          "file_id": str,
          "bucket_id": str,
          "page": int,
          "image_id": str,
          "description": str,
          "text_inside": str,
          "nearby_text_id": str | None,
          "dense": list[float],          # 512-dim from CLIP
          "status": "active" | "deprecated"
        }
    """
    client = get_async_qdrant_client()
    points: list[PointStruct] = []

    for img in image_chunks:
        # Single unnamed dense vector → pass as plain list
        point = PointStruct(
            id=str(img["id"]),
            vector=img["dense"],   # unnamed: bare list, not a dict
            payload={
                "file_id": str(img["file_id"]),
                "bucket_id": str(img["bucket_id"]),
                "page": img["page"],
                "image_id": img["image_id"],
                "description": img.get("description", ""),
                "text_inside": img.get("text_inside", ""),
                "nearby_text_id": img.get("nearby_text_id"),
                "status": img.get("status", "active"),
            },
        )
        points.append(point)

    result = await client.upsert(collection_name=IMAGE_COLLECTION, points=points, wait=True)
    if result.status != UpdateStatus.COMPLETED:
        raise RuntimeError(f"Qdrant image upsert returned status: {result.status}")
    logger.info("Qdrant: upserted %d image chunks", len(points))


async def deprecate_file_vectors(
    file_id: str,
    collections: list[str] | None = None,
) -> None:
    """Mark all existing vectors for a file as deprecated before reprocessing.

    Pass ``collections`` to scope the deprecation (e.g. only the lite text
    collection). Defaults to every text + image collection so a reprocess
    catches vectors regardless of which tier produced them originally.
    """
    client = get_async_qdrant_client()
    file_filter = Filter(
        must=[FieldCondition(key="file_id", match=MatchValue(value=str(file_id)))]
    )
    targets = collections or [TEXT_COLLECTION, TEXT_COLLECTION_LITE, IMAGE_COLLECTION]
    for collection in targets:
        try:
            await client.set_payload(
                collection_name=collection,
                payload={"status": "deprecated"},
                points=file_filter,
            )
        except Exception as exc:
            # Collection may not exist yet on a fresh deployment — that's fine.
            logger.debug("Skipping deprecate on %s: %s", collection, exc)
    logger.info("Deprecated Qdrant vectors for file %s", file_id)
