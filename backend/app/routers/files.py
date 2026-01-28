from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Header, Form, Query
from typing import Optional, List, Dict
from app.models.files import FileResponse, FilesListResponse, FileUploadResponse, SummaryUpdateRequest, SearchResponse, SearchResult
from app.models.buckets import BucketResponse
from app.services.supabase import get_supabase_auth, get_supabase
from app.services.file_processor import extract_text_from_file, chunk_text, generate_embedding, generate_embeddings_batch, generate_summary, analyze_file_comprehensive, fetch_full_file_content
from app.services.semantic_search import semantic_search, hybrid_search
from app.services.notifications import create_file_uploaded_notification, create_file_processed_notification
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

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


async def process_file_async(
    file_id: str,
    temp_file_path: str,
    filename: str,
    mime_type: str,
    user_id: str,
    bucket_id: str,
    supabase,
    skip_ai_summary: bool = True  # Skip AI summary by default for speed
) -> Dict:
    """Async helper function to process a single file (extract text, create chunks, optionally generate analysis)"""
    logger.info("=" * 80)
    logger.info(f"📄 Processing file: {filename}")
    logger.info(f"   File ID: {file_id}")
    logger.info(f"   MIME Type: {mime_type}")
    logger.info(f"   Skip AI Summary: {skip_ai_summary}")
    
    try:
        # Extract text
        logger.info(f"  1️⃣  Extracting text from {filename}...")
        text_data = extract_text_from_file(temp_file_path, mime_type)
        text = text_data["text"]
        metadata = text_data["metadata"]
        
        logger.info(f"  ✅ Text extracted: {len(text)} chars, {metadata.get('word_count', 0)} words")
        
        # Only process if we got text content
        if not text or len(text.strip()) == 0:
            logger.error(f"  ❌ No text content extracted from {filename}")
            raise Exception("No text content extracted from file")
        
        # Create chunks
        logger.info(f"  2️⃣  Creating text chunks...")
        chunks = chunk_text(text)
        logger.info(f"  ✅ Created {len(chunks)} chunks")
        
        # Generate embeddings in BATCH (much faster than one-by-one)
        logger.info(f"  3️⃣  Generating embeddings for {len(chunks)} chunks...")
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = generate_embeddings_batch(chunk_texts)
        
        # Store chunks with embeddings
        logger.info(f"  4️⃣  Storing chunks in database...")
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
        
        # Generate AI summary only if requested (lazy loading)
        if not skip_ai_summary:
            logger.info(f"  5️⃣  Generating AI summary...")
            analysis_data = analyze_file_comprehensive(text, filename)
            if analysis_data.get("summary"):
                summary_record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "bucket_id": bucket_id,
                    "file_id": file_id,
                    "summary_type": "file",
                    "title": filename,
                    "content": analysis_data["summary"],
                    "model_used": analysis_data.get("model_used")
                }
                supabase.table("summaries").insert(summary_record).execute()
                logger.info(f"  ✅ AI summary generated and stored")
        else:
            logger.info(f"  ⏭️  Skipping AI summary (will generate on-demand)")
        
        # Update file status to ready
        logger.info(f"  6️⃣  Updating file status to 'ready'...")
        supabase.table("files").update({
            "status": "ready",
            "processed_at": "now()",
            "page_count": metadata.get("page_count"),
            "word_count": metadata.get("word_count")
        }).eq("id", file_id).execute()
        
        logger.info(f"✅ File processed successfully: {filename}")
        logger.info("=" * 80)
        
        # Create file processed notification
        create_file_processed_notification(user_id, filename, bucket_id, file_id)
        
        return {
            "file_id": file_id,
            "status": "ready",
            "metadata": metadata
        }
    except Exception as e:
        error_message = str(e)
        logger.error("=" * 80)
        logger.error(f"❌ File processing FAILED for {filename} (file_id: {file_id})")
        logger.error(f"   Error: {error_message}")
        logger.error(f"   Traceback:", exc_info=True)
        logger.error("=" * 80)
        
        # Update file status to failed with error tracking
        supabase.table("files").update({
            "status": "failed",
            "status_message": f"Processing failed: {error_message[:200]}",
            "processed_at": "now()"
        }).eq("id", file_id).execute()
        
        return {
            "file_id": file_id,
            "status": "failed",
            "error": error_message
        }


@router.post("/{bucket_id}/upload", response_model=FileUploadResponse)
async def upload_file(
    bucket_id: str,
    file: UploadFile = File(...),
    folder_path: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    """Upload a file to a bucket - handles any file type, marks as failed if processing fails"""
    try:
        # Use service role for bucket verification to avoid RLS propagation delays
        supabase = get_supabase()
        
        # Verify bucket belongs to user
        try:
            bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Save file temporarily
        file_ext = Path(file.filename).suffix
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        file_id = None
        storage_path = None
        
        try:
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Store file in Supabase Storage first (always save the file)
            storage_path = f"{user_id}/{bucket_id}/{uuid.uuid4()}{file_ext}"
            with open(temp_file.name, 'rb') as f:
                supabase.storage.from_("files").upload(storage_path, f.read())
            
            # Extract just the filename (remove folder path if present in filename)
            filename = file.filename
            if '/' in filename:
                filename = filename.split('/')[-1]
            
            # Create file record with pending status
            file_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "bucket_id": bucket_id,
                "name": filename,
                "original_name": filename,
                "mime_type": file.content_type,
                "size_bytes": len(content),
                "storage_path": storage_path,
                "status": "processing"
            }
            
            # Add folder_path if provided
            if folder_path:
                file_record["folder_path"] = folder_path
            
            file_res = supabase.table("files").insert(file_record).execute()
            file_id = file_res.data[0]["id"]
            
            # Create file uploaded notification
            create_file_uploaded_notification(user_id, filename, bucket_id, file_id)
            
            # Process the file using async helper
            process_result = await process_file_async(
                file_id=file_id,
                temp_file_path=temp_file.name,
                filename=file.filename,
                mime_type=file.content_type,
                user_id=user_id,
                bucket_id=bucket_id,
                supabase=supabase
            )
            
            if process_result["status"] == "ready":
                return FileUploadResponse(
                    id=file_id,
                    name=file.filename,
                    status="ready",
                    message="File uploaded and processed successfully"
                )
            else:
                return FileUploadResponse(
                    id=file_id,
                    name=file.filename,
                    status="failed",
                    message=f"File uploaded but processing failed: {process_result.get('error', 'Unknown error')}"
                )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in files router: {error_trace}")
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
        # Use service role for backend operations
        supabase = get_supabase()
        
        # Verify bucket belongs to user
        bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
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
        supabase = get_supabase_auth()
        
        # Verify file belongs to user and bucket
        file_res = supabase.table("files").select("storage_path").eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", user_id).single().execute()
        if not file_res.data:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from storage
        storage_path = file_res.data["storage_path"]
        get_supabase().storage.from_("files").remove([storage_path])
        
        # Delete file record (cascade will delete chunks)
        supabase.table("files").delete().eq("id", file_id).execute()
        
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
