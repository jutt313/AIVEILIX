"""
Direct-to-R2 upload session endpoints.

The browser uploads raw file bytes straight to Cloudflare R2 using presigned
URLs, so large files never pass through Cloud Run (which caps HTTP/1 request
bodies at 32 MiB). The backend still owns auth, plan/quota checks, the R2 object
key, verification, the DB rows, and the processing pipeline.

POST /v1/buckets/{bucket_id}/uploads/init               — start an upload
POST /v1/buckets/{bucket_id}/uploads/{upload_id}/parts  — presigned multipart part URLs
POST /v1/buckets/{bucket_id}/uploads/{upload_id}/complete — verify + persist + process
POST /v1/buckets/{bucket_id}/uploads/{upload_id}/abort  — cancel + abort R2 multipart
"""

import asyncio
import logging
import math
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_user_context
from app.api.v1.endpoints.files import _require_bucket_for_action
from app.database import get_db
from app.models.file import File
from app.models.upload_session import UploadSession
from app.schemas.files import FileUploadResponse
from app.schemas.uploads import (
    UploadAbortResponse,
    UploadCompleteRequest,
    UploadInitRequest,
    UploadInitResponse,
    UploadPartsRequest,
    UploadPartsResponse,
    UploadPartUrl,
)
from app.services.notifications import create_notification
from app.services.pipeline.upload import finalize_r2_upload
from app.services.quota import enforce_upload_quota
from app.services.storage.r2 import (
    MULTIPART_THRESHOLD_BYTES,
    abort_multipart_upload,
    build_raw_key,
    complete_multipart_upload,
    compute_part_size,
    create_multipart_upload,
    create_presigned_put_url,
    create_presigned_upload_part_url,
    delete_file as r2_delete_file,
    head_object,
    safe_object_filename,
)
from app.services.team.permissions import UserContext
from app.valkey import get_valkey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/buckets", tags=["uploads"])

# Presigned URL lifetimes. Single PUTs finish fast; multipart part URLs are
# requested in batches as the upload progresses, so they get a longer window.
PRESIGN_TTL_SECONDS = 900            # 15 min — single PUT
PART_PRESIGN_TTL_SECONDS = 3600      # 1 h   — multipart part URLs
SESSION_TTL_SECONDS = 24 * 3600      # how long an upload session stays resumable

# Rate-limit how many uploads a single user may start, to bound presigning cost.
_INIT_RATE_LIMIT = 60
_INIT_RATE_WINDOW_SECONDS = 60


async def _rate_limit_init(user_id: uuid.UUID) -> None:
    """Bound upload-init calls per user via Valkey. Fails open if Valkey is down
    so a cache outage can never block uploads."""
    try:
        v = get_valkey()
        key = f"upload:init:{user_id}"
        count = await v.incr(key)
        if count == 1:
            await v.expire(key, _INIT_RATE_WINDOW_SECONDS)
    except Exception:
        return
    if count > _INIT_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many uploads started. Please wait a moment and try again.",
        )


async def _load_session(
    db: AsyncSession, bucket_id: uuid.UUID, session_id: uuid.UUID, ctx: UserContext
) -> UploadSession:
    """Load an upload session and verify it belongs to this bucket + workspace.
    The caller must have already passed ``_require_bucket_for_action``."""
    session = await db.get(UploadSession, session_id)
    if session is None or session.bucket_id != bucket_id:
        raise HTTPException(status_code=404, detail="Upload session not found.")
    if session.user_id != ctx.owner_user_id:
        raise HTTPException(status_code=403, detail="Access denied to this upload session.")
    return session


