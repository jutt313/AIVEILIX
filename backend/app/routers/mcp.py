from fastapi import APIRouter, HTTPException, Header, Depends, Request
from typing import Optional, Dict, Any
from app.models.mcp import (
    MCPQueryRequest,
    MCPChatRequest,
    MCPBucketsListResponse,
    MCPBucketResponse,
    MCPFilesListResponse,
    MCPFileResponse,
    MCPQueryResponse,
    MCPQueryResult,
    MCPChatResponse,
    MCPSource
)
from app.services.supabase import get_supabase
from app.services.rate_limiter import enforce_rate_limit
from app.services.file_processor import generate_embedding, fetch_full_file_content
from app.config import get_settings
from app.routers.chat import deepseek_client, SYSTEM_PROMPT
import hashlib
import uuid
import logging
import traceback
import re
from datetime import datetime

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def sanitize_error_message(error: Exception) -> str:
    """Sanitize error messages to prevent leaking internal details"""
    error_str = str(error).lower()
    
    # Don't expose internal paths, stack traces, or sensitive info
    if "traceback" in error_str or "file" in error_str and "line" in error_str:
        return "An internal error occurred"
    
    # Generic sanitized messages
    if "database" in error_str or "sql" in error_str:
        return "Database error occurred"
    if "connection" in error_str or "timeout" in error_str:
        return "Service temporarily unavailable"
    
    return "An error occurred processing your request"


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format"""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


class APIKeyUser:
    """Container for API key user data"""
    def __init__(self, user_id: str, api_key_id: str, allowed_buckets: Optional[list], scopes: list):
        self.user_id = user_id
        self.api_key_id = api_key_id
        self.allowed_buckets = allowed_buckets  # None = all buckets, [] = specific buckets
        self.scopes = scopes


async def get_api_key_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> APIKeyUser:
    """
    Validate API key and return user information
    Raises 401 if invalid/expired/revoked
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header. Use: Authorization: Bearer <api_key>"
        )
    
    api_key = authorization.replace("Bearer ", "").strip()
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    # Hash the API key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    try:
        supabase = get_supabase()
        
        # Query API key by hash
        response = supabase.table("api_keys").select(
            "id, user_id, allowed_buckets, scopes, is_active, expires_at, request_count"
        ).eq("key_hash", key_hash).single().execute()
        
        if not response.data:
            logger.warning(f"Invalid API key attempt (hash not found)")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        key_data = response.data
        
        # Validate active status
        if not key_data.get("is_active", False):
            logger.warning(f"Revoked API key attempt: {key_data.get('id')}")
            raise HTTPException(status_code=401, detail="API key has been revoked")
        
        # Validate expiration
        expires_at = key_data.get("expires_at")
        if expires_at:
            from datetime import timezone
            if datetime.now(timezone.utc) > datetime.fromisoformat(expires_at.replace('Z', '+00:00')):
                logger.warning(f"Expired API key attempt: {key_data.get('id')}")
                raise HTTPException(status_code=401, detail="API key has expired")
        
        # Verify user exists
        user_id = str(key_data["user_id"])
        user_check = supabase.table("profiles").select("id").eq("id", user_id).single().execute()
        if not user_check.data:
            logger.error(f"API key references non-existent user: {user_id}")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Log successful authentication (for audit trail)
        logger.info(f"MCP API key authenticated: key_id={key_data.get('id')}, user_id={user_id}")
        
        # Enforce rate limiting
        api_key_id = str(key_data["id"])
        enforce_rate_limit(api_key_id)
        
        # Update usage tracking atomically
        try:
            current_count = key_data.get("request_count", 0)
            supabase.table("api_keys").update({
                "last_used_at": datetime.utcnow().isoformat(),
                "request_count": current_count + 1
            }).eq("id", api_key_id).execute()
        except Exception as e:
            logger.error(f"Failed to update API key usage for {api_key_id}: {e}")
            # Don't fail the request if usage tracking fails, but log it
        
        return APIKeyUser(
            user_id=user_id,
            api_key_id=api_key_id,
            allowed_buckets=key_data.get("allowed_buckets"),
            scopes=key_data.get("scopes", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"API key validation error: {error_trace}")
        raise HTTPException(
            status_code=401,
            detail="API key validation failed"
        )


def check_bucket_access(api_user: APIKeyUser, bucket_id: str, supabase) -> bool:
    """
    Check if API key has access to bucket
    Returns True if allowed, raises 403 if denied
    """
    # Verify bucket exists and belongs to user
    bucket_res = supabase.table("buckets").select("id, user_id").eq("id", bucket_id).single().execute()
    
    if not bucket_res.data:
        raise HTTPException(status_code=404, detail="Bucket not found")
    
    bucket_user_id = str(bucket_res.data["user_id"])
    
    # Check if bucket belongs to API key owner
    if bucket_user_id != api_user.user_id:
        logger.warning(f"Cross-user bucket access attempt: API key user {api_user.user_id} tried to access bucket {bucket_id} owned by {bucket_user_id}")
        raise HTTPException(status_code=403, detail="Access denied to this bucket")
    
    # Check allowed_buckets restriction
    if api_user.allowed_buckets is not None:  # None means all buckets allowed
        if bucket_id not in api_user.allowed_buckets:
            raise HTTPException(status_code=403, detail="API key does not have access to this bucket")
    
    return True


@router.get("/buckets", response_model=MCPBucketsListResponse)
async def list_buckets(api_user: APIKeyUser = Depends(get_api_key_user)):
    """List all accessible buckets for the API key"""
    try:
        supabase = get_supabase()
        
        # Get all buckets for user
        response = supabase.table("buckets").select(
            "id, name, description, file_count, total_size_bytes, created_at"
        ).eq("user_id", api_user.user_id).order("created_at", desc=True).execute()
        
        buckets_data = response.data if response.data else []
        
        # Filter by allowed_buckets if restricted
        if api_user.allowed_buckets is not None:
            # Filter to only allowed buckets
            allowed_set = set(api_user.allowed_buckets)
            buckets_data = [b for b in buckets_data if str(b["id"]) in allowed_set]
        
        buckets = [
            MCPBucketResponse(
                id=str(bucket["id"]),
                name=bucket["name"],
                description=bucket.get("description"),
                file_count=bucket.get("file_count", 0),
                total_size_bytes=bucket.get("total_size_bytes", 0),
                created_at=bucket["created_at"]
            )
            for bucket in buckets_data
        ]
        
        return MCPBucketsListResponse(buckets=buckets, total=len(buckets))
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"MCP list buckets error for API key {api_user.api_key_id}, user {api_user.user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=sanitize_error_message(e)
        )


