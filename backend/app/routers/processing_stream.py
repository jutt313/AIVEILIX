"""
Processing Stream Router
SSE endpoint that streams live AI commentary during file processing.
No DB polling - pure in-memory queue broadcast.
"""

import asyncio
import json
import logging
import base64
import time as _time
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.services.supabase import get_supabase, get_supabase_auth
from app.services.processing_commentary import get_or_create_queue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/buckets", tags=["processing-stream"])


async def _get_user_from_token(token: str) -> str:
    """Decode JWT locally (fast path) — same logic as get_current_user_id."""
    try:
        parts = token.split(".")
        if len(parts) == 3:
            payload_b64 = parts[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            import json as _json
            payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
            user_id = payload.get("sub")
            exp = payload.get("exp", 0)
            if user_id and exp > _time.time():
                return str(user_id)
            elif exp <= _time.time():
                raise HTTPException(status_code=401, detail="Token expired")
    except HTTPException:
        raise
    except Exception:
        pass

    # Fallback: verify with Supabase
    try:
        supabase_auth = get_supabase_auth()
        user = supabase_auth.auth.get_user(token)
        if not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return str(user.user.id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


async def _verify_bucket_access(bucket_id: str, user_id: str):
    """Quick ownership check — one DB call, no RLS bypass needed."""
    try:
        supabase = get_supabase()
        from app.services.team_service import get_effective_user_id
        effective_uid = get_effective_user_id(supabase, user_id, bucket_id)
        result = (
            supabase.table("buckets")
            .select("id")
            .eq("id", bucket_id)
            .eq("user_id", effective_uid)
            .limit(1)
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Bucket access check failed: {e}")
        raise HTTPException(status_code=403, detail="Access denied")


async def _stream_commentary(bucket_id: str, file_id: Optional[str]) -> AsyncGenerator[str, None]:
    """Async generator that yields SSE-formatted messages from the broadcast queue."""
    queue = get_or_create_queue(bucket_id)

    # Send a heartbeat immediately so the connection is confirmed
    yield "data: {\"type\": \"connected\"}\n\n"

    try:
        while True:
            try:
                # Wait up to 30s for next message (heartbeat if nothing comes)
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)

                # Filter to the requested file if specified
                if file_id and msg.get("file_id") and msg["file_id"] != file_id:
                    continue

                payload = json.dumps(msg)
                yield f"data: {payload}\n\n"

                # Close stream when file is done
                if msg.get("type") in ("complete", "error"):
                    break

            except asyncio.TimeoutError:
                # Keep-alive heartbeat every 30s
                yield "data: {\"type\": \"heartbeat\"}\n\n"

    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.debug(f"SSE stream ended: {e}")
    finally:
        # Clean up queue only if no more files processing in this bucket
        # (leave queue alive - another file may start soon)
        pass


@router.get("/{bucket_id}/processing-stream")
async def stream_processing_commentary(
    bucket_id: str,
    token: str = Query(..., description="Bearer token (EventSource cannot set headers)"),
    file_id: Optional[str] = None,
):
    """
    SSE stream for live AI commentary during file processing.
    Frontend connects once per upload — receives text updates then auto-closes.
    Token passed as query param because EventSource API cannot set headers.
    """
    user_id = await _get_user_from_token(token)
    await _verify_bucket_access(bucket_id, user_id)

    return StreamingResponse(
        _stream_commentary(bucket_id, file_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
