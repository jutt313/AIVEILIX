"""
File pipeline API endpoints.

POST   /v1/buckets/{bucket_id}/files                         — upload one or more files
GET    /v1/buckets/{bucket_id}/files                         — list files in bucket
GET    /v1/buckets/{bucket_id}/files/{file_id}               — file detail
GET    /v1/buckets/{bucket_id}/files/{file_id}/layout        — layout JSON
GET    /v1/buckets/{bucket_id}/files/{file_id}/chunks        — chunk list
GET    /v1/buckets/{bucket_id}/files/{file_id}/download      — download original file
DELETE /v1/buckets/{bucket_id}/files/{file_id}               — delete file
POST   /v1/buckets/{bucket_id}/files/{file_id}/retry         — re-trigger processing
POST   /v1/buckets/{bucket_id}/files/{file_id}/replace       — replace file content

Auth: Bearer token via existing get_current_user dependency.
JWT payload key: user_id  (set by security.create_access_token)
"""

import asyncio
import json
import logging
import uuid
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from fastapi.responses import Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_context
from app.database import get_db
from app.models.bucket import Bucket, Category
from app.models.chunk import Chunk
from app.models.file import File, FileVersion
from app.models.investigation_event import InvestigationEvent
from app.services.team.permissions import (
    UserContext,
    check_bucket_permission,
    get_bucket_access,
)
from app.schemas.files import (
    ChunkListResponse,
    ChunkResponse,
    DeleteFileResponse,
    FileListResponse,
    FileResponse,
    FileUploadResponse,
    InvestigationEventListResponse,
    InvestigationEventResponse,
    LayoutResponse,
    RetryResponse,
)
from app.services.pipeline.upload import _normalise_type, intake_upload
from app.services.quota import enforce_upload_quota
from app.services.notifications import create_notification
from app.services.storage.r2 import build_raw_key, download_file, delete_file as r2_delete_file, upload_file as r2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/buckets", tags=["files"])


# ── auth helpers ─────────────────────────────────────────────────────────────

def _current_user_id(current_user: dict) -> uuid.UUID:
    """Extract UUID from JWT payload — token uses 'user_id' key."""
    return uuid.UUID(current_user["user_id"])