@router.get("/buckets/{bucket_id}/files", response_model=MCPFilesListResponse)
async def list_files(
    bucket_id: str,
    api_user: APIKeyUser = Depends(get_api_key_user)
):
    """List files in a bucket"""
    try:
        # Validate UUID format
        if not validate_uuid(bucket_id):
            raise HTTPException(status_code=400, detail="Invalid bucket ID format")
        
        supabase = get_supabase()
        
        # Check bucket access
        check_bucket_access(api_user, bucket_id, supabase)
        
        # Get files
        response = supabase.table("files").select(
            "id, name, status, status_message, word_count, size_bytes, created_at"
        ).eq("bucket_id", bucket_id).eq("user_id", api_user.user_id).order("created_at", desc=True).execute()
        
        files_data = response.data if response.data else []
        
        files = [
            MCPFileResponse(
                id=str(file["id"]),
                name=file["name"],
                status=file.get("status", "unknown"),
                status_message=file.get("status_message"),
                word_count=file.get("word_count"),
                size_bytes=file.get("size_bytes", 0),
                created_at=file["created_at"]
            )
            for file in files_data
        ]
        
        return MCPFilesListResponse(files=files, total=len(files))
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"MCP list files error for bucket {bucket_id}, API key {api_user.api_key_id}, user {api_user.user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=sanitize_error_message(e)
        )


