"""
File upload intake service.

Responsibilities:
- create files + file_versions rows in PostgreSQL
- set initial status: uploading → processing
- log investigation events for successful upload and processing start

Two entry points share the persistence + event logic below:
- ``intake_upload``     — legacy multipart-form upload: reads the bytes and pushes
                          them to R2 here, then persists.
- ``finalize_r2_upload`` — direct-to-R2 upload: the bytes are already in R2 (the
                          browser uploaded them via presigned URLs), so this only
                          persists the rows and starts processing.
"""

import logging
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File, FileVersion
from app.models.investigation_event import InvestigationEvent
from app.services.storage.r2 import upload_file, build_raw_key

logger = logging.getLogger(__name__)


async def _persist_uploaded_file(
    db: AsyncSession,
    *,
    file_id: uuid.UUID,
    bucket_id: uuid.UUID,
    user_id: uuid.UUID,
    filename: str,
    file_type: str,
    file_size: int,
    r2_key: str,
    trace_run_id: str,
    category_id: uuid.UUID | None = None,
) -> File:
    """Create the files + file_versions rows, log the upload/processing events,
    and transition the file to ``processing``. The raw object MUST already be in
    R2 before this is called. Commits and returns the refreshed File row."""
    file_row = File(
        id=file_id,
        bucket_id=bucket_id,
        user_id=user_id,
        category_id=category_id,
        name=filename,
        type=file_type,
        size=file_size,
        r2_path=r2_key,
        status="uploading",
        page_count=0,
        version=1,
    )
    db.add(file_row)
    await db.flush()

    # --- create file_versions row ---
    version_row = FileVersion(
        file_id=file_id,
        version_number=1,
        r2_path=r2_key,
        size=file_size,
    )
    db.add(version_row)

    await _log_event(
        db,
        file_id=file_id,
        event="upload_completed",
        status="completed",
        metadata={
            "filename": filename,
            "size": file_size,
            "r2_path": r2_key,
            "trace_run_id": trace_run_id,
            "trigger_source": "upload",
            "stage": "upload_intake",
        },
    )

    # --- update status to processing ---
    file_row.status = "processing"
    await db.flush()

    await _log_event(
        db,
        file_id=file_id,
        event="file_processing_started",
        status="started",
        metadata={
            "trace_run_id": trace_run_id,
            "trigger_source": "upload",
            "stage": "pipeline_enqueue",
        },
    )

    await db.commit()
    await db.refresh(file_row)
    return file_row


async def intake_upload(
    db: AsyncSession,
    bucket_id: uuid.UUID,
    user_id: uuid.UUID,
    upload: UploadFile,
    category_id: uuid.UUID | None = None,
) -> tuple[File, str]:
    """
    Handle a single uploaded file (legacy multipart-form path).
    Returns the created File ORM object (status='processing').
    """
    file_bytes = await upload.read()
    filename = upload.filename or "unnamed"
    file_size = len(file_bytes)

    # Detect file type
    content_type = upload.content_type or "application/octet-stream"
    file_ext = (filename.rsplit(".", 1)[-1].lower()) if "." in filename else "bin"
    file_type = _normalise_type(file_ext, content_type)

    file_id = uuid.uuid4()
    trace_run_id = str(uuid.uuid4())
    r2_key = build_raw_key(str(file_id), filename, version=1)

    # Match the pipeline contract exactly: raw object lands in R2 before any DB row exists.
    upload_file(file_bytes, r2_key, content_type=content_type)
    logger.info("R2 upload complete: %s", r2_key)

    file_row = await _persist_uploaded_file(
        db,
        file_id=file_id,
        bucket_id=bucket_id,
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        r2_key=r2_key,
        trace_run_id=trace_run_id,
        category_id=category_id,
    )
    return file_row, trace_run_id


async def finalize_r2_upload(
    db: AsyncSession,
    *,
    file_id: uuid.UUID,
    bucket_id: uuid.UUID,
    user_id: uuid.UUID,
    filename: str,
    content_type: str,
    size: int,
    r2_key: str,
    category_id: uuid.UUID | None = None,
) -> tuple[File, str]:
    """Persist a file whose raw bytes were uploaded directly to R2 by the browser.

    The caller (upload-complete endpoint) is responsible for completing any
    multipart upload and verifying the R2 object (HEAD + size) BEFORE calling
    this. Returns ``(file_row, trace_run_id)`` with status='processing'.
    """
    file_ext = (filename.rsplit(".", 1)[-1].lower()) if "." in filename else "bin"
    file_type = _normalise_type(file_ext, content_type or "application/octet-stream")
    trace_run_id = str(uuid.uuid4())

    file_row = await _persist_uploaded_file(
        db,
        file_id=file_id,
        bucket_id=bucket_id,
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        file_size=size,
        r2_key=r2_key,
        trace_run_id=trace_run_id,
        category_id=category_id,
    )
    return file_row, trace_run_id


async def _log_event(
    db: AsyncSession,
    file_id: uuid.UUID | None,
    event: str,
    status: str,
    metadata: dict,
) -> None:
    """Write an investigation_events row. If file_id is None it is skipped."""
    if file_id is None:
        return
    ev = InvestigationEvent(
        file_id=file_id,
        event=event,
        status=status,
        event_metadata=metadata,
    )
    db.add(ev)
    await db.flush()


def _normalise_type(ext: str, content_type: str) -> str:
    mapping = {
        "pdf": "pdf",
        "docx": "docx",
        "doc": "doc",
        "pptx": "pptx",
        "ppt": "ppt",
        # Multi-format intake (converted to Markdown at processing time —
        # see processing_v3/convert.py). Labels here only affect the row's
        # display/download Content-Type, not the conversion path.
        "xlsx": "spreadsheet",
        "xls": "spreadsheet",
        "epub": "ebook",
        "zip": "archive",
        "txt": "txt",
        "md": "md",
        "markdown": "md",
        "html": "html",
        "htm": "html",
        "adoc": "asciidoc",
        "asciidoc": "asciidoc",
        "nxml": "xml_pubmed",
        "xml": "xml",
        "json": "json",
        "jsonl": "json",
        "ndjson": "json",
        "csv": "csv",
        "tsv": "tsv",
        "yaml": "yaml",
        "yml": "yaml",
        "ini": "config",
        "toml": "config",
        "env": "config",
        "cfg": "config",
        "conf": "config",
        "properties": "config",
        "log": "log",
        "rtf": "rtf",
        # code
        "py": "code",
        "js": "code", "mjs": "code", "cjs": "code",
        "ts": "code", "tsx": "code", "jsx": "code",
        "java": "code", "kt": "code", "swift": "code",
        "c": "code", "h": "code", "cpp": "code", "cc": "code", "cxx": "code", "hpp": "code",
        "cs": "code", "go": "code", "rs": "code", "rb": "code", "php": "code",
        "sql": "code", "sh": "code", "bash": "code", "zsh": "code",
        "r": "code", "dart": "code", "vue": "code", "svelte": "code",
        "png": "image",
        "jpg": "image",
        "jpeg": "image",
        "gif": "image",
        "webp": "image",
        "bmp": "image",
        "tif": "image",
        "tiff": "image",
    }
    if ext in mapping:
        return mapping[ext]
    if content_type.startswith("image/"):
        return "image"
    return ext or "unknown"
