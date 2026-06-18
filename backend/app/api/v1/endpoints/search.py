import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.database import get_db
from app.schemas.agent import (
    BucketQueryRequest,
    BucketQueryResponse,
    BucketSearchRequest,
    BucketSearchResponse,
)
from app.services.agent.retrieval import search_bucket_documents
from app.services.agent.service import answer_bucket_query, get_bucket_for_user

router = APIRouter(prefix="/buckets", tags=["search"])


@router.post("/{bucket_id}/search", response_model=BucketSearchResponse)
async def search_bucket(
    bucket_id: str,
    body: BucketSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await get_bucket_for_user(db, str(current_user["user_id"]), bucket_id)
    results = await search_bucket_documents(db, uuid.UUID(bucket_id), body.query, limit=body.top_k)
    return {
        "results": [
            {
                "chunk_id": item.chunk_id,
                "file_id": item.file_id,
                "file_name": item.file_name,
                "page": item.page,
                "content": item.content,
                "score": item.score,
            }
            for item in results
        ],
        "total": len(results),
    }


@router.post("/{bucket_id}/query", response_model=BucketQueryResponse)
async def query_bucket(
    bucket_id: str,
    body: BucketQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await answer_bucket_query(
        db,
        user_id=str(current_user["user_id"]),
        bucket_id=bucket_id,
        question=body.question,
        conversation_id=str(body.conversation_id) if body.conversation_id else None,
    )