@router.post("/buckets/{bucket_id}/query", response_model=MCPQueryResponse)
async def query_bucket(
    bucket_id: str,
    request: MCPQueryRequest,
    api_user: APIKeyUser = Depends(get_api_key_user)
):
    """Search/query bucket content using semantic search"""
    try:
        # Validate UUID format
        if not validate_uuid(bucket_id):
            raise HTTPException(status_code=400, detail="Invalid bucket ID format")
        
        # Validate query length
        if len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        supabase = get_supabase()
        
        # Check bucket access
        check_bucket_access(api_user, bucket_id, supabase)
        
        # Generate embedding for query
        try:
            query_embedding = generate_embedding(request.query)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            query_embedding = None
        
        # Try vector search if embedding available
        chunks_data = []
        if query_embedding:
            try:
                # Try RPC function for vector search (if exists)
                chunks_res = supabase.rpc(
                    "match_chunks",
                    {
                        "query_embedding": query_embedding,
                        "bucket_id": bucket_id,
                        "match_threshold": 0.5,
                        "match_count": request.max_results
                    }
                ).execute()
                if chunks_res.data:
                    chunks_data = chunks_res.data
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to text search: {e}")
        
        # Fallback to text search if vector search fails or no embedding
        if not chunks_data:
            # Simple text search fallback - search in content
            query_lower = request.query.lower()
            all_chunks_res = supabase.table("chunks").select(
                "id, content, file_id, bucket_id"
            ).eq("bucket_id", bucket_id).eq("user_id", api_user.user_id).execute()
            
            if all_chunks_res.data:
                # Simple text matching
                matching_chunks = []
                for chunk in all_chunks_res.data:
                    content = chunk.get("content", "").lower()
                    if query_lower in content:
                        matching_chunks.append(chunk)
                        if len(matching_chunks) >= request.max_results:
                            break
                chunks_data = matching_chunks
        
        # Get file names
        file_ids = list(set([chunk.get("file_id") for chunk in chunks_data if chunk.get("file_id")]))
        file_names = {}
        if file_ids:
            files_res = supabase.table("files").select("id, name").in_("id", file_ids).execute()
            if files_res.data:
                file_names = {str(f["id"]): f["name"] for f in files_res.data}
        
        # Build results
        results = []
        for chunk in chunks_data:
            file_id = str(chunk.get("file_id", ""))
            file_name = file_names.get(file_id, "Unknown")
            content = chunk.get("content", "")[:1000]  # Limit content length
            # Use similarity if available from vector search, otherwise calculate simple relevance
            if chunk.get("similarity"):
                relevance_score = float(chunk.get("similarity"))
            else:
                # Simple relevance: count query terms in content
                query_terms = request.query.lower().split()
                content_lower = content.lower()
                matches = sum(1 for term in query_terms if term in content_lower)
                relevance_score = min(1.0, matches / max(len(query_terms), 1))
            
            results.append(MCPQueryResult(
                file_id=file_id,
                file_name=file_name,
                content=content,
                relevance_score=relevance_score,
                chunk_id=str(chunk.get("id", ""))
            ))
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        results = results[:request.max_results]
        
        return MCPQueryResponse(
            results=results,
            total=len(results),
            query=request.query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"MCP query error for bucket {bucket_id}, API key {api_user.api_key_id}, user {api_user.user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=sanitize_error_message(e)
        )


