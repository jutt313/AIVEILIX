from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Header, Form, Query, BackgroundTasks
from typing import Optional, List, Dict, Any, Callable
from app.models.files import FileResponse, FilesListResponse, FileUploadResponse, SummaryUpdateRequest, SearchResponse, SearchResult, CreateFileRequest, FileContentUpdateRequest
from app.models.buckets import BucketResponse
from app.services.supabase import get_supabase_auth, get_supabase
from app.services.file_processor import extract_text_from_file, chunk_text, generate_embedding, generate_embeddings_batch, generate_summary, analyze_file_comprehensive, generate_spatial_summary, fetch_full_file_content, enrich_summary_with_web_search
from app.services.semantic_search import semantic_search, hybrid_search
from app.services.notifications import create_file_uploaded_notification, create_file_processed_notification
from app.services.plan_limits import check_all_upload_limits, check_file_size_limit, check_storage_limit
from postgrest.exceptions import APIError as PostgrestAPIError
import asyncio
from app.routers.buckets import get_current_user_id
from app.config import get_settings
from app.utils.tracer import Tracer
import uuid
import os
import hashlib
import tempfile
import logging
import traceback
from pathlib import Path
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import sentry_sdk
import re
import io
import zipfile
import fitz
import time

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

ALLOWED_CREATED_FILE_EXTENSIONS = {".md", ".txt"}
IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
ACTIVE_FILE_STATUSES = ["pending", "processing"]

PROGRESS_STAGE_BOUNDS = {
    "queued": (0.0, 0.0),
    "downloading": (0.0, 10.0),
    "extracting": (10.0, 25.0),
    "image_ocr": (25.0, 55.0),
    "chunking": (55.0, 65.0),
    "embedding": (65.0, 85.0),
    "storing": (85.0, 95.0),
    "summarizing": (95.0, 99.0),
    "finalizing": (99.0, 100.0),
    "ready": (100.0, 100.0),
}


def _clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))


def _compute_progress_percent(stage: str, current: int, total: int, fallback: float = 0.0) -> float:
    if stage == "failed":
        return _clamp_percent(fallback)
    bounds = PROGRESS_STAGE_BOUNDS.get(stage)
    if not bounds:
        return _clamp_percent(fallback)
    start, end = bounds
    if total and total > 0:
        ratio = max(0.0, min(1.0, float(current) / float(total)))
    else:
        ratio = 1.0 if current > 0 else 0.0
    return _clamp_percent(start + (end - start) * ratio)


