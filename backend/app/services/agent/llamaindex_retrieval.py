from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.qdrant_client import get_async_qdrant_client
from app.services.qdrant.file_indexer import TEXT_COLLECTION

logger = logging.getLogger(__name__)


def llamaindex_available() -> bool:
    try:
        import llama_index.core  # noqa: F401
        import llama_index.vector_stores.qdrant  # noqa: F401
        return True
    except Exception:
        return False


def _get_vector_store():
    from llama_index.vector_stores.qdrant import QdrantVectorStore

    return QdrantVectorStore(
        collection_name=TEXT_COLLECTION,
        aclient=get_async_qdrant_client(),
        text_key="content",
        dense_vector_name="",
    )


async def search_bucket_documents_with_llamaindex(
    db: AsyncSession,
    *,
    bucket_id: uuid.UUID,
    query: str,
    query_embedding: list[float],
    limit: int,
    candidate_limit: int,
    resolve_file_names,
    retrieved_chunk_cls,
) -> list:
    from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
    from llama_index.core.vector_stores.types import VectorStoreQuery
    from llama_index.core.vector_stores.types import VectorStoreQueryMode

    vector_store = _get_vector_store()
    query_result = await vector_store.aquery(
        query=VectorStoreQuery(
            query_embedding=query_embedding,
            query_str=query,
            similarity_top_k=max(limit, candidate_limit),
            mode=VectorStoreQueryMode.DEFAULT,
            filters=MetadataFilters(
                filters=[
                    MetadataFilter(key="bucket_id", value=str(bucket_id)),
                    MetadataFilter(key="status", value="active"),
                ]
            ),
        )
    )

    nodes = query_result.nodes or []
    similarities = query_result.similarities or []
    ids = query_result.ids or []
    if not nodes:
        return []

    file_ids: set[uuid.UUID] = set()
    for node in nodes:
        file_id = (node.metadata or {}).get("file_id")
        if file_id:
            try:
                file_ids.add(uuid.UUID(str(file_id)))
            except Exception:
                continue

    file_names = await resolve_file_names(db, file_ids)

    results: list = []
    for idx, node in enumerate(nodes):
        metadata = node.metadata or {}
        file_id_raw = metadata.get("file_id")
        if not file_id_raw:
            continue
        try:
            file_id = uuid.UUID(str(file_id_raw))
        except Exception:
            continue
        file_name = file_names.get(file_id)
        if file_name is None:
            continue

        node_id = ids[idx] if idx < len(ids) and ids[idx] else node.node_id
        score = similarities[idx] if idx < len(similarities) else 0.0
        results.append(
            retrieved_chunk_cls(
                chunk_id=uuid.UUID(str(node_id)),
                file_id=file_id,
                file_name=file_name,
                page=int(metadata.get("page") or 0),
                content=node.get_content().strip(),
                score=float(score or 0.0),
                block_id=str(metadata.get("block_id") or ""),
                is_summary=bool(metadata.get("is_summary", False)),
            )
        )
        if len(results) >= limit:
            break

    logger.info(
        "LlamaIndex retrieval returned %d bucket chunks for bucket %s",
        len(results),
        bucket_id,
    )
    return results