async def _require_owned_bucket(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Bucket:
    """Owner-only: fetch bucket and verify the caller owns it."""
    bucket = await db.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")
    if bucket.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to this bucket")
    return bucket


async def _require_bucket_for_action(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    ctx: UserContext,
    permission: str | None = None,
) -> Bucket:
    """Resolve a bucket the caller is allowed to act on.

    - Owner: must own the bucket.
    - Member: must have an access row for the bucket; if `permission` is given,
      that flag must be true.
    """
    bucket = await db.get(Bucket, bucket_id)
    if bucket is None:
        raise HTTPException(status_code=404, detail="Bucket not found")

    if not ctx.is_member:
        if bucket.user_id != ctx.user_id:
            raise HTTPException(status_code=403, detail="Access denied to this bucket")
        return bucket

    if bucket.user_id != ctx.owner_user_id:
        raise HTTPException(status_code=403, detail="Access denied to this bucket")

    access = await get_bucket_access(db, ctx.team_member_id, bucket_id)
    if not access:
        raise HTTPException(status_code=403, detail="You don't have access to this bucket.")
    if permission and not getattr(access, permission, False):
        raise HTTPException(status_code=403, detail=f"You don't have permission: {permission}.")
    return bucket


def _require_file(file_row: File | None, file_id: str) -> File:
    if file_row is None:
        raise HTTPException(status_code=404, detail=f"File {file_id} not found")
    return file_row


def _check_file_in_bucket(file_row: File, bucket_id: uuid.UUID) -> None:
    if file_row.bucket_id != bucket_id:
        raise HTTPException(status_code=404, detail="File not found in this bucket")


# ── upload ───────────────────────────────────────────────────────────────────

@router.post(
    "/{bucket_id}/files",
    response_model=list[FileUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload one or more files to a bucket",
)
async def upload_files(
    bucket_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from app.services.processing_v3.dispatch import schedule_file_processing

    bucket = await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    user_id = ctx.owner_user_id

    incoming_bytes = sum(int(getattr(u, "size", 0) or 0) for u in files)
    await enforce_upload_quota(
        db, user_id, incoming_files=len(files), incoming_bytes=incoming_bytes
    )

    responses: list[FileUploadResponse] = []
    for upload in files:
        file_row, trace_run_id = await intake_upload(
            db=db,
            bucket_id=bucket_id,
            user_id=user_id,
            upload=upload,
        )
        await schedule_file_processing(str(file_row.id), trace_run_id, "upload")
        await create_notification(
            db,
            str(user_id),
            "info",
            "File upload started",
            f'"{file_row.name}" was uploaded to "{bucket.name}" and is now processing.',
            commit=True,
        )
        responses.append(FileUploadResponse.model_validate(file_row))

    return responses


# ── list files ───────────────────────────────────────────────────────────────

@router.get(
    "/{bucket_id}/files",
    response_model=FileListResponse,
    summary="List all files in a bucket",
)
async def list_files(
    bucket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx)

    # Join Category so the bucket UI can render a category chip without an
    # extra round-trip per file.
    result = await db.execute(
        select(File, Category)
        .outerjoin(Category, File.category_id == Category.id)
        .where(File.bucket_id == bucket_id)
        .order_by(File.created_at.desc())
    )
    rows = result.all()
    files: list[FileResponse] = []
    for f, cat in rows:
        resp = FileResponse.model_validate(f)
        if cat is not None:
            resp.category = {"id": cat.id, "name": cat.name, "color": cat.color}
        files.append(resp)
    return FileListResponse(files=files, total=len(files))


# ── file detail ──────────────────────────────────────────────────────────────

@router.get(
    "/{bucket_id}/files/{file_id}",
    response_model=FileResponse,
    summary="Get file metadata",
)
async def get_file(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx)

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)
    return FileResponse.model_validate(row)


# ── layout ───────────────────────────────────────────────────────────────────

@router.get(
    "/{bucket_id}/files/{file_id}/layout",
    response_model=LayoutResponse,
    summary="Get the Layout JSON for a processed file",
)
async def get_file_layout(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx)

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)

    layout_data = None
    if row.layout_json_path:
        try:
            raw = download_file(row.layout_json_path)
            layout_data = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            logger.warning("Could not fetch layout for file %s: %s", file_id, exc)

    return LayoutResponse(
        file_id=file_id,
        layout_json_path=row.layout_json_path,
        layout=layout_data,
    )


# ── chunks ───────────────────────────────────────────────────────────────────

@router.get(
    "/{bucket_id}/files/{file_id}/chunks",
    response_model=ChunkListResponse,
    summary="List all chunks for a file",
)
async def list_file_chunks(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx)

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)

    result = await db.execute(
        select(Chunk)
        .where(Chunk.file_id == file_id)
        .order_by(Chunk.page, Chunk.created_at)
    )
    chunks = result.scalars().all()
    return ChunkListResponse(
        chunks=[ChunkResponse.model_validate(c) for c in chunks],
        total=len(chunks),
    )


@router.get(
    "/{bucket_id}/files/{file_id}/events",
    response_model=InvestigationEventListResponse,
    summary="List pipeline events for a file",
)
async def list_file_events(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx)

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)

    result = await db.execute(
        select(InvestigationEvent)
        .where(InvestigationEvent.file_id == file_id)
        .order_by(InvestigationEvent.created_at.asc(), InvestigationEvent.event.asc())
    )
    events = result.scalars().all()
    return InvestigationEventListResponse(
        events=[InvestigationEventResponse.model_validate(event) for event in events],
        total=len(events),
    )


# ── download original file ───────────────────────────────────────────────────

_MIME_BY_EXT = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "epub": "application/epub+zip",
    "zip": "application/zip",
    "csv": "text/csv",
    "txt": "text/plain",
    "md": "text/markdown",
    "json": "application/json",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
}


def _content_type_for_file(file_row: File) -> str:
    if file_row.type and "/" in file_row.type:
        return file_row.type
    ext = (file_row.name.rsplit(".", 1)[-1] if "." in file_row.name else file_row.type).lower()
    return _MIME_BY_EXT.get(ext, "application/octet-stream")


@router.get(
    "/{bucket_id}/files/{file_id}/download",
    summary="Download the original uploaded file",
)
async def download_original_file(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx, "can_download_files")

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)

    if not row.r2_path:
        raise HTTPException(status_code=404, detail="File content not found")

    try:
        data = await asyncio.to_thread(download_file, row.r2_path)
    except Exception as exc:
        logger.warning("Could not download raw file %s from R2: %s", file_id, exc)
        raise HTTPException(status_code=404, detail="File content not found") from exc

    encoded_name = quote(row.name)
    return Response(
        content=data,
        media_type=_content_type_for_file(row),
        headers={
            "Content-Disposition": f"attachment; filename=\"{row.name}\"; filename*=UTF-8''{encoded_name}",
        },
    )


# ── delete file ──────────────────────────────────────────────────────────────

