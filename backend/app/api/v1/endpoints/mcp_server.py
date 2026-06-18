"""
MCP protocol server — JSON-RPC 2.0 over Streamable HTTP.

Two endpoints, one per MCP URL type:
  POST /mcp/bucket/{token}    — bucket-scoped, 10 tools
  POST /mcp/account/{token}   — account-scoped, 5 tools

Implements the MCP methods Claude (and any MCP client) needs:
  initialize · notifications/initialized · tools/list · tools/call · ping

Auth: bucket token -> BucketMcpToken; account token -> AccountMcpToken.
Tool errors are returned as JSON-RPC results with isError=true (per MCP spec);
protocol errors use JSON-RPC error objects.
"""

from __future__ import annotations

import datetime
import decimal
import json
import logging
import time
import uuid as _uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.database import db_session
from app.models.mcp_token import AccountMcpToken, BucketMcpToken, McpAccessLog
from app.services.mcp.registry import (
    ACCOUNT_TOOLS,
    BUCKET_TOOLS,
    account_tool_definitions,
    bucket_tool_definitions,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp-server"])

SERVER_INFO = {"name": "AIveilix MCP", "version": "1.0.0"}
DEFAULT_PROTOCOL = "2025-06-18"
SUPPORTED_PROTOCOLS = {"2025-06-18", "2025-03-26", "2024-11-05"}


# ── JSON-RPC envelope helpers ─────────────────────────────────────────────────

def _result(msg_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _json_default(obj):
    """Convert DB-native types into JSON-safe values."""
    if isinstance(obj, decimal.Decimal):
        return int(obj) if obj == obj.to_integral_value() else float(obj)
    if isinstance(obj, _uuid.UUID):
        return str(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    return str(obj)


def _sanitize(data):
    """Round-trip through JSON so the payload is fully serializable downstream."""
    return json.loads(json.dumps(data, default=_json_default))


def _tool_ok(data) -> dict:
    safe = _sanitize(data)
    return {
        "content": [{"type": "text", "text": json.dumps(safe)}],
        "structuredContent": safe if isinstance(safe, dict) else {"value": safe},
        "isError": False,
    }


def _tool_err(message: str) -> dict:
    return {"content": [{"type": "text", "text": message}], "isError": True}


# ── access logging (bucket tokens only) ───────────────────────────────────────

def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _log_call(
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
    db.add(McpAccessLog(
        token_id=token.id,
        bucket_id=token.bucket_id,
        tool=tool,
        status=status,
        status_code=status_code,
        error_message=error_message,
        origin=request.headers.get("origin") or request.headers.get("referer"),
        ip_address=_client_ip(request),
        duration_ms=duration_ms,
    ))
    token.last_used_at = func.now()
    try:
        await db.commit()
    except Exception:
        await db.rollback()


# ── core JSON-RPC message handler ─────────────────────────────────────────────

async def _check_mcp_rate(db: AsyncSession, owner_id) -> str | None:
    """Per-minute MCP rate limit for the owner's plan. Returns an error message if over, else None."""
    if owner_id is None:
        return None
    from app.services.quota import owner_effective_plan
    from app.valkey import get_valkey

    try:
        ep = await owner_effective_plan(db, _uuid.UUID(str(owner_id)))
    except Exception:
        return None  # fail open if the plan can't be resolved
    if ep.locked:
        return "Your AIveilix free trial has ended — choose a plan to keep using MCP."
    limit = ep.limits.mcp_rate_per_min
    window = int(time.time() // 60)
    key = f"mcp_rl:{owner_id}:{window}"
    try:
        v = get_valkey()
        count = await v.incr(key)
        if count == 1:
            await v.expire(key, 65)
    except Exception:
        return None  # fail open on limiter errors
    if count > limit:
        return (
            f"MCP rate limit reached: {limit} requests/min on the {ep.limits.name} plan. "
            "Please slow down and retry shortly."
        )
    return None


async def _handle_message(
    msg: dict,
    *,
    db: AsyncSession,
    request: Request,
    kind: str,                     # "bucket" | "account"
    tool_defs: list[dict],
    tools: dict,                   # name -> registry entry
    allowed: set[str] | None,      # bucket: allowed_tools; account: None (all)
    bucket_token: BucketMcpToken | None,
    account_token=None,            # AccountMcpToken for account scope
    bucket_id=None,
    user_id=None,
) -> dict | None:
    """Returns a JSON-RPC response dict, or None for notifications."""
    method = msg.get("method")
    msg_id = msg.get("id")
    is_notification = "id" not in msg

    if not isinstance(method, str):
        return None if is_notification else _error(msg_id, -32600, "Invalid Request: missing method.")

    if method == "initialize":
        params = msg.get("params") or {}
        proto = params.get("protocolVersion")
        if proto not in SUPPORTED_PROTOCOLS:
            proto = DEFAULT_PROTOCOL
        instructions = (
            f"AIveilix MCP server ({kind} scope). This server exposes processed knowledge "
            "from the user's documents.\n\n"
            "GROUNDING RULES (read first — these are strict):\n"
            "  1. Answer ONLY from what these tools return. Never use your own general "
            "knowledge to fill gaps, and never guess.\n"
            "  2. If the tools return no supporting evidence, say plainly: \"That isn't "
            "covered in the document(s).\" Do not invent an answer.\n"
            "  3. ABSENCE CHECK — before concluding something is NOT present (e.g. \"is "
            "Japanese mentioned?\"), run `search` at least twice: once for the exact term "
            "and once for a synonym/related term. Only answer \"not found\" if both miss.\n"
            "  4. COUNTS & STRUCTURE — for \"how many images / pages / sections / visuals / "
            "chunks\" or \"list every …\", you MUST use the exact tools (`get_file_stats`, "
            "`list_visuals`, `get_file_layout`, `list_chunks`). NEVER answer counts from "
            "`search` or `query` — semantic retrieval caps results and undercounts.\n\n"
            "HOW TO USE — pick the right tool for the job:\n"
            "  • To ANSWER a question: call `search` to pull the most relevant grounded "
            "chunks (with citations), then compose the answer YOURSELF from those chunks. "
            "This is the required path — fastest, grounded, no second model in the loop.\n"
            "  • `query` is an OPTIONAL fallback that makes the SERVER synthesize a cited "
            "answer with an internal LLM — use it only for thin/non-AI clients or when you "
            "cannot compose the answer yourself (it adds latency and a second model that can err).\n"
            "  • To READ a specific file's full content → `get_file` with the file_id.\n"
            "  • To LIST what's available → `list_files` or `get_bucket_info`.\n\n"
            "IMPORTANT — do NOT rely on `get_file_summary` alone. The summary is a short "
            "high-level overview only and may omit details. To actually read a file, call "
            "`get_file` (full content) or `search` (grounded chunks across the bucket). "
            "When in doubt, prefer `search` or `get_file` over the summary."
        )
        return _result(msg_id, {
            "protocolVersion": proto,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": instructions,
        })

    if method in ("notifications/initialized", "initialized"):
        return None

    if method.startswith("notifications/"):
        return None

    if method == "ping":
        return _result(msg_id, {})

    if method == "tools/list":
        return _result(msg_id, {"tools": tool_defs})

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}

        owner_id = user_id if user_id is not None else getattr(account_token, "user_id", None)
        rate_err = await _check_mcp_rate(db, owner_id)
        if rate_err is not None:
            return _result(msg_id, _tool_err(rate_err))

        if name not in tools:
            return _result(msg_id, _tool_err(f"Unknown tool: '{name}'."))
        if allowed is not None and name not in allowed:
            return _result(msg_id, _tool_err(f"Tool '{name}' is not enabled for this token."))

        handler = tools[name]["handler"]
        start = time.monotonic()
        try:
            if kind == "bucket":
                data = await handler(db, bucket_id, user_id, args)
            else:
                data = await handler(db, account_token, args)
            duration_ms = int((time.monotonic() - start) * 1000)
            if bucket_token is not None:
                await _log_call(db, token=bucket_token, tool=name, status="success",
                                status_code=200, duration_ms=duration_ms, request=request)
            elif account_token is not None:
                account_token.last_used_at = func.now()
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()
            logger.info("[MCP] %s tool=%s ok (%dms)", kind, name, duration_ms)
            return _result(msg_id, _tool_ok(data))
        except Exception as exc:  # noqa: BLE001 — tool errors become isError results
            duration_ms = int((time.monotonic() - start) * 1000)
            detail = getattr(exc, "detail", None) or str(exc)
            if bucket_token is not None:
                await _log_call(db, token=bucket_token, tool=name, status="error",
                                status_code=getattr(exc, "status_code", 500),
                                duration_ms=duration_ms, request=request,
                                error_message=str(detail)[:500])
            logger.warning("[MCP] %s tool=%s error: %s", kind, name, detail)
            return _result(msg_id, _tool_err(f"Tool '{name}' failed: {detail}"))

    return None if is_notification else _error(msg_id, -32601, f"Method not found: {method}")


async def _process_request(
    request: Request,
    *,
    kind: str,
    tool_defs: list[dict],
    tools: dict,
    allowed: set[str] | None,
    bucket_token: BucketMcpToken | None,
    db: AsyncSession,
    account_token=None,
    bucket_id=None,
    user_id=None,
) -> Response:
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content=_error(None, -32700, "Parse error: invalid JSON."))

    messages = body if isinstance(body, list) else [body]
    responses = []
    for msg in messages:
        if not isinstance(msg, dict):
            responses.append(_error(None, -32600, "Invalid Request."))
            continue
        resp = await _handle_message(
            msg, db=db, request=request, kind=kind, tool_defs=tool_defs,
            tools=tools, allowed=allowed, bucket_token=bucket_token,
            account_token=account_token, bucket_id=bucket_id, user_id=user_id,
        )
        if resp is not None:
            responses.append(resp)

    if not responses:
        # All messages were notifications — Streamable HTTP expects 202 Accepted.
        return Response(status_code=202)

    payload = responses if isinstance(body, list) else responses[0]
    return JSONResponse(status_code=200, content=payload)


# ── bucket endpoint ───────────────────────────────────────────────────────────

@router.post("/bucket/{token}")
async def mcp_bucket_endpoint(token: str, request: Request):
    async with db_session() as db:
        result = await db.execute(
            select(BucketMcpToken).where(BucketMcpToken.token == token)
        )
        mcp_token = result.scalar_one_or_none()
        if mcp_token is None or not mcp_token.is_active:
            return JSONResponse(status_code=401, content=_error(None, -32001, "Invalid or revoked MCP token."))

        allowed = set(mcp_token.allowed_tools or [])
        return await _process_request(
            request,
            kind="bucket",
            tool_defs=bucket_tool_definitions(list(allowed)),
            tools=BUCKET_TOOLS,
            allowed=allowed,
            bucket_token=mcp_token,
            bucket_id=mcp_token.bucket_id,
            user_id=mcp_token.user_id,
            db=db,
        )


# ── account endpoint ──────────────────────────────────────────────────────────

@router.post("/account/{token}")
async def mcp_account_endpoint(token: str, request: Request):
    async with db_session() as db:
        result = await db.execute(
            select(AccountMcpToken).where(AccountMcpToken.token == token)
        )
        account_token = result.scalar_one_or_none()
        if account_token is None or not account_token.is_active:
            return JSONResponse(status_code=401, content=_error(None, -32001, "Invalid or revoked account MCP token."))

        return await _process_request(
            request,
            kind="account",
            tool_defs=account_tool_definitions(),
            tools=ACCOUNT_TOOLS,
            allowed=None,
            bucket_token=None,
            account_token=account_token,
            user_id=account_token.user_id,
            db=db,
        )


# ── GET / DELETE (Streamable HTTP transport niceties) ─────────────────────────

@router.get("/bucket/{token}")
@router.get("/account/{token}")
async def mcp_get(token: str):
    # Server-initiated SSE streams are not used — clients must POST.
    return JSONResponse(
        status_code=405,
        content=_error(None, -32000, "This MCP endpoint accepts POST requests only."),
        headers={"Allow": "POST"},
    )


@router.delete("/bucket/{token}")
@router.delete("/account/{token}")
async def mcp_delete(token: str):
    # Stateless server — nothing to tear down.
    return Response(status_code=200)
