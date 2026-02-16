from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Header, Form, Query, BackgroundTasks
from typing import Optional, List, Dict
from app.models.files import FileResponse, FilesListResponse, FileUploadResponse, SummaryUpdateRequest, SearchResponse, SearchResult, CreateFileRequest, FileContentUpdateRequest
from app.models.buckets import BucketResponse
from app.services.supabase import get_supabase_auth, get_supabase
from app.services.file_processor import extract_text_from_file, chunk_text, generate_embedding, generate_embeddings_batch, generate_summary, analyze_file_comprehensive, fetch_full_file_content, enrich_summary_with_web_search
from app.services.semantic_search import semantic_search, hybrid_search
from app.services.notifications import create_file_uploaded_notification, create_file_processed_notification
from app.services.plan_limits import check_all_upload_limits, check_file_size_limit, check_storage_limit
from postgrest.exceptions import APIError as PostgrestAPIError
import asyncio
from app.routers.buckets import get_current_user_id
from app.config import get_settings
import uuid
import os
import hashlib
import tempfile
import logging
import traceback
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import sentry_sdk
import re
import io
import zipfile
import fitz

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

ALLOWED_CREATED_FILE_EXTENSIONS = {".md", ".txt"}
IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}


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
    supabase
) -> Dict:
    """
    Inner function that does the actual processing with retry support.
    Retries on transient errors (connection, timeout, OS errors).
    """
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

    try:
        # Extract text
        logger.info(f"  2️⃣  Extracting text from {filename}...")
        text_data = extract_text_from_file(temp_file_path, mime_type)
        text = text_data["text"]
        metadata = text_data["metadata"]

        logger.info(f"  ✅ Text extracted: {len(text)} chars, {metadata.get('word_count', 0)} words")

        # Only process if we got text content
        if not text or len(text.strip()) == 0:
            raise ValueError("No text content extracted from file")

        # Create chunks
        logger.info(f"  3️⃣  Creating text chunks...")
        chunks = chunk_text(text)
        logger.info(f"  ✅ Created {len(chunks)} chunks")

        # Generate embeddings in BATCH (much faster than one-by-one)
        logger.info(f"  4️⃣  Generating embeddings for {len(chunks)} chunks...")
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = generate_embeddings_batch(chunk_texts)

        # Store chunks with embeddings
        logger.info(f"  5️⃣  Storing chunks in database...")
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

        # Batch insert chunks
        if chunk_records:
            supabase.table("chunks").insert(chunk_records).execute()
            logger.info(f"  ✅ Stored {len(chunk_records)} chunks")

        return {"metadata": metadata, "chunks_count": len(chunk_records)}

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

    # Get fresh supabase client for background task
    supabase = get_supabase()

    try:
        # Update status to processing
        supabase.table("files").update({
            "status": "processing"
        }).eq("id", file_id).execute()

        # Process with retry logic
        result = _process_file_with_retry(
            file_id=file_id,
            storage_path=storage_path,
            filename=filename,
            mime_type=mime_type,
            user_id=user_id,
            bucket_id=bucket_id,
            supabase=supabase
        )

        metadata = result["metadata"]

        # Generate comprehensive summary during processing
        logger.info(f"  6️⃣  Generating comprehensive summary...")
        try:
            # Get the extracted text from chunks for summary
            chunks_res = supabase.table("chunks").select("content").eq(
                "file_id", file_id
            ).order("chunk_index").execute()
            full_text = " ".join([c["content"] for c in (chunks_res.data or [])])

            if full_text and len(full_text.strip()) > 50:
                summary_result = analyze_file_comprehensive(full_text, filename)
                summary_text = summary_result.get("summary", "")

                # Enrich with web search
                import asyncio
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

                # Store summary
                supabase.table("summaries").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "bucket_id": bucket_id,
                    "file_id": file_id,
                    "summary_type": "file",
                    "title": f"Analysis: {filename}",
                    "content": summary_text,
                    "model_used": summary_result.get("model_used", "deepseek-chat")
                }).execute()
                logger.info(f"  ✅ Summary stored ({len(summary_text)} chars)")
        except Exception as summary_err:
            logger.warning(f"Summary generation failed (non-critical): {summary_err}")

        # Update file status to ready
        logger.info(f"  7️⃣  Updating file status to 'ready'...")
        supabase.table("files").update({
            "status": "ready",
            "processed_at": "now()",
            "page_count": metadata.get("page_count"),
            "word_count": metadata.get("word_count")
        }).eq("id", file_id).execute()

        logger.info(f"✅ BACKGROUND PROCESSING COMPLETE: {filename}")
        logger.info("=" * 80)

        # Create file processed notification
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

        # Update file status to failed with error tracking
        try:
            supabase.table("files").update({
                "status": "failed",
                "status_message": f"Processing failed: {error_message[:200]}",
                "processed_at": "now()"
            }).eq("id", file_id).execute()
        except Exception as update_error:
            logger.error(f"Failed to update file status: {update_error}")