@router.delete(
    "/{bucket_id}/files/{file_id}",
    response_model=DeleteFileResponse,
    summary="Delete a file and all its data",
)
async def delete_file(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    await _require_bucket_for_action(db, bucket_id, ctx, "can_delete_files")
    user_id = ctx.owner_user_id

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)
    file_name = row.name

    version_rows = (
        await db.execute(select(FileVersion.r2_path).where(FileVersion.file_id == file_id))
    ).all()
    for (r2_path,) in {entry for entry in version_rows if entry and entry[0]}:
        r2_delete_file(r2_path)

    if row.r2_path:
        r2_delete_file(row.r2_path)
    if row.layout_json_path:
        r2_delete_file(row.layout_json_path)

    # ON DELETE CASCADE handles chunks, events, versions
    await db.delete(row)
    await create_notification(
        db,
        str(user_id),
        "warning",
        "File deleted",
        f'"{file_name}" was deleted from this bucket.',
    )
    await db.commit()

    return DeleteFileResponse(message="File deleted successfully", file_id=file_id)


# ── retry processing ──────────────────────────────────────────────────────────

@router.post(
    "/{bucket_id}/files/{file_id}/retry",
    response_model=RetryResponse,
    summary="Re-trigger processing for a failed file",
)
async def retry_file(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from app.services.processing_v3.dispatch import schedule_file_processing

    await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    user_id = ctx.owner_user_id

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)

    if row.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"File status is '{row.status}' — only failed files can be retried",
        )

    trace_run_id = str(uuid.uuid4())

    await db.execute(
        update(File)
        .where(File.id == file_id)
        .values(status="processing", layout_json_path=None, page_count=0)
    )
    ev = InvestigationEvent(
        file_id=file_id,
        event="retry_triggered",
        status="started",
        event_metadata={
            "triggered_by": str(user_id),
            "trace_run_id": trace_run_id,
            "trigger_source": "retry",
            "stage": "retry_enqueue",
        },
    )
    db.add(ev)
    await create_notification(
        db,
        str(user_id),
        "info",
        "File retry started",
        f'Processing retry started for "{row.name}".',
    )
    await db.commit()

    await schedule_file_processing(str(file_id), trace_run_id, "retry")

    return RetryResponse(
        message="Processing re-triggered successfully",
        file_id=file_id,
    )


# ── replace file ──────────────────────────────────────────────────────────────

@router.post(
    "/{bucket_id}/files/{file_id}/replace",
    response_model=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace the file content and re-trigger processing",
)
async def replace_file(
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from app.services.processing_v3.dispatch import schedule_file_processing

    await _require_bucket_for_action(db, bucket_id, ctx, "can_upload_files")
    user_id = ctx.owner_user_id

    row = await db.get(File, file_id)
    row = _require_file(row, str(file_id))
    _check_file_in_bucket(row, bucket_id)
    if row.status == "processing":
        raise HTTPException(
            status_code=409,
            detail="File is already processing and cannot be replaced right now",
        )

    trace_run_id = str(uuid.uuid4())

    file_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"
    filename = file.filename or row.name
    file_ext = (filename.rsplit(".", 1)[-1].lower()) if "." in filename else "bin"
    next_version = row.version + 1
    next_r2_key = build_raw_key(str(file_id), filename, version=next_version)

    # Write the replacement to a version-specific raw object so prior versions remain addressable.
    r2_upload_file(file_bytes, next_r2_key, content_type=content_type)

    # Reset status, increment version, update size
    row.name = filename
    row.type = _normalise_type(file_ext, content_type)
    row.status = "processing"
    row.version = next_version
    row.size = len(file_bytes)
    row.r2_path = next_r2_key
    row.layout_json_path = None
    row.page_count = 0

    db.add(
        FileVersion(
            file_id=file_id,
            version_number=row.version,
            r2_path=row.r2_path,
            size=row.size,
        )
    )

    ev = InvestigationEvent(
        file_id=file_id,
        event="replace_triggered",
        status="started",
        event_metadata={
            "triggered_by": str(user_id),
            "new_version": row.version,
            "filename": filename,
            "trace_run_id": trace_run_id,
            "trigger_source": "replace",
            "stage": "replace_enqueue",
        },
    )
    db.add(ev)
    await create_notification(
        db,
        str(user_id),
        "info",
        "File replacement started",
        f'"{row.name}" was replaced and is processing again.',
    )
    await db.commit()
    await db.refresh(row)

    await schedule_file_processing(str(file_id), trace_run_id, "replace")

    return FileResponse.model_validate(row)