@router.post(
    "/{bucket_id}/uploads/init",
    response_model=UploadInitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a direct-to-R2 upload",
)
async def init_upload(
    bucket_id: uuid.UUID,
    body: UploadInitRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    owner_id = ctx.owner_user_id

    await _rate_limit_init(ctx.user_id)

    # Enforce plan + quota BEFORE signing anything: per-file size cap, total
    # storage, and document count. Raises HTTP 402 with a clear message.
    await enforce_upload_quota(
        db, owner_id, incoming_files=1, incoming_bytes=body.size, single_file_bytes=body.size
    )

    file_id = uuid.uuid4()
    safe_name = safe_object_filename(body.filename)
    r2_key = build_raw_key(str(file_id), safe_name, version=1)
    content_type = (body.content_type or "application/octet-stream").strip() or "application/octet-stream"
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)

    if body.size >= MULTIPART_THRESHOLD_BYTES:
        mode = "multipart"
        r2_upload_id = await asyncio.to_thread(create_multipart_upload, r2_key, content_type)
        part_size = compute_part_size(body.size)
        part_count = max(1, math.ceil(body.size / part_size))
        single_url = None
        expires_in = PART_PRESIGN_TTL_SECONDS
    else:
        mode = "single"
        r2_upload_id = None
        part_size = None
        part_count = None
        single_url = await asyncio.to_thread(
            create_presigned_put_url, r2_key, content_type, PRESIGN_TTL_SECONDS
        )
        expires_in = PRESIGN_TTL_SECONDS

    session = UploadSession(
        file_id=file_id,
        bucket_id=bucket_id,
        user_id=owner_id,
        filename=safe_name,
        content_type=content_type,
        size=body.size,
        r2_key=r2_key,
        mode=mode,
        r2_upload_id=r2_upload_id,
        status="initiated",
        expires_at=expires_at,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return UploadInitResponse(
        mode=mode,
        upload_id=session.id,
        file_id=file_id,
        r2_key=r2_key,
        expires_in=expires_in,
        url=single_url,
        r2_upload_id=r2_upload_id,
        part_size=part_size,
        part_count=part_count,
    )


@router.post(
    "/{bucket_id}/uploads/{upload_id}/parts",
    response_model=UploadPartsResponse,
    summary="Get presigned URLs for multipart parts",
)
async def get_upload_part_urls(
    bucket_id: uuid.UUID,
    upload_id: uuid.UUID,
    body: UploadPartsRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    session = await _load_session(db, bucket_id, upload_id, ctx)

    if session.mode != "multipart" or not session.r2_upload_id:
        raise HTTPException(status_code=400, detail="This upload is not a multipart upload.")
    if session.status not in ("initiated", "uploaded"):
        raise HTTPException(status_code=409, detail=f"Upload session is '{session.status}'.")

    part_size = compute_part_size(session.size)
    part_count = max(1, math.ceil(session.size / part_size))
    requested = sorted({int(n) for n in body.part_numbers})
    if not requested or requested[0] < 1 or requested[-1] > part_count:
        raise HTTPException(
            status_code=400,
            detail=f"part_numbers must be within 1..{part_count} for this upload.",
        )

    urls: list[UploadPartUrl] = []
    for part_number in requested:
        url = await asyncio.to_thread(
            create_presigned_upload_part_url,
            session.r2_key,
            session.r2_upload_id,
            part_number,
            PART_PRESIGN_TTL_SECONDS,
        )
        urls.append(UploadPartUrl(part_number=part_number, url=url))
    return UploadPartsResponse(parts=urls)


@router.post(
    "/{bucket_id}/uploads/{upload_id}/complete",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Finalize a direct-to-R2 upload",
)
async def complete_upload(
    bucket_id: uuid.UUID,
    upload_id: uuid.UUID,
    body: UploadCompleteRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from app.services.processing_v3.orchestrator import process_file

    bucket = await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    session = await _load_session(db, bucket_id, upload_id, ctx)

    # Idempotent: if the files row already exists (completed, or a retry after a
    # crash between finalize and the status flip), just return it.
    existing = await db.get(File, session.file_id)
    if existing is not None:
        if session.status != "completed":
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
            await db.commit()
        return FileUploadResponse.model_validate(existing)
    if session.status in ("aborted", "failed"):
        raise HTTPException(status_code=409, detail="This upload was cancelled. Start a new upload.")

    # 1. Complete the multipart upload if needed. A retry may hit an already-
    # completed upload (R2 errors); don't fail outright — let the HEAD below be
    # the source of truth on whether the object is actually present and intact.
    if session.mode == "multipart":
        if not body.parts:
            raise HTTPException(status_code=400, detail="Multipart completion requires the uploaded part list.")
        parts = [{"PartNumber": p.PartNumber, "ETag": p.ETag} for p in body.parts]
        try:
            await asyncio.to_thread(
                complete_multipart_upload, session.r2_key, session.r2_upload_id, parts
            )
        except Exception as exc:
            logger.warning("Multipart completion error for %s (will verify via HEAD): %s", session.r2_key, exc)

    # 2-3. HEAD the object and verify it exists with the exact declared size.
    head = await asyncio.to_thread(head_object, session.r2_key)
    if head is None:
        session.status = "failed"
        await db.commit()
        raise HTTPException(status_code=400, detail="Uploaded file was not found in storage. Please retry.")
    if int(head["size"]) != int(session.size):
        # Reject and clean up a partial/altered object so it can't be processed.
        try:
            await asyncio.to_thread(r2_delete_file, session.r2_key)
        except Exception:
            pass
        session.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded size {head['size']} bytes does not match the expected {session.size} bytes.",
        )

    session.status = "uploaded"

    # 4-8. Create files + file_versions rows, log events, set processing, enqueue.
    file_row, trace_run_id = await finalize_r2_upload(
        db,
        file_id=session.file_id,
        bucket_id=session.bucket_id,
        user_id=session.user_id,
        filename=session.filename,
        content_type=session.content_type,
        size=session.size,
        r2_key=session.r2_key,
    )

    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)
    await create_notification(
        db,
        str(session.user_id),
        "info",
        "File upload started",
        f'"{file_row.name}" was uploaded to "{bucket.name}" and is now processing.',
        commit=True,
    )

    background_tasks.add_task(process_file, str(file_row.id), trace_run_id, "upload")

    return FileUploadResponse.model_validate(file_row)


@router.post(
    "/{bucket_id}/uploads/{upload_id}/abort",
    response_model=UploadAbortResponse,
    summary="Cancel a direct-to-R2 upload",
)
async def abort_upload(
    bucket_id: uuid.UUID,
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    session = await _load_session(db, bucket_id, upload_id, ctx)

    if session.status == "completed":
        raise HTTPException(status_code=409, detail="This upload already completed and cannot be cancelled.")

    if session.mode == "multipart" and session.r2_upload_id and session.status != "aborted":
        await asyncio.to_thread(abort_multipart_upload, session.r2_key, session.r2_upload_id)

    session.status = "aborted"
    await db.commit()
    return UploadAbortResponse(status="aborted", upload_id=session.id)