@router.post("/buckets/{bucket_id}/chat", response_model=MCPChatResponse)
async def chat_with_bucket(
    bucket_id: str,
    request: MCPChatRequest,
    api_user: APIKeyUser = Depends(get_api_key_user)
):
    """Chat with bucket using AI"""
    try:
        # Validate UUID format
        if not validate_uuid(bucket_id):
            raise HTTPException(status_code=400, detail="Invalid bucket ID format")
        
        # Validate message
        if len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not deepseek_client:
            raise HTTPException(status_code=503, detail="AI service is not available")
        
        supabase = get_supabase()
        
        # Check bucket access
        check_bucket_access(api_user, bucket_id, supabase)
        
        # Get bucket info
        bucket_res = supabase.table("buckets").select("id, name").eq("id", bucket_id).eq("user_id", api_user.user_id).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Get ALL files from bucket (include storage_path for full file access)
        all_files_res = supabase.table("files").select("id, name, status, status_message, folder_path, storage_path").eq("bucket_id", bucket_id).eq("user_id", api_user.user_id).execute()
        all_files = all_files_res.data if all_files_res.data else []
        file_names = {f["id"]: f["name"] for f in all_files}
        file_storage_paths = {f["id"]: f.get("storage_path") for f in all_files}
        all_file_ids = [f["id"] for f in all_files]
        
        # Get chunks and summaries
        chunks_res = supabase.table("chunks").select("id, content, file_id").eq("bucket_id", bucket_id).eq("user_id", api_user.user_id).execute()
        summaries_res = supabase.table("summaries").select("id, content, file_id, title").eq("bucket_id", bucket_id).eq("user_id", api_user.user_id).execute()
        
        # Organize by file
        chunks_by_file = {}
        if chunks_res.data:
            for chunk in chunks_res.data:
                file_id = chunk.get("file_id")
                if file_id not in chunks_by_file:
                    chunks_by_file[file_id] = []
                chunks_by_file[file_id].append(chunk)
        
        summaries_by_file = {}
        if summaries_res.data:
            for summary in summaries_res.data:
                file_id = summary.get("file_id")
                summaries_by_file[file_id] = summary
        
        # Build context
        context_parts = []
        sources = []
        processed_files = []
        unprocessed_files = []
        
        for file in all_files:
            file_id = file["id"]
            file_name = file_names.get(file_id, "Unknown")
            if file.get("status") == "ready" and file_id in chunks_by_file:
                processed_files.append(file_name)
            else:
                unprocessed_files.append({
                    "name": file_name,
                    "status": file.get("status", "unknown"),
                    "message": file.get("status_message", "Not processed")
                })
        
        # Build file inventory
        file_inventory = f"[File Inventory - Total: {len(all_files)} files]\n"
        if processed_files:
            file_inventory += f"Processed files ({len(processed_files)}): {', '.join(processed_files)}\n"
        if unprocessed_files:
            file_inventory += f"\nUnprocessed files ({len(unprocessed_files)}):\n"
            for up_file in unprocessed_files:
                file_inventory += f"  - {up_file['name']} (status: {up_file['status']}, reason: {up_file['message']})\n"
        
        # Add content from processed files
        for file_id in all_file_ids:
            file_name = file_names.get(file_id, "Unknown")
            storage_path = file_storage_paths.get(file_id)
            
            # Add analysis if available
            if file_id in summaries_by_file:
                summary = summaries_by_file[file_id]
                analysis_content = summary.get("content", "")
                summary_id = summary.get("id")
                context_parts.append(f"[Analysis: {file_name}]\n{analysis_content}")
                sources.append(MCPSource(
                    file_name=file_name,
                    file_id=str(file_id),
                    type="analysis",
                    summary_id=str(summary_id)
                ))
            
            # Add chunks if available
            has_chunks = file_id in chunks_by_file
            if has_chunks:
                chunks_for_file = chunks_by_file[file_id]
                chunk_contents = []
                total_chunk_chars = 0
                for chunk in chunks_for_file[:5]:  # Limit chunks per file
                    content = chunk.get("content", "")
                    chunk_id = chunk.get("id")
                    chunk_contents.append(content[:1000])
                    total_chunk_chars += len(content)
                    sources.append(MCPSource(
                        file_name=file_name,
                        file_id=str(file_id),
                        type="chunk",
                        chunk_id=str(chunk_id)
                    ))
                if chunk_contents:
                    raw_content = "\n".join(chunk_contents)
                    context_parts.append(f"[Content: {file_name}]\n{raw_content}")
                
                # INTELLIGENT FALLBACK for MCP: If chunks are insufficient, fetch full file
                if total_chunk_chars < 500 and storage_path:
                    logger.info(f"🔍 MCP: Chunks limited for '{file_name}'. Fetching full file...")
                    full_content = fetch_full_file_content(storage_path, supabase)
                    if full_content and len(full_content) > total_chunk_chars:
                        logger.info(f"  ✅ MCP: Full file fetched: {len(full_content)} chars")
                        context_parts.append(f"[FULL CONTENT: {file_name}]\n{full_content[:8000]}")  # Cap at 8k for MCP
                        sources.append(MCPSource(
                            file_name=file_name,
                            file_id=str(file_id),
                            type="full_file"
                        ))
            elif storage_path:
                # No chunks? Try full file directly
                logger.info(f"📥 MCP: No chunks for '{file_name}'. Fetching full file...")
                full_content = fetch_full_file_content(storage_path, supabase)
                if full_content:
                    logger.info(f"  ✅ MCP: Full file fetched: {len(full_content)} chars")
                    context_parts.append(f"[FULL CONTENT: {file_name}]\n{full_content[:8000]}")
                    sources.append(MCPSource(
                        file_name=file_name,
                        file_id=str(file_id),
                        type="full_file"
                    ))
        
        # Combine context
        if context_parts:
            full_context = file_inventory + "\n\n" + "\n\n".join(context_parts)
        else:
            full_context = file_inventory + "\n\nNo file content available for analysis."
        
        # Create or get conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conv_res = supabase.table("conversations").insert({
                "id": str(uuid.uuid4()),
                "user_id": api_user.user_id,
                "bucket_id": bucket_id,
                "title": request.message[:50],
                "mode": "mcp"
            }).execute()
            conversation_id = conv_res.data[0]["id"]
        
        # Get previous messages
        previous_messages = []
        if conversation_id:
            prev_msgs_res = supabase.table("messages").select("role, content").eq("conversation_id", conversation_id).order("created_at", desc=False).limit(10).execute()
            if prev_msgs_res.data:
                previous_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in prev_msgs_res.data
                ]
        
        # Save user message
        supabase.table("messages").insert({
            "id": str(uuid.uuid4()),
            "user_id": api_user.user_id,
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.message
        }).execute()
        
        # Build AI messages
        ai_messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + full_context}
        ]
        ai_messages.extend(previous_messages)
        ai_messages.append({"role": "user", "content": request.message})
        
        # Get AI response
        try:
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=ai_messages,
                temperature=0.7,
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                raise HTTPException(
                    status_code=429,
                    detail="AI service quota exceeded. Please try again later."
                )
            logger.error(f"DeepSeek API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="AI service error"
            )
        
        # Save assistant message
        supabase.table("messages").insert({
            "id": str(uuid.uuid4()),
            "user_id": api_user.user_id,
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_response,
            "model_used": "deepseek-chat",
            "sources": [{"file_name": s.file_name, "file_id": s.file_id, "type": s.type} for s in sources[:10]]
        }).execute()
        
        return MCPChatResponse(
            response=ai_response,
            sources=sources[:10],
            conversation_id=str(conversation_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"MCP chat error for bucket {bucket_id}, API key {api_user.api_key_id}, user {api_user.user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=sanitize_error_message(e)
        )