@router.post("/{bucket_id}/upload", response_model=FileUploadResponse)
async def upload_file(
    bucket_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    folder_path: Optional[str] = Form(None),
    batch_count: Optional[int] = Form(None),
    batch_total_bytes: Optional[int] = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    """
    Upload a file to a bucket - INSTANT RESPONSE.

    File is saved to storage immediately, processing happens in background.
    Chat AI can read unprocessed files directly from storage.
    """
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)
        team_ctx = get_team_member_context(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_upload"):
            raise HTTPException(status_code=403, detail="You don't have upload permission for this bucket")

        # Use service role for bucket verification to avoid RLS propagation delays
        supabase = get_supabase()

        # Verify bucket belongs to effective user (owner)
        try:
            bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")

        # Read file content
        content = await file.read()
        file_ext = Path(file.filename).suffix

        image_count = _count_images_in_file(content, file.content_type or "", file.filename or "")
        effective_batch_count = max(1, int(batch_count or 1))
        effective_batch_total = int(batch_total_bytes or len(content))

        # Check plan limits before upload (storage, document count, file size, image/file, batch)
        await check_all_upload_limits(
            user_id,
            len(content),
            batch_count=effective_batch_count,
            batch_total_bytes=effective_batch_total,
            image_count=image_count
        )

        # Store file in Supabase Storage (this is fast)
        storage_path = f"{user_id}/{bucket_id}/{uuid.uuid4()}{file_ext}"
        supabase.storage.from_("files").upload(storage_path, content)

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
            "source": "uploaded"
        }

        # Track which team member uploaded
        if team_ctx:
            file_record["uploaded_by_member_id"] = team_ctx["team_member_id"]
            file_record["uploaded_by_color"] = team_ctx["color"]
            file_record["uploaded_by_name"] = team_ctx["name"]

        # Add folder_path if provided
        if folder_path:
            file_record["folder_path"] = folder_path

        supabase.table("files").insert(file_record).execute()

        # Create file uploaded notification
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

        logger.info(f"⚡ INSTANT UPLOAD: {filename} (processing in background)")

        # Return immediately - user sees file instantly
        return FileUploadResponse(
            id=file_id,
            name=filename,
            status="pending",
            message="File uploaded! Processing in background. You can chat about it now."
        )

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
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
            "source": "uploaded"
        }

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
            detail=f"Internal server error: {str(e)}"
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
            detail=f"Internal server error: {str(e)}"
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
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{bucket_id}/files", response_model=FilesListResponse)
async def list_files(
    bucket_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """List all files in a bucket"""
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission
        effective_uid = get_effective_user_id(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_view"):
            raise HTTPException(status_code=403, detail="You don't have access to this bucket")

        # Use service role for backend operations
        supabase = get_supabase()

        # Verify bucket belongs to effective user
        bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")

        files_res = supabase.table("files").select("*").eq("bucket_id", bucket_id).order("created_at", desc=True).execute()

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
                uploaded_by_color=f.get("uploaded_by_color"),
                uploaded_by_name=f.get("uploaded_by_name"),
                created_at=f["created_at"],
                updated_at=f["updated_at"]
            )
            for f in files_res.data
        ]

        return FilesListResponse(files=files, total=len(files))
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{bucket_id}/files/{file_id}/content")
async def get_file_content(
    bucket_id: str,
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get file content (summary + full text from chunks)"""
    try:
        supabase = get_supabase()
        
        # Verify file belongs to user and bucket
        file_res = supabase.table("files").select("*").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", user_id).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_data = file_res.data
        
        # Get summary (or generate on-demand if not exists)
        summary_res = supabase.table("summaries").select("content, title").eq("file_id", file_id).execute()
        summary = ""
        
        if summary_res.data and len(summary_res.data) > 0:
            summary = summary_res.data[0].get("content", "")
        else:
            # Generate AI summary on-demand (lazy loading)
            logger.info(f"💡 Generating AI summary on-demand for file {file_id}")
            
            # NEW: First try to get full file for better summary
            storage_path = file_data.get("storage_path")
            full_file_text = ""
            if storage_path:
                logger.info(f"  📥 Fetching full file from storage for complete summary...")
                full_file_text = fetch_full_file_content(storage_path, supabase)
            
            # If full file fetch successful, use it; otherwise fall back to chunks
            if full_file_text:
                logger.info(f"  ✅ Using full file content ({len(full_file_text)} chars) for summary")
                analysis_data = analyze_file_comprehensive(full_file_text, file_data["name"])
            else:
                logger.info(f"  ⚠️  Full file not available, using chunks for summary")
                chunks_for_summary = supabase.table("chunks").select("content").eq("file_id", file_id).order("chunk_index").limit(20).execute()
                if chunks_for_summary.data:
                    sample_text = "\n".join([c["content"] for c in chunks_for_summary.data])
                    analysis_data = analyze_file_comprehensive(sample_text, file_data["name"])
                else:
                    analysis_data = {"summary": "No content available for summary."}
            
            if analysis_data.get("summary"):
                # Store the generated summary
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
        
        # Get all chunks ordered by chunk_index to reconstruct full text
        chunks_res = supabase.table("chunks").select("content, chunk_index").eq("file_id", file_id).order("chunk_index").execute()
        
        # Reconstruct full text from chunks (or fetch full file if chunks insufficient)
        full_text = ""
        if chunks_res.data:
            full_text = "\n".join([chunk["content"] for chunk in chunks_res.data])
        
        # NEW: If no chunks or chunks seem incomplete, try fetching full file
        if (not chunks_res.data or len(full_text) < 100) and file_data.get("storage_path"):
            logger.info(f"📥 Chunks insufficient for '{file_data['name']}', fetching full file...")
            full_file_text = fetch_full_file_content(file_data["storage_path"], supabase)
            if full_file_text and len(full_file_text) > len(full_text):
                logger.info(f"  ✅ Using full file content: {len(full_file_text)} chars")
                full_text = full_file_text
        
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
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error getting file content: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
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
            detail=f"Internal server error: {str(e)}"
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
            detail=f"Internal server error: {str(e)}"
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
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{bucket_id}/files/{file_id}")
async def delete_file(
    bucket_id: str,
    file_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a file from a bucket"""
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_delete"):
            raise HTTPException(status_code=403, detail="You don't have delete permission for this bucket")

        supabase = get_supabase_auth()

        # Verify file belongs to effective user and bucket
        file_res = supabase.table("files").select("storage_path, name").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", effective_uid).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from storage
        storage_path = file_res.data["storage_path"]
        file_name = file_res.data.get("name", "")
        get_supabase().storage.from_("files").remove([storage_path])

        # Delete file record (cascade will delete chunks)
        supabase.table("files").delete().eq("id", file_id).execute()

        # Log team activity
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

        return {"success": True, "message": "File deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
