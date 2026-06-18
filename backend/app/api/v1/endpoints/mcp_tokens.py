"""
MCP Token Management — CRUD endpoints for bucket MCP tokens.

Endpoints:
  GET    /buckets/{bucket_id}/mcp-tokens              list all tokens
  POST   /buckets/{bucket_id}/mcp-tokens              create token (max 10)
  PATCH  /buckets/{bucket_id}/mcp-tokens/{token_id}  update name/tools/origins
  DELETE /buckets/{bucket_id}/mcp-tokens/{token_id}  revoke token
  GET    /buckets/{bucket_id}/mcp-tokens/{token_id}/logs  access logs
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_context
from app.database import get_db
from app.models.bucket import Bucket
from app.models.mcp_token import BucketMcpToken, McpAccessLog
from app.services.team.permissions import UserContext, require_owner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/buckets", tags=["mcp-tokens"])

MAX_TOKENS_PER_BUCKET = 10

ALL_TOOLS = [
    "search",
    "query",
    "list_files",
    "get_file",
    "get_file_summary",
    "list_categories",
    "get_bucket_info",
    "list_members",
    "get_file_layout",
    "get_chunk",
    "list_chunks",
    "get_file_stats",
    "get_section",
    "get_pages",
    "list_visuals",
    "get_visual",
]

TOOL_DESCRIPTIONS = {
    "search": "Semantic search — returns grounded source chunks with citations (recommended: let the connected AI answer from these)",
    "query": "Server-generated answer with sources (optional — uses an internal LLM; best for clients without their own AI)",
    "list_files": "List all files in the bucket with metadata",
    "get_file": "Get full file spread — metadata, summary, chunks and images",
    "get_file_summary": "Get the AI-generated summary for a specific file",
    "list_categories": "List all categories in the bucket with file counts",
    "get_bucket_info": "Get bucket name, description and storage statistics",
    "list_members": "List who can access the bucket — owner + team members and their permissions (names only, no emails)",
    "get_file_layout": "Get the full Layout JSON map of a file across all pages",
    "get_chunk": "Get a specific chunk with its nearby-image metadata",
    "list_chunks": "List all chunks for a specific file",
    "get_file_stats": "Authoritative structural facts: page_count, image_count, section_outline",
    "get_section": "Read a named section by heading — full content, no truncation",
    "get_pages": "Read a contiguous page range — full content, no truncation",
    "list_visuals": "Enumerate every visual element with stable 1-based index",
    "get_visual": "Fetch one visual by 1-based index — page, type, full description, enclosing section",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_bucket_for_user(db: AsyncSession, user_id: str, bucket_id: str) -> Bucket:
    result = await db.execute(
        select(Bucket).where(
            Bucket.id == uuid.UUID(bucket_id),
            Bucket.user_id == uuid.UUID(user_id),
        )
    )
    bucket = result.scalar_one_or_none()
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found.")
    return bucket


async def _get_token(db: AsyncSession, user_id: str, bucket_id: str, token_id: str) -> BucketMcpToken:
    result = await db.execute(
        select(BucketMcpToken).where(
            BucketMcpToken.id == uuid.UUID(token_id),
            BucketMcpToken.bucket_id == uuid.UUID(bucket_id),
            BucketMcpToken.user_id == uuid.UUID(user_id),
        )
    )
    token = result.scalar_one_or_none()
    if token is None:
        raise HTTPException(status_code=404, detail="MCP token not found.")
    return token


def _token_response(token: BucketMcpToken) -> dict:
    from app.services.mcp.account_tools import bucket_mcp_url
    return {
        "id": str(token.id),
        "name": token.name,
        "token": token.token,
        "mcp_url": bucket_mcp_url(token.token),
        "is_active": token.is_active,
        "allowed_tools": token.allowed_tools,
        "allowed_origins": token.allowed_origins,
        "tool_descriptions": TOOL_DESCRIPTIONS,
        "created_at": token.created_at.isoformat(),
        "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
    }


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateTokenRequest(BaseModel):
    name: str = "New Token"
    allowed_tools: list[str] = ALL_TOOLS
    allowed_origins: list[str] = []


class UpdateTokenRequest(BaseModel):
    name: str | None = None
    allowed_tools: list[str] | None = None
    allowed_origins: list[str] | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{bucket_id}/mcp-tokens")
async def list_mcp_tokens(
    bucket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    await _get_bucket_for_user(db, str(current_user["user_id"]), bucket_id)
    result = await db.execute(
        select(BucketMcpToken)
        .where(
            BucketMcpToken.bucket_id == uuid.UUID(bucket_id),
            BucketMcpToken.user_id == uuid.UUID(str(current_user["user_id"])),
        )
        .order_by(BucketMcpToken.created_at.asc())
    )
    tokens = result.scalars().all()
    return {
        "tokens": [_token_response(t) for t in tokens],
        "total": len(tokens),
        "max": MAX_TOKENS_PER_BUCKET,
        "tool_descriptions": TOOL_DESCRIPTIONS,
    }


@router.post("/{bucket_id}/mcp-tokens")
async def create_mcp_token(
    bucket_id: str,
    body: CreateTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    await _get_bucket_for_user(db, str(current_user["user_id"]), bucket_id)

    # Enforce max 10
    count_result = await db.execute(
        select(func.count()).where(
            BucketMcpToken.bucket_id == uuid.UUID(bucket_id),
            BucketMcpToken.user_id == uuid.UUID(str(current_user["user_id"])),
        )
    )
    count = count_result.scalar_one()
    if count >= MAX_TOKENS_PER_BUCKET:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_TOKENS_PER_BUCKET} MCP tokens per bucket.")

    # Validate tools
    invalid = [t for t in body.allowed_tools if t not in ALL_TOOLS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unknown tools: {invalid}")

    token = BucketMcpToken(
        bucket_id=uuid.UUID(bucket_id),
        user_id=uuid.UUID(str(current_user["user_id"])),
        name=body.name.strip() or "New Token",
        allowed_tools=body.allowed_tools,
        allowed_origins=body.allowed_origins,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    logger.info("MCP token created: bucket=%s token=%s", bucket_id, token.id)
    return _token_response(token)


@router.patch("/{bucket_id}/mcp-tokens/{token_id}")
async def update_mcp_token(
    bucket_id: str,
    token_id: str,
    body: UpdateTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    token = await _get_token(db, str(current_user["user_id"]), bucket_id, token_id)

    if body.name is not None:
        token.name = body.name.strip() or token.name
    if body.allowed_tools is not None:
        invalid = [t for t in body.allowed_tools if t not in ALL_TOOLS]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Unknown tools: {invalid}")
        token.allowed_tools = body.allowed_tools
    if body.allowed_origins is not None:
        token.allowed_origins = body.allowed_origins

    await db.commit()
    await db.refresh(token)
    logger.info("MCP token updated: token=%s", token_id)
    return _token_response(token)


@router.delete("/{bucket_id}/mcp-tokens/{token_id}")
async def revoke_mcp_token(
    bucket_id: str,
    token_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    token = await _get_token(db, str(current_user["user_id"]), bucket_id, token_id)
    token.is_active = False
    await db.commit()
    logger.info("MCP token revoked: token=%s", token_id)
    return {"message": "Token revoked.", "token_id": token_id}


@router.get("/{bucket_id}/mcp-tokens/{token_id}/logs")
async def get_token_logs(
    bucket_id: str,
    token_id: str,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    token = await _get_token(db, str(current_user["user_id"]), bucket_id, token_id)

    result = await db.execute(
        select(McpAccessLog)
        .where(McpAccessLog.token_id == token.id)
        .order_by(McpAccessLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()

    count_result = await db.execute(
        select(func.count()).where(McpAccessLog.token_id == token.id)
    )
    total = count_result.scalar_one()

    return {
        "token_id": token_id,
        "token_name": token.name,
        "logs": [
            {
                "id": str(log.id),
                "tool": log.tool,
                "status": log.status,
                "status_code": log.status_code,
                "error_message": log.error_message,
                "origin": log.origin,
                "ip_address": log.ip_address,
                "duration_ms": log.duration_ms,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
