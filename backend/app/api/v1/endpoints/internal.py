"""Internal endpoints for the dedicated processing worker (Phase 3).

Cloud Tasks delivers one HTTP task per uploaded file to ``/v1/internal/process-file``
on the worker service. The worker runs with concurrency=1 and CPU always allocated,
so each instance processes a single file at full speed; Cloud Tasks handles retries.

The endpoint is guarded by a shared secret (``PROCESSING_SECRET``) sent as the
``X-Processing-Secret`` header. It is mounted on every service but only ever called
on the worker; on the public API it simply rejects anything without the secret.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Header, HTTPException, Request

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/process-file")
async def process_file_endpoint(
    request: Request,
    x_processing_secret: str | None = Header(default=None),
):
    if not settings.processing_secret or x_processing_secret != settings.processing_secret:
        raise HTTPException(status_code=403, detail="forbidden")

    payload = await request.json()
    file_id = payload.get("file_id")
    if not file_id:
        raise HTTPException(status_code=400, detail="file_id is required")
    trace_run_id = payload.get("trace_run_id")
    source = payload.get("source") or "upload"

    from app.services.processing_v3.orchestrator import process_file

    logger.info("[internal] processing file %s (source=%s)", file_id, source)
    # Run to completion: Cloud Tasks waits for the response and retries on non-2xx.
    await process_file(file_id, trace_run_id, source)
    return {"status": "ok", "file_id": file_id}
