"""
MCP Tool Endpoints — the 6 tools exposed to external AI agents via bucket token.

Auth flow per request:
  1. Extract token from URL path
  2. Look up BucketMcpToken → must be is_active=True
  3. Check requested tool is in token.allowed_tools
  4. Check Origin header against token.allowed_origins (empty = allow all)
  5. Run tool
  6. Write McpAccessLog with status, duration, origin, ip

Tools:
  POST /mcp/bucket/{token}/search        — semantic search
  POST /mcp/bucket/{token}/query         — full AI Q&A
  GET  /mcp/bucket/{token}/files         — list files
  GET  /mcp/bucket/{token}/file/{file_id}           — full file spread
  GET  /mcp/bucket/{token}/file/{file_id}/layout    — page layout blocks
  GET  /mcp/bucket/{token}/info          — bucket info
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_session
from app.models.mcp_token import BucketMcpToken, McpAccessLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp/bucket", tags=["mcp-tools"])


# ── Auth helper ───────────────────────────────────────────────────────────────

async def _auth(
    db: AsyncSession,
    raw_token: str,
    tool: str,
    request: Request,
) -> BucketMcpToken:
    """
    Validates token, checks tool permission, checks origin.
    Raises HTTPException on any failure — caller logs it.
    """
    result = await db.execute(
        select(BucketMcpToken).where(BucketMcpToken.token == raw_token)
    )
    token = result.scalar_one_or_none()

    if token is None or not token.is_active:
        raise HTTPException(status_code=401, detail="Invalid or revoked MCP token.")

    if tool not in token.allowed_tools:
        raise HTTPException(status_code=403, detail=f"Tool '{tool}' is not enabled for this token.")

    # Origin check — empty list = allow all
    if token.allowed_origins:
        origin = request.headers.get("origin") or request.headers.get("referer") or ""
        allowed = any(origin.startswith(o) for o in token.allowed_origins)
        if not allowed:
            raise HTTPException(status_code=403, detail="Origin not allowed for this token.")

    return token


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _log(
    db: AsyncSession,
    *,
    token: BucketMcpToken,
    tool: str,
    status: str,
    status_code: int,
    duration_ms: int,
    request: Request,
    error_message: str | None = None,
) -> None:
    origin = request.headers.get("origin") or request.headers.get("referer")
    log = McpAccessLog(
        token_id=token.id,
        bucket_id=token.bucket_id,
        tool=tool,
        status=status,
        status_code=status_code,
        error_message=error_message,
        origin=origin,
        ip_address=_get_ip(request),
        duration_ms=duration_ms,
    )
    db.add(log)
    # Update last_used_at on token
    from sqlalchemy.sql import func
    token.last_used_at = func.now()
    try:
        await db.commit()
    except Exception:
        await db.rollback()


async def _run_tool(
    db: AsyncSession,
    raw_token: str,
    tool: str,
    request: Request,
    handler,
):
    """Wraps any tool handler with auth + timing + logging."""
    start = time.monotonic()
    token = None
    try:
        token = await _auth(db, raw_token, tool, request)
        result = await handler(db, token)
        duration_ms = int((time.monotonic() - start) * 1000)
        await _log(db, token=token, tool=tool, status="success", status_code=200, duration_ms=duration_ms, request=request)
        logger.info("[MCP] tool=%s bucket=%s duration=%dms", tool, token.bucket_id, duration_ms)
        return result
    except HTTPException as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        status = "forbidden" if exc.status_code == 403 else "error"
        if token:
            await _log(db, token=token, tool=tool, status=status, status_code=exc.status_code, duration_ms=duration_ms, request=request, error_message=exc.detail)
        logger.warning("[MCP] tool=%s status=%d detail=%s", tool, exc.status_code, exc.detail)
        raise
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        if token:
            await _log(db, token=token, tool=tool, status="error", status_code=500, duration_ms=duration_ms, request=request, error_message=str(exc)[:500])
        logger.exception("[MCP] tool=%s unexpected error: %s", tool, exc)
        raise HTTPException(status_code=500, detail="Internal MCP error.")


# ── Schemas ───────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryRequest(BaseModel):
    question: str


# ── 1. search ─────────────────────────────────────────────────────────────────

@router.post("/{token}/search")
async def mcp_search(token: str, body: SearchRequest, request: Request):
    async with db_session() as db:
        async def handler(db, tok):
            from app.services.agent.retrieval import search_bucket_documents
            chunks = await search_bucket_documents(db, tok.bucket_id, body.query, limit=min(body.top_k, 10))
            return {
                "results": [
                    {
                        "chunk_id": str(c.chunk_id),
                        "file_id": str(c.file_id),
                        "file_name": c.file_name,
                        "page": c.page,
                        "content": c.content,
                        "is_summary": c.is_summary,
                        "score": round(c.score, 4),
                    }
                    for c in chunks
                ]
            }
        return await _run_tool(db, token, "search", request, handler)


# ── 2. query ──────────────────────────────────────────────────────────────────

@router.post("/{token}/query")
async def mcp_query(token: str, body: QueryRequest, request: Request):
    async with db_session() as db:
        async def handler(db, tok):
            from app.services.agent.service import answer_bucket_query
            resp = await answer_bucket_query(
                db,
                user_id=str(tok.user_id),
                bucket_id=str(tok.bucket_id),
                question=body.question,
            )
            return {
                "answer": resp.answer,
                "sources": resp.sources,
                "used_web_search": resp.used_web_search,
            }
        return await _run_tool(db, token, "query", request, handler)


# ── 3. list_files ─────────────────────────────────────────────────────────────

@router.get("/{token}/files")
async def mcp_list_files(token: str, request: Request):
    async with db_session() as db:
        async def handler(db, tok):
            from app.services.mcp.tools import fetch_files_list
            files = await fetch_files_list(db, tok.bucket_id)
            return {"files": files, "total": len(files)}
        return await _run_tool(db, token, "list_files", request, handler)


# ── 4. get_file ───────────────────────────────────────────────────────────────

@router.get("/{token}/file/{file_id}")
async def mcp_get_file(token: str, file_id: str, request: Request):
    async with db_session() as db:
        async def handler(db, tok):
            from app.services.mcp.tools import fetch_file_spread
            try:
                fid = uuid.UUID(file_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid file_id.")
            data = await fetch_file_spread(db, tok.bucket_id, fid)
            if data is None:
                raise HTTPException(status_code=404, detail="File not found in this bucket.")
            return data
        return await _run_tool(db, token, "get_file", request, handler)


# ── 5. get_layout ─────────────────────────────────────────────────────────────

@router.get("/{token}/file/{file_id}/layout")
async def mcp_get_layout(
    token: str,
    file_id: str,
    request: Request,
    page: int = Query(..., ge=1, description="Page number (1-based)"),
):
    async with db_session() as db:
        async def handler(db, tok):
            from app.services.mcp.tools import fetch_page_blocks
            try:
                fid = uuid.UUID(file_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid file_id.")
            data = await fetch_page_blocks(db, tok.bucket_id, fid, page)
            if data is None:
                raise HTTPException(status_code=404, detail="File not found in this bucket.")
            return data
        return await _run_tool(db, token, "get_layout", request, handler)


# ── 6. get_bucket_info ────────────────────────────────────────────────────────

@router.get("/{token}/info")
async def mcp_bucket_info(token: str, request: Request):
    async with db_session() as db:
        async def handler(db, tok):
            from app.services.mcp.tools import fetch_bucket_info
            data = await fetch_bucket_info(db, tok.bucket_id)
            if data is None:
                raise HTTPException(status_code=404, detail="Bucket not found.")
            return data
        return await _run_tool(db, token, "get_bucket_info", request, handler)