def _safe_progress_meta(meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return meta if isinstance(meta, dict) else {}


def _append_investigation_event(
    supabase,
    *,
    file_id: str,
    bucket_id: str,
    user_id: str,
    event_type: str,
    stage: Optional[str],
    label: str,
    current: int,
    total: int,
    percent: float,
    meta: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if not settings.investigation_events_enabled:
        return None

    payload = {
        "id": str(uuid.uuid4()),
        "file_id": file_id,
        "bucket_id": bucket_id,
        "user_id": user_id,
        "event_type": event_type,
        "stage": stage,
        "label": (label or stage or "Progress update")[:300],
        "current": max(0, int(current or 0)),
        "total": max(0, int(total or 0)),
        "percent": _clamp_percent(percent),
        "meta": _safe_progress_meta(meta),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        result = supabase.table("investigation_events").insert(payload).execute()
        if result.data:
            return result.data[0]
    except Exception as e:
        logger.warning(f"Investigation event write failed (non-critical) for file {file_id}: {e}")
    return None


def _build_progress_writer(
    supabase,
    file_id: str,
    bucket_id: str,
    user_id: str,
    file_name: str,
    loop=None,
):
    state = {
        "last_stage": None,
        "last_current": -1,
        "last_percent": 0.0,
        "last_write_at": 0.0,
        "stage_started_at": None,
        "last_event_at": 0.0,
        "last_event_stage": None,
        "last_event_current": -1,
    }

    def update_file_progress(
        stage: str,
        label: Optional[str] = None,
        current: int = 0,
        total: int = 0,
        percent: Optional[float] = None,
        meta: Optional[Dict[str, Any]] = None,
        status_message: Optional[str] = None,
        force: bool = False,
    ) -> float:
        now = time.monotonic()
        current_value = max(0, int(current or 0))
        total_value = max(0, int(total or 0))
        if total_value and current_value > total_value:
            current_value = total_value

        percent_value = (
            _clamp_percent(percent)
            if percent is not None
            else _compute_progress_percent(
                stage=stage,
                current=current_value,
                total=total_value,
                fallback=state["last_percent"],
            )
        )

        stage_changed = stage != state["last_stage"]
        item_delta = current_value - state["last_current"]
        should_write = (
            force
            or stage_changed
            or item_delta >= 2
            or (now - state["last_write_at"] >= 1.0)
            or status_message is not None
        )
        if not should_write:
            return percent_value

        try:
            safe_meta = _safe_progress_meta(meta)
            if stage_changed:
                if state["last_stage"] and state["stage_started_at"] is not None:
                    logger.info(
                        "📈 Progress stage completed: file_id=%s stage=%s duration=%.2fs",
                        file_id,
                        state["last_stage"],
                        now - state["stage_started_at"],
                    )
                logger.info(
                    "📈 Progress stage transition: file_id=%s stage=%s percent=%.2f",
                    file_id,
                    stage,
                    percent_value,
                )
                state["stage_started_at"] = now

            # Broadcast live SSE commentary for every throttled progress update.
            try:
                from app.services.processing_commentary import broadcast_progress
                broadcast_progress(
                    bucket_id=bucket_id,
                    stage=stage,
                    filename=file_name,
                    file_id=file_id,
                    label=label,
                    current=current_value,
                    total=total_value,
                    meta=safe_meta,
                    loop=loop,
                )
            except Exception as _sse_err:
                logger.debug(f"SSE broadcast skipped: {_sse_err}")

            payload: Dict[str, Any] = {
                "progress_stage": stage,
                "progress_label": label,
                "progress_current": current_value,
                "progress_total": total_value,
                "progress_percent": percent_value,
                "progress_meta": safe_meta,
                "progress_updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if status_message is not None:
                payload["status_message"] = status_message

            supabase.table("files").update(payload).eq("id", file_id).execute()

            event_type = "counter"
            if stage_changed:
                event_type = "stage"
            if stage == "ready":
                event_type = "complete"
            elif stage == "failed":
                event_type = "error"

            event_should_write = (
                event_type in ("stage", "complete", "error")
                or force
                or (current_value - state["last_event_current"] >= 2)
                or (now - state["last_event_at"] >= 1.0)
            )
            if event_should_write:
                event_meta = safe_meta.copy()
                if file_name and "file_name" not in event_meta:
                    event_meta["file_name"] = file_name
                if status_message:
                    event_meta["status_message"] = status_message

                _append_investigation_event(
                    supabase,
                    file_id=file_id,
                    bucket_id=bucket_id,
                    user_id=user_id,
                    event_type=event_type,
                    stage=stage,
                    label=label or stage or "Progress update",
                    current=current_value,
                    total=total_value,
                    percent=percent_value,
                    meta=event_meta,
                )
                state["last_event_at"] = now
                state["last_event_stage"] = stage
                state["last_event_current"] = current_value

            state["last_stage"] = stage
            state["last_current"] = current_value
            state["last_percent"] = percent_value
            state["last_write_at"] = now
        except Exception as e:
            logger.warning(f"Progress write failed (non-critical) for file {file_id}: {e}")

        return percent_value

    return update_file_progress


def _resolve_investigation_conversation_id(
    supabase,
    effective_uid: str,
    bucket_id: str,
    conversation_id: Optional[str],
) -> Optional[str]:
    if not conversation_id:
        return None
    try:
        conv_res = (
            supabase.table("conversations")
            .select("id")
            .eq("id", conversation_id)
            .eq("user_id", effective_uid)
            .eq("bucket_id", bucket_id)
            .limit(1)
            .execute()
        )
        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found for this bucket")
        return conversation_id
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversation_id")


def _get_or_create_investigation_conversation(supabase, user_id: str, bucket_id: str) -> str:
    existing = (
        supabase.table("conversations")
        .select("id")
        .eq("user_id", user_id)
        .eq("bucket_id", bucket_id)
        .eq("mode", "investigation")
        .order("created_at", desc=False)
        .limit(1)
        .execute()
    )
    if existing.data:
        return str(existing.data[0]["id"])

    created = (
        supabase.table("conversations")
        .insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "bucket_id": bucket_id,
            "title": "Investigation",
            "mode": "investigation",
        })
        .execute()
    )
    if created.data:
        return str(created.data[0]["id"])
    raise RuntimeError("Failed to create investigation conversation")


def _post_auto_investigation_reply(
    supabase,
    *,
    user_id: str,
    bucket_id: str,
    file_id: str,
    filename: str,
    summary_text: str,
    summary_id: Optional[str] = None,
    preferred_conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    conversation_id = preferred_conversation_id or _get_or_create_investigation_conversation(
        supabase, user_id, bucket_id
    )

    existing_auto = (
        supabase.table("messages")
        .select("id, conversation_id")
        .eq("user_id", user_id)
        .eq("role", "assistant")
        .contains("metadata", {"auto_investigation": True, "file_id": file_id})
        .limit(1)
        .execute()
    )
    if existing_auto.data:
        return {
            "conversation_id": str(existing_auto.data[0].get("conversation_id") or conversation_id),
            "posted": False,
        }

    summary_excerpt = (summary_text or "").strip()
    if len(summary_excerpt) > 1800:
        summary_excerpt = summary_excerpt[:1800].rstrip() + "\n..."
    if not summary_excerpt:
        summary_excerpt = "File processing finished, but no summary text was generated."

    message_content = (
        f"Investigation complete for `{filename}`.\n\n"
        f"{summary_excerpt}\n\n"
        "You can now ask follow-up questions about this file."
    )

    metadata = {
        "auto_investigation": True,
        "file_id": file_id,
        "summary_id": summary_id,
        "source": "background_processing",
    }
    sources = [{
        "type": "analysis",
        "file_id": file_id,
        "file_name": filename,
        "summary_id": summary_id,
        "confidence": "high",
    }]

    supabase.table("messages").insert({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": message_content,
        "model_used": "investigation-summary",
        "sources": sources,
        "metadata": metadata,
    }).execute()
    supabase.table("conversations").update({
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", conversation_id).execute()
    return {"conversation_id": conversation_id, "posted": True}


def _validate_created_filename(filename: str) -> str:
    name = (filename or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="File name is required")

    if "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="File name must not include a path")

    if len(name) > 255:
        raise HTTPException(status_code=400, detail="File name is too long")

    ext = Path(name).suffix.lower()
    if not ext or ext not in ALLOWED_CREATED_FILE_EXTENSIONS:
        # Default to .md if no extension or invalid extension
        name = name.rsplit('.', 1)[0] + '.md' if '.' in name else name + '.md'

    # Basic filename sanity (no control chars)
    if re.search(r"[\x00-\x1f\x7f]", name):
        raise HTTPException(status_code=400, detail="File name contains invalid characters")

    return name


async def _enforce_update_limits(user_id: str, new_size: int, existing_size: int) -> None:
    can_upload, error = await check_file_size_limit(user_id, new_size)
    if not can_upload:
        raise HTTPException(status_code=402, detail={
            "error": "file_size_limit",
            "message": error,
            "upgrade_required": True
        })

    delta = max(0, new_size - existing_size)
    can_upload, error = await check_storage_limit(user_id, delta)
    if not can_upload:
        raise HTTPException(status_code=402, detail={
            "error": "storage_limit",
            "message": error,
            "upgrade_required": True
        })


def _count_images_in_file(content: bytes, mime_type: str, filename: str) -> int:
    """Best-effort image count per single file for plan enforcement."""
    if not content:
        return 0

    mt = (mime_type or "").lower()
    ext = Path(filename or "").suffix.lower()

    # Single image files
    if mt.startswith("image/") or ext in IMAGE_FILE_EXTENSIONS:
        return 1

    # PDF: count embedded images
    if mt == "application/pdf" or ext == ".pdf":
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            count = 0
            for page in doc:
                count += len(page.get_images(full=False))
            doc.close()
            return count
        except Exception:
            return 0

    # DOCX: count media images in zip package
    if mt in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ) or ext == ".docx":
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                return len([
                    n for n in zf.namelist()
                    if n.startswith("word/media/")
                    and Path(n).suffix.lower() in IMAGE_FILE_EXTENSIONS
                ])
        except Exception:
            return 0

    return 0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
    before_sleep=lambda retry_state: logger.warning(
        f"⚠️ Retry attempt {retry_state.attempt_number} for file processing after error: {retry_state.outcome.exception()}"
    )
)
def _process_file_with_retry(
    file_id: str,
    storage_path: str,
    filename: str,
    mime_type: str,
    user_id: str,
    bucket_id: str,
    supabase,
    progress_callback: Optional[Callable[..., Any]] = None,
) -> Dict:
    """
    Inner function that does the actual processing with retry support.
    Retries on transient errors (connection, timeout, OS errors).
    """
    if progress_callback:
        progress_callback(
            stage="downloading",
            label="Opening your file...",
            current=0,
            total=1,
            meta={"file_name": filename},
            force=True,
        )
    # Download file from storage
    logger.info(f"  1️⃣  Downloading file from storage...")
    file_data = supabase.storage.from_("files").download(storage_path)

    if not file_data:
        raise ConnectionError("Failed to download file from storage")

    # Save to temp file for processing
    file_ext = os.path.splitext(storage_path)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(file_data)
        temp_file_path = temp_file.name

    logger.info(f"  ✅ Downloaded ({len(file_data)} bytes)")
    if progress_callback:
        progress_callback(
            stage="downloading",
            label="File opened successfully.",
            current=1,
            total=1,
            meta={"bytes": len(file_data)},
            force=True,
        )

    try:
        # Extract text
        logger.info(f"  2️⃣  Extracting text from {filename}...")
        if progress_callback:
            progress_callback(
                stage="extracting",
                label="Reading text and structure...",
                current=0,
                total=1,
                meta={"mime_type": mime_type},
                force=True,
            )
        text_data = extract_text_from_file(
            temp_file_path,
            mime_type,
            progress_callback=progress_callback,
        )
        text = text_data["text"]
        metadata = text_data["metadata"]

        logger.info(f"  ✅ Text extracted: {len(text)} chars, {metadata.get('word_count', 0)} words")
        if progress_callback:
            progress_callback(
                stage="extracting",
                label="Text and layout captured.",
                current=1,
                total=1,
                meta={"char_count": len(text), "word_count": metadata.get("word_count", 0)},
                force=True,
            )

        # Only process if we got text content
        if not text or len(text.strip()) == 0:
            raise ValueError("No text content extracted from file")

        # Create chunks
        logger.info(f"  3️⃣  Creating text chunks...")
        if progress_callback:
            progress_callback(
                stage="chunking",
                label="Organizing content into readable sections...",
                current=0,
                total=1,
                meta={},
                force=True,
            )
        chunks = chunk_text(text)
        logger.info(f"  ✅ Created {len(chunks)} chunks")
        if progress_callback:
            progress_callback(
                stage="chunking",
                label="Sections organized.",
                current=1,
                total=1,
                meta={"chunk_count": len(chunks)},
                force=True,
            )

        # Generate embeddings in BATCH (much faster than one-by-one)
        logger.info(f"  4️⃣  Generating embeddings for {len(chunks)} chunks...")
        chunk_texts = [chunk["content"] for chunk in chunks]
        if progress_callback:
            progress_callback(
                stage="embedding",
                label=f"Connecting ideas across sections (0/{len(chunks)})",
                current=0,
                total=max(1, len(chunks)),
                meta={"chunk_count": len(chunks)},
                force=True,
            )
        embeddings = generate_embeddings_batch(chunk_texts)
        if progress_callback:
            for i in range(len(chunks)):
                progress_callback(
                    stage="embedding",
                    label=f"Connecting ideas across sections ({i + 1}/{len(chunks)})",
                    current=i + 1,
                    total=max(1, len(chunks)),
                    meta={"chunk_count": len(chunks)},
                )

        # Store chunks with embeddings
        logger.info(f"  5️⃣  Storing chunks in database...")
        if progress_callback:
            progress_callback(
                stage="storing",
                label=f"Saving findings (0/{len(chunks)})",
                current=0,
                total=max(1, len(chunks)),
                meta={"chunk_count": len(chunks)},
                force=True,
            )
        chunk_records = []
        for i, chunk in enumerate(chunks):
            chunk_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "bucket_id": bucket_id,
                "file_id": file_id,
                "content": chunk["content"],
                "content_hash": hashlib.md5(chunk["content"].encode()).hexdigest(),
                "chunk_index": chunk["chunk_index"],
                "start_offset": chunk["start_offset"],
                "end_offset": chunk["end_offset"],
                "token_count": chunk["token_count"]
            }
            # Only add embedding if it was generated
            if embeddings[i]:
                chunk_record["embedding"] = embeddings[i]
            chunk_records.append(chunk_record)
            if progress_callback:
                progress_callback(
                    stage="storing",
                    label=f"Saving findings ({i + 1}/{len(chunks)})",
                    current=i + 1,
                    total=max(1, len(chunks)),
                    meta={"chunk_count": len(chunks)},
                )

        # Batch insert chunks
        if chunk_records:
            supabase.table("chunks").insert(chunk_records).execute()
            logger.info(f"  ✅ Stored {len(chunk_records)} chunks")
            if progress_callback:
                progress_callback(
                    stage="storing",
                    label="Findings saved.",
                    current=len(chunk_records),
                    total=max(1, len(chunk_records)),
                    meta={"chunk_count": len(chunk_records)},
                    force=True,
                )

        return {"metadata": metadata, "chunks_count": len(chunk_records), "text_data": text_data}

    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def process_file_background(
    file_id: str,
    storage_path: str,
    filename: str,
    mime_type: str,
    user_id: str,
    bucket_id: str
) -> None:
    """
    Background task to process a file after upload.
    Fetches file from Supabase Storage, extracts text, creates chunks with embeddings.
    This runs in background so upload returns instantly.
    Includes retry logic for transient failures.
    """
    logger.info("=" * 80)
    logger.info(f"🔄 BACKGROUND PROCESSING STARTED: {filename}")
    logger.info(f"   File ID: {file_id}")
    logger.info(f"   Storage Path: {storage_path}")
    logger.info(f"   MIME Type: {mime_type}")

    supabase = get_supabase()
    try:
        _bg_loop = asyncio.get_event_loop()
    except RuntimeError:
        _bg_loop = None
    update_file_progress = _build_progress_writer(
        supabase=supabase,
        file_id=file_id,
        bucket_id=bucket_id,
        user_id=user_id,
        file_name=filename,
        loop=_bg_loop,
    )

    existing_investigation_conversation_id = None
    try:
        file_res = (
            supabase.table("files")
            .select("investigation_conversation_id")
            .eq("id", file_id)
            .limit(1)
            .execute()
        )
        if file_res.data:
            existing_investigation_conversation_id = file_res.data[0].get("investigation_conversation_id")
    except Exception:
        existing_investigation_conversation_id = None

    try:
        supabase.table("files").update({
            "status": "processing",
            "status_message": "Processing started",
            "auto_summary_error": None,
        }).eq("id", file_id).execute()

        def progress_callback(
            stage: str,
            label: str,
            current: int,
            total: int,
            meta: Optional[Dict[str, Any]] = None,
            force: bool = False,
            status_message: Optional[str] = None,
        ) -> None:
            update_file_progress(
                stage=stage,
                label=label,
                current=current,
                total=total,
                meta=meta,
                status_message=status_message,
                force=force,
            )

        update_file_progress(
            stage="queued",
            label="Queued. Starting investigation shortly...",
            current=0,
            total=1,
            percent=0.0,
            meta={"file_name": filename},
            force=True,
        )

        result = _process_file_with_retry(
            file_id=file_id,
            storage_path=storage_path,
            filename=filename,
            mime_type=mime_type,
            user_id=user_id,
            bucket_id=bucket_id,
            supabase=supabase,
            progress_callback=progress_callback,
        )

        metadata = result["metadata"]
        summary_text = ""
        summary_id: Optional[str] = None

        logger.info("  6️⃣  Generating spatial summary...")
        update_file_progress(
            stage="summarizing",
            label="Preparing your first answer...",
            current=0,
            total=1,
            meta={},
            force=True,
        )
        try:
            text_data_for_summary = result.get("text_data", {})
            full_text = text_data_for_summary.get("text", "")

            if full_text and len(full_text.strip()) > 50:
                summary_result = generate_spatial_summary(text_data_for_summary, filename)
                summary_text = summary_result.get("summary", "")

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            enriched = pool.submit(
                                asyncio.run,
                                enrich_summary_with_web_search(summary_text, filename)
                            ).result(timeout=15)
                    else:
                        enriched = asyncio.run(enrich_summary_with_web_search(summary_text, filename))
                    summary_text = enriched
                except Exception as web_err:
                    logger.warning(f"Web enrichment skipped: {web_err}")

                summary_id = str(uuid.uuid4())
                supabase.table("summaries").insert({
                    "id": summary_id,
                    "user_id": user_id,
                    "bucket_id": bucket_id,
                    "file_id": file_id,
                    "summary_type": "file",
                    "title": f"Analysis: {filename}",
                    "content": summary_text,
                    "model_used": summary_result.get("model_used", "deepseek-chat")
                }).execute()
                logger.info(f"  ✅ Summary stored ({len(summary_text)} chars)")

            update_file_progress(
                stage="summarizing",
                label="First answer draft ready.",
                current=1,
                total=1,
                meta={"summary_created": bool(summary_text), "summary_id": summary_id},
                force=True,
            )
        except Exception as summary_err:
            logger.warning(f"Summary generation failed (non-critical): {summary_err}")
            update_file_progress(
                stage="summarizing",
                label="Skipped first-answer draft.",
                current=1,
                total=1,
                meta={"summary_error": str(summary_err)[:200]},
                force=True,
            )

        update_file_progress(
            stage="finalizing",
            label="Finalizing your file...",
            current=1,
            total=1,
            meta={},
            force=True,
        )
        supabase.table("files").update({
            "status": "ready",
            "status_message": "Processing complete",
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "page_count": metadata.get("page_count"),
            "word_count": metadata.get("word_count"),
        }).eq("id", file_id).execute()

        auto_summary_error = None
        resolved_conversation_id = existing_investigation_conversation_id
        if settings.auto_first_reply_enabled:
            try:
                auto_summary_content = (summary_text or "").strip()
                if not auto_summary_content:
                    auto_summary_content = (
                        f"The file `{filename}` has been processed and is ready. "
                        "Ask any question about its content."
                    )

                auto_result = _post_auto_investigation_reply(
                    supabase,
                    user_id=user_id,
                    bucket_id=bucket_id,
                    file_id=file_id,
                    filename=filename,
                    summary_text=auto_summary_content,
                    summary_id=summary_id,
                    preferred_conversation_id=existing_investigation_conversation_id,
                )
                resolved_conversation_id = auto_result.get("conversation_id")

                supabase.table("files").update({
                    "investigation_conversation_id": resolved_conversation_id,
                    "auto_summary_posted_at": datetime.now(timezone.utc).isoformat(),
                    "auto_summary_error": None,
                }).eq("id", file_id).execute()
            except Exception as auto_err:
                auto_summary_error = str(auto_err)
                logger.warning(f"Auto investigation post failed for file {file_id}: {auto_summary_error}")
                _append_investigation_event(
                    supabase,
                    file_id=file_id,
                    bucket_id=bucket_id,
                    user_id=user_id,
                    event_type="error",
                    stage="ready",
                    label="Auto investigation message failed",
                    current=1,
                    total=1,
                    percent=100.0,
                    meta={
                        "file_name": filename,
                        "error": auto_summary_error[:300],
                    },
                )
                supabase.table("files").update({
                    "investigation_conversation_id": resolved_conversation_id,
                    "auto_summary_error": auto_summary_error[:500],
                }).eq("id", file_id).execute()

        update_file_progress(
            stage="ready",
            label="Investigation ready.",
            current=1,
            total=1,
            percent=100.0,
            meta={
                "chunks_count": result.get("chunks_count", 0),
                "summary_id": summary_id,
                "investigation_conversation_id": resolved_conversation_id,
            },
            force=True,
        )

        logger.info(f"✅ BACKGROUND PROCESSING COMPLETE: {filename}")
        logger.info("=" * 80)
        create_file_processed_notification(user_id, filename, bucket_id, file_id)

    except Exception as e:
        error_message = str(e)
        logger.error("=" * 80)
        logger.error(f"❌ BACKGROUND PROCESSING FAILED: {filename} (file_id: {file_id})")
        logger.error(f"   Error: {error_message}")
        logger.error(f"   Traceback:", exc_info=True)
        logger.error("=" * 80)

        # Capture to Sentry with file context
        sentry_sdk.set_context("file_processing", {
            "file_id": file_id,
            "filename": filename,
            "storage_path": storage_path,
            "mime_type": mime_type,
            "user_id": user_id,
            "bucket_id": bucket_id,
        })
        sentry_sdk.capture_exception(e)

        update_file_progress(
            stage="failed",
            label="Processing failed",
            current=0,
            total=1,
            meta={"error": error_message[:200]},
            status_message=f"Processing failed: {error_message[:200]}",
            force=True,
        )

        try:
            supabase.table("files").update({
                "status": "failed",
                "status_message": f"Processing failed: {error_message[:200]}",
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "progress_stage": "failed",
                "progress_label": "Processing failed",
                "progress_meta": {"error": error_message[:200]},
                "progress_updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", file_id).execute()
        except Exception as update_error:
            logger.error(f"Failed to update file status: {update_error}")


@router.post("/{bucket_id}/upload", response_model=FileUploadResponse)
async def upload_file(
    bucket_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    folder_path: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    batch_count: Optional[int] = Form(None),
    batch_total_bytes: Optional[int] = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    """
    Upload a file to a bucket - INSTANT RESPONSE.

    File is saved to storage immediately, processing happens in background.
    Chat AI can read unprocessed files directly from storage.
    """
    t = Tracer("POST /api/buckets/{id}/upload", user_id=user_id, bucket_id=bucket_id, filename=file.filename)
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)
        team_ctx = get_team_member_context(user_id)
        t.step("Team service checks")

        if not check_bucket_permission(user_id, bucket_id, "can_upload"):
            raise HTTPException(status_code=403, detail="You don't have upload permission for this bucket")

        supabase = get_supabase()

        try:
            bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")
        t.step("DB verify bucket")

        resolved_conversation_id = _resolve_investigation_conversation_id(
            supabase=supabase,
            effective_uid=effective_uid,
            bucket_id=bucket_id,
            conversation_id=conversation_id,
        )

        content = await file.read()
        file_ext = Path(file.filename).suffix
        t.step("Read file content", size=len(content))

        image_count = _count_images_in_file(content, file.content_type or "", file.filename or "")
        effective_batch_count = max(1, int(batch_count or 1))
        effective_batch_total = int(batch_total_bytes or len(content))

        await check_all_upload_limits(
            user_id,
            len(content),
            batch_count=effective_batch_count,
            batch_total_bytes=effective_batch_total,
            image_count=image_count
        )
        t.step("Check plan limits")

        storage_path = f"{user_id}/{bucket_id}/{uuid.uuid4()}{file_ext}"
        supabase.storage.from_("files").upload(storage_path, content)
        t.step("Upload to Supabase Storage")

        # Extract just the filename (remove folder path if present in filename)
        filename = file.filename
        if '/' in filename:
            filename = filename.split('/')[-1]

        # Create file record with "pending" status - INSTANT
        file_id = str(uuid.uuid4())
        file_record = {
            "id": file_id,
            "user_id": effective_uid,
            "bucket_id": bucket_id,
            "name": filename,
            "original_name": filename,
            "mime_type": file.content_type,
            "size_bytes": len(content),
            "storage_path": storage_path,
            "status": "pending",  # Will be "processing" then "ready" after background task
            "source": "uploaded",
            "progress_stage": "queued",
            "progress_label": "Queued for processing",
            "progress_current": 0,
            "progress_total": 1,
            "progress_percent": 0,
            "progress_meta": {"file_name": filename},
            "progress_updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if resolved_conversation_id:
            file_record["investigation_conversation_id"] = resolved_conversation_id

        # Track which team member uploaded
        if team_ctx:
            file_record["uploaded_by_member_id"] = team_ctx["team_member_id"]
            file_record["uploaded_by_color"] = team_ctx["color"]
            file_record["uploaded_by_name"] = team_ctx["name"]

        # Add folder_path if provided
        if folder_path:
            file_record["folder_path"] = folder_path

        supabase.table("files").insert(file_record).execute()
        t.step("DB insert file record")

        create_file_uploaded_notification(effective_uid, filename, bucket_id, file_id)

        # Log team activity
        if team_ctx:
            log_team_activity(
                owner_id=effective_uid,
                member_id=user_id,
                team_member_id=team_ctx["team_member_id"],
                bucket_id=bucket_id,
                action_type="uploaded_file",
                resource_id=file_id,
                resource_name=filename,
                member_color=team_ctx["color"],
                member_name=team_ctx["name"],
            )

        # Add background task for processing - DOES NOT BLOCK RESPONSE
        background_tasks.add_task(
            process_file_background,
            file_id=file_id,
            storage_path=storage_path,
            filename=filename,
            mime_type=file.content_type,
            user_id=effective_uid,
            bucket_id=bucket_id
        )

        t.done()

        return FileUploadResponse(
            id=file_id,
            name=filename,
            status="pending",
            message="File uploaded! Processing in background. You can chat about it now."
        )

    except HTTPException:
        t.done(status_code=400)
        raise
    except Exception as e:
        t.error("upload failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.post("/{bucket_id}/register-upload", response_model=FileUploadResponse)
async def register_direct_upload(
    bucket_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    storage_path: str = Form(...),
    filename: str = Form(...),
    size_bytes: int = Form(...),
    mime_type: str = Form("application/octet-stream"),
    folder_path: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    batch_count: Optional[int] = Form(None),
    batch_total_bytes: Optional[int] = Form(None),
):
    """
    Register a file that was uploaded directly to Supabase Storage from the frontend.
    Creates the file record and triggers background processing.
    """
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)
        team_ctx = get_team_member_context(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_upload"):
            raise HTTPException(status_code=403, detail="You don't have upload permission for this bucket")

        supabase = get_supabase()

        # Verify bucket belongs to effective user
        try:
            supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")

        resolved_conversation_id = _resolve_investigation_conversation_id(
            supabase=supabase,
            effective_uid=effective_uid,
            bucket_id=bucket_id,
            conversation_id=conversation_id,
        )

        # Direct uploads don't include file bytes in this request; fetch once for image-count checks
        image_count = 0
        try:
            file_data = supabase.storage.from_("files").download(storage_path)
            image_count = _count_images_in_file(file_data, mime_type, filename)
        except Exception as e:
            logger.warning(f"Could not inspect direct-upload file for image count: {e}")

        effective_batch_count = max(1, int(batch_count or 1))
        effective_batch_total = int(batch_total_bytes or size_bytes)

        # Check plan limits
        await check_all_upload_limits(
            user_id,
            size_bytes,
            batch_count=effective_batch_count,
            batch_total_bytes=effective_batch_total,
            image_count=image_count
        )

        # Clean filename
        clean_name = filename
        if '/' in clean_name:
            clean_name = clean_name.split('/')[-1]

        # Create file record
        file_id = str(uuid.uuid4())
        file_record = {
            "id": file_id,
            "user_id": effective_uid,
            "bucket_id": bucket_id,
            "name": clean_name,
            "original_name": clean_name,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "storage_path": storage_path,
            "status": "pending",
            "source": "uploaded",
            "progress_stage": "queued",
            "progress_label": "Queued for processing",
            "progress_current": 0,
            "progress_total": 1,
            "progress_percent": 0,
            "progress_meta": {"file_name": clean_name},
            "progress_updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if resolved_conversation_id:
            file_record["investigation_conversation_id"] = resolved_conversation_id

        if team_ctx:
            file_record["uploaded_by_member_id"] = team_ctx["team_member_id"]
            file_record["uploaded_by_color"] = team_ctx["color"]
            file_record["uploaded_by_name"] = team_ctx["name"]

        if folder_path:
            file_record["folder_path"] = folder_path

        supabase.table("files").insert(file_record).execute()

        create_file_uploaded_notification(effective_uid, clean_name, bucket_id, file_id)

        if team_ctx:
            log_team_activity(
                owner_id=effective_uid,
                member_id=user_id,
                team_member_id=team_ctx["team_member_id"],
                bucket_id=bucket_id,
                action_type="uploaded_file",
                resource_id=file_id,
                resource_name=clean_name,
                member_color=team_ctx["color"],
                member_name=team_ctx["name"],
            )

        background_tasks.add_task(
            process_file_background,
            file_id=file_id,
            storage_path=storage_path,
            filename=clean_name,
            mime_type=mime_type,
            user_id=effective_uid,
            bucket_id=bucket_id
        )

        logger.info(f"⚡ DIRECT UPLOAD REGISTERED: {clean_name} (processing in background)")

        return FileUploadResponse(
            id=file_id,
            name=clean_name,
            status="pending",
            message="File registered! Processing in background."
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error registering direct upload: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.post("/{bucket_id}/files/create", response_model=FileUploadResponse)
async def create_file(
    bucket_id: str,
    request: CreateFileRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id)
):
    """Create a .md or .txt file in a bucket (stored in DB + storage)."""
    try:
        supabase = get_supabase()

        # Verify bucket belongs to user
        try:
            supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")

        filename = _validate_created_filename(request.name)
        content_text = request.content or ""
        if not content_text.strip():
            raise HTTPException(status_code=400, detail="File content is required")

        content_bytes = content_text.encode("utf-8")
        await check_all_upload_limits(user_id, len(content_bytes))

        file_ext = Path(filename).suffix.lower()
        mime_type = "text/markdown" if file_ext == ".md" else "text/plain"

        # Check if a file with this name already exists
        existing = supabase.table("files").select("id, source, storage_path, size_bytes").eq("bucket_id", bucket_id).eq("user_id", user_id).eq("name", filename).limit(1).execute()
        if existing.data:
            existing_file = existing.data[0]
            if existing_file.get("source") != "created":
                raise HTTPException(status_code=409, detail="A file with this name already exists")

            file_id = str(existing_file["id"])
            storage_path = existing_file["storage_path"]
            existing_size = existing_file.get("size_bytes") or 0

            await _enforce_update_limits(user_id, len(content_bytes), existing_size)

            # Replace file content in storage
            try:
                supabase.storage.from_("files").remove([storage_path])
            except Exception:
                pass
            supabase.storage.from_("files").upload(storage_path, content_bytes)

            # Reset processing status and update size/mime
            supabase.table("files").update({
                "mime_type": mime_type,
                "size_bytes": len(content_bytes),
                "status": "pending",
                "status_message": None,
                "processed_at": None,
                "source": "created"
            }).eq("id", file_id).execute()

            # Clear old chunks before reprocessing
            supabase.table("chunks").delete().eq("file_id", file_id).execute()

            # Reprocess in background
            background_tasks.add_task(
                process_file_background,
                file_id=file_id,
                storage_path=storage_path,
                filename=filename,
                mime_type=mime_type,
                user_id=user_id,
                bucket_id=bucket_id
            )

            return FileUploadResponse(
                id=file_id,
                name=filename,
                status="pending",
                message="File updated! Processing in background."
            )

        # Create new file in storage
        storage_path = f"{user_id}/{bucket_id}/{uuid.uuid4()}{file_ext}"
        supabase.storage.from_("files").upload(storage_path, content_bytes)

        file_id = str(uuid.uuid4())
        file_record = {
            "id": file_id,
            "user_id": user_id,
            "bucket_id": bucket_id,
            "name": filename,
            "original_name": filename,
            "mime_type": mime_type,
            "size_bytes": len(content_bytes),
            "storage_path": storage_path,
            "status": "pending",
            "source": "created"
        }

        supabase.table("files").insert(file_record).execute()

        # Process in background
        background_tasks.add_task(
            process_file_background,
            file_id=file_id,
            storage_path=storage_path,
            filename=filename,
            mime_type=mime_type,
            user_id=user_id,
            bucket_id=bucket_id
        )

        return FileUploadResponse(
            id=file_id,
            name=filename,
            status="pending",
            message="File created! Processing in background."
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error creating file: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.put("/{bucket_id}/files/{file_id}/content", response_model=FileUploadResponse)
async def update_created_file_content(
    bucket_id: str,
    file_id: str,
    request: FileContentUpdateRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id)
):
    """Update content of a created file and reprocess it."""
    try:
        supabase = get_supabase()

        file_res = supabase.table("files").select("id, name, source, storage_path, mime_type, size_bytes").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", user_id).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")

        if file_res.data.get("source") != "created":
            raise HTTPException(status_code=400, detail="Only created files can be edited")

        content_text = request.content or ""
        if not content_text.strip():
            raise HTTPException(status_code=400, detail="File content is required")

        content_bytes = content_text.encode("utf-8")
        existing_size = file_res.data.get("size_bytes") or 0
        await _enforce_update_limits(user_id, len(content_bytes), existing_size)

        storage_path = file_res.data["storage_path"]
        mime_type = file_res.data.get("mime_type") or "text/plain"

        try:
            supabase.storage.from_("files").remove([storage_path])
        except Exception:
            pass
        supabase.storage.from_("files").upload(storage_path, content_bytes)

        supabase.table("files").update({
            "size_bytes": len(content_bytes),
            "status": "pending",
            "status_message": None,
            "processed_at": None
        }).eq("id", file_id).execute()

        supabase.table("chunks").delete().eq("file_id", file_id).execute()

        background_tasks.add_task(
            process_file_background,
            file_id=file_id,
            storage_path=storage_path,
            filename=file_res.data.get("name"),
            mime_type=mime_type,
            user_id=user_id,
            bucket_id=bucket_id
        )

        return FileUploadResponse(
            id=str(file_id),
            name=file_res.data.get("name"),
            status="pending",
            message="File updated! Processing in background."
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error updating file content: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.get("/{bucket_id}/files", response_model=FilesListResponse)
async def list_files(
    bucket_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """List all files in a bucket"""
    t = Tracer("GET /api/buckets/{id}/files", user_id=user_id, bucket_id=bucket_id)
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission
        effective_uid = get_effective_user_id(user_id)
        t.step("get_effective_user_id")

        if not check_bucket_permission(user_id, bucket_id, "can_view"):
            raise HTTPException(status_code=403, detail="You don't have access to this bucket")

        supabase = get_supabase()

        bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        t.step("DB verify bucket")

        files_res = supabase.table("files").select("*").eq("bucket_id", bucket_id).order("created_at", desc=True).execute()
        t.step("DB query files", count=len(files_res.data) if files_res.data else 0)

        files = [
            FileResponse(
                id=str(f["id"]),
                bucket_id=str(f["bucket_id"]),
                name=f["name"],
                original_name=f["original_name"],
                mime_type=f["mime_type"],
                size_bytes=f["size_bytes"],
                status=f["status"],
                status_message=f.get("status_message"),
                page_count=f.get("page_count"),
                word_count=f.get("word_count"),
                folder_path=f.get("folder_path"),
                source=f.get("source"),
                progress_stage=f.get("progress_stage"),
                progress_label=f.get("progress_label"),
                progress_current=f.get("progress_current"),
                progress_total=f.get("progress_total"),
                progress_percent=float(f.get("progress_percent") or 0),
                progress_meta=f.get("progress_meta") or {},
                investigation_conversation_id=f.get("investigation_conversation_id"),
                auto_summary_posted_at=f.get("auto_summary_posted_at"),
                auto_summary_error=f.get("auto_summary_error"),
                uploaded_by_color=f.get("uploaded_by_color"),
                uploaded_by_name=f.get("uploaded_by_name"),
                created_at=f["created_at"],
                updated_at=f["updated_at"]
            )
            for f in files_res.data
        ]

        t.done()
        return FilesListResponse(files=files, total=len(files))

    except HTTPException:
        t.done(status_code=404)
        raise
    except Exception as e:
        t.error("list files failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.get("/{bucket_id}/files/progress")
async def list_file_progress(
    bucket_id: str,
    active_only: bool = Query(True),
    user_id: str = Depends(get_current_user_id),
):
    """Lightweight file progress feed for polling."""
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission
        effective_uid = get_effective_user_id(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_view"):
            raise HTTPException(status_code=403, detail="You don't have access to this bucket")

        supabase = get_supabase()
        try:
            supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")

        query = (
            supabase.table("files")
            .select(
                "id,name,status,status_message,progress_stage,progress_label,progress_current,"
                "progress_total,progress_percent,progress_meta,investigation_conversation_id,"
                "created_at,updated_at,progress_updated_at"
            )
            .eq("bucket_id", bucket_id)
            .order("created_at", desc=False)
        )
        if active_only:
            query = query.in_("status", ACTIVE_FILE_STATUSES)

        result = query.execute()
        return {"files": result.data or []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching file progress: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )



@router.get("/{bucket_id}/files/{file_id}/content")
async def get_file_content(
    bucket_id: str,
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get file content (summary + full text from chunks)"""
    t = Tracer("GET /api/buckets/{id}/files/{fid}/content", user_id=user_id, file_id=file_id)
    try:
        supabase = get_supabase()

        file_res = supabase.table("files").select("*").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", user_id).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")
        t.step("DB query file")

        file_data = file_res.data

        summary_res = supabase.table("summaries").select("content, title").eq("file_id", file_id).execute()
        summary = ""

        if summary_res.data and len(summary_res.data) > 0:
            summary = summary_res.data[0].get("content", "")
            t.step("Summary found in DB")
        else:
            t.step("No summary, generating on-demand")
            storage_path = file_data.get("storage_path")
            full_file_text = ""
            if storage_path:
                full_file_text = fetch_full_file_content(storage_path, supabase)
                t.step("Fetched full file for summary", chars=len(full_file_text) if full_file_text else 0)

            if full_file_text:
                analysis_data = analyze_file_comprehensive(full_file_text, file_data["name"])
                t.step("AI summary generated")
            else:
                chunks_for_summary = supabase.table("chunks").select("content").eq("file_id", file_id).order("chunk_index").limit(20).execute()
                if chunks_for_summary.data:
                    sample_text = "\n".join([c["content"] for c in chunks_for_summary.data])
                    analysis_data = analyze_file_comprehensive(sample_text, file_data["name"])
                    t.step("AI summary from chunks")
                else:
                    analysis_data = {"summary": "No content available for summary."}

            if analysis_data.get("summary"):
                summary_record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "bucket_id": bucket_id,
                    "file_id": file_id,
                    "summary_type": "file",
                    "title": file_data["name"],
                    "content": analysis_data["summary"],
                    "model_used": analysis_data.get("model_used")
                }
                supabase.table("summaries").insert(summary_record).execute()
                summary = analysis_data["summary"]
                t.step("Summary saved to DB")

        chunks_res = supabase.table("chunks").select("content, chunk_index").eq("file_id", file_id).order("chunk_index").execute()
        t.step("DB query chunks", count=len(chunks_res.data) if chunks_res.data else 0)

        full_text = ""
        if chunks_res.data:
            full_text = "\n".join([chunk["content"] for chunk in chunks_res.data])

        if (not chunks_res.data or len(full_text) < 100) and file_data.get("storage_path"):
            full_file_text = fetch_full_file_content(file_data["storage_path"], supabase)
            if full_file_text and len(full_file_text) > len(full_text):
                full_text = full_file_text
            t.step("Full file fallback", chars=len(full_text))

        t.done()
        return {
            "id": file_data["id"],
            "name": file_data["name"],
            "mime_type": file_data["mime_type"],
            "size_bytes": file_data["size_bytes"],
            "word_count": file_data.get("word_count"),
            "page_count": file_data.get("page_count"),
            "summary": summary,
            "content": full_text,
            "chunk_count": len(chunks_res.data) if chunks_res.data else 0
        }

    except HTTPException:
        t.done(status_code=404)
        raise
    except Exception as e:
        t.error("get file content failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error getting file content: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.put("/{bucket_id}/files/{file_id}/summary", response_model=dict)
async def update_file_summary(
    bucket_id: str,
    file_id: str,
    request: SummaryUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Update/edit the comprehensive analysis summary for a file"""
    try:
        supabase = get_supabase_auth()
        
        # Verify file belongs to user and bucket
        file_res = supabase.table("files").select("id, name").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", user_id).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get or create summary record
        summary_res = supabase.table("summaries").select("id").eq("file_id", file_id).eq("bucket_id", bucket_id).eq("user_id", user_id).single().execute()
        
        if summary_res.data:
            # Update existing summary
            summary_id = summary_res.data["id"]
            supabase.table("summaries").update({
                "content": request.content,
                "updated_at": "now()"
            }).eq("id", summary_id).execute()
        else:
            # Create new summary record
            summary_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "bucket_id": bucket_id,
                "file_id": file_id,
                "summary_type": "file",
                "title": file_res.data["name"],
                "content": request.content
            }
            supabase.table("summaries").insert(summary_record).execute()
        
        return {"success": True, "message": "Summary updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error updating summary: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.get("/{bucket_id}/search", response_model=SearchResponse)
async def search_files(
    bucket_id: str,
    q: str,
    user_id: str = Depends(get_current_user_id)
):
    """Search for keywords across chunks, summaries, and filenames"""
    try:
        supabase = get_supabase_auth()
        
        # Verify bucket belongs to user
        bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        search_results = []
        
        # Search in filenames (case-insensitive)
        files_res = supabase.table("files").select("id, name").eq("bucket_id", bucket_id).eq("user_id", user_id).ilike("name", f"%{q}%").execute()
        for file_data in files_res.data:
            search_results.append(SearchResult(
                file_id=str(file_data["id"]),
                file_name=file_data["name"],
                match_type="filename",
                content=f"Filename matches: {file_data['name']}"
            ))
        
        # Search in chunks using PostgreSQL full-text search (ilike for simple matching)
        chunks_res = supabase.table("chunks").select("id, content, file_id").eq("bucket_id", bucket_id).eq("user_id", user_id).ilike("content", f"%{q}%").execute()
        
        # Get file names for chunks
        chunk_file_ids = list(set([c["file_id"] for c in chunks_res.data]))
        chunk_file_names = {}
        if chunk_file_ids:
            chunk_files_res = supabase.table("files").select("id, name").in_("id", chunk_file_ids).execute()
            chunk_file_names = {f["id"]: f["name"] for f in chunk_files_res.data}
        
        for chunk in chunks_res.data:
            file_id = chunk.get("file_id")
            file_name = chunk_file_names.get(file_id, "Unknown")
            content = chunk.get("content", "")
            # Extract relevant snippet (context around match)
            content_lower = content.lower()
            q_lower = q.lower()
            idx = content_lower.find(q_lower)
            if idx != -1:
                start = max(0, idx - 100)
                end = min(len(content), idx + len(q) + 100)
                snippet = content[start:end]
            else:
                snippet = content[:200]
            
            search_results.append(SearchResult(
                file_id=str(file_id),
                file_name=file_name,
                match_type="chunk",
                content=snippet,
                chunk_id=str(chunk.get("id"))
            ))
        
        # Search in summaries
        summaries_res = supabase.table("summaries").select("id, content, file_id, title").eq("bucket_id", bucket_id).eq("user_id", user_id).ilike("content", f"%{q}%").execute()
        
        # Get file names for summaries
        summary_file_ids = list(set([s["file_id"] for s in summaries_res.data]))
        summary_file_names = {}
        if summary_file_ids:
            summary_files_res = supabase.table("files").select("id, name").in_("id", summary_file_ids).execute()
            summary_file_names = {f["id"]: f["name"] for f in summary_files_res.data}
        
        for summary in summaries_res.data:
            file_id = summary.get("file_id")
            file_name = summary_file_names.get(file_id, "Unknown")
            content = summary.get("content", "")
            # Extract relevant snippet
            content_lower = content.lower()
            q_lower = q.lower()
            idx = content_lower.find(q_lower)
            if idx != -1:
                start = max(0, idx - 100)
                end = min(len(content), idx + len(q) + 100)
                snippet = content[start:end]
            else:
                snippet = content[:200]
            
            search_results.append(SearchResult(
                file_id=str(file_id),
                file_name=file_name,
                match_type="summary",
                content=snippet,
                summary_id=str(summary.get("id"))
            ))
        
        return SearchResponse(
            query=q,
            results=search_results,
            total=len(search_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in search: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.get("/{bucket_id}/semantic-search", response_model=SearchResponse)
async def semantic_search_files(
    bucket_id: str,
    q: str,
    mode: str = Query("hybrid", description="Search mode: 'semantic', 'keyword', or 'hybrid'"),
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id)
):
    """
    Semantic search for similar content using vector embeddings.
    
    - **semantic**: Uses vector similarity (requires embeddings)
    - **keyword**: Traditional text search
    - **hybrid**: Combines both methods (recommended)
    """
    try:
        supabase = get_supabase()
        
        # Verify bucket belongs to user
        bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        search_results = []
        
        if mode == "semantic":
            results = await semantic_search(q, user_id, bucket_id, limit=limit)
        elif mode == "hybrid":
            results = await hybrid_search(q, user_id, bucket_id, limit=limit)
        else:
            # Keyword mode - fall back to existing search
            chunks_res = supabase.table("chunks").select("id, content, file_id, chunk_index").eq("bucket_id", bucket_id).eq("user_id", user_id).ilike("content", f"%{q}%").limit(limit).execute()
            results = [
                {
                    "chunk_id": c["id"],
                    "file_id": c["file_id"],
                    "content": c["content"],
                    "chunk_index": c.get("chunk_index"),
                    "similarity": None,
                    "match_type": "keyword"
                }
                for c in (chunks_res.data or [])
            ]
        
        # Get file names for results
        file_ids = list(set([r["file_id"] for r in results if r.get("file_id")]))
        file_names = {}
        if file_ids:
            files_res = supabase.table("files").select("id, name").in_("id", file_ids).execute()
            file_names = {f["id"]: f["name"] for f in (files_res.data or [])}
        
        # Format results
        for result in results:
            file_id = result.get("file_id")
            file_name = file_names.get(file_id, "Unknown")
            content = result.get("content", "")
            
            # Extract snippet around match (for keyword) or use first part
            snippet = content[:300] if len(content) > 300 else content
            
            search_results.append(SearchResult(
                file_id=str(file_id) if file_id else "",
                file_name=file_name,
                match_type=result.get("match_type", "semantic"),
                content=snippet,
                chunk_id=str(result.get("chunk_id")) if result.get("chunk_id") else None,
                relevance_score=result.get("similarity")
            ))
        
        return SearchResponse(
            query=q,
            results=search_results,
            total=len(search_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in semantic search: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.delete("/{bucket_id}/files/{file_id}")
async def delete_file(
    bucket_id: str,
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a file from a bucket"""
    t = Tracer("DELETE /api/buckets/{id}/files/{fid}", user_id=user_id, file_id=file_id)
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_delete"):
            raise HTTPException(status_code=403, detail="You don't have delete permission for this bucket")
        t.step("Permission check")

        supabase = get_supabase_auth()

        file_res = supabase.table("files").select("storage_path, name").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", effective_uid).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")
        t.step("DB query file")

        storage_path = file_res.data["storage_path"]
        file_name = file_res.data.get("name", "")
        get_supabase().storage.from_("files").remove([storage_path])
        t.step("Delete from storage")

        supabase.table("files").delete().eq("id", file_id).execute()
        t.step("DB delete file record")

        team_ctx = get_team_member_context(user_id)
        if team_ctx:
            log_team_activity(
                owner_id=effective_uid,
                member_id=user_id,
                team_member_id=team_ctx["team_member_id"],
                bucket_id=bucket_id,
                action_type="deleted_file",
                resource_id=file_id,
                resource_name=file_name,
                member_color=team_ctx["color"],
                member_name=team_ctx["name"],
            )

        t.done()
        return {"success": True, "message": "File deleted"}

    except HTTPException:
        t.done(status_code=404)
        raise
    except Exception as e:
        t.error("delete file failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )
