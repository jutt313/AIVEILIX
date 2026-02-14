"""
MCP Service Layer

Business logic extracted from REST endpoints for reuse by MCP protocol handlers.
Avoids HTTP overhead when MCP tools call these services directly.
"""
import logging
import uuid
import re
from typing import Optional, List, Dict, Any
from app.services.supabase import get_supabase
from app.services.file_processor import generate_embedding, fetch_full_file_content
from app.models.mcp import (
    MCPBucketResponse,
    MCPFileResponse,
    MCPQueryResult,
    MCPSource,
)
from app.models.oauth import MCPUser
from datetime import datetime

logger = logging.getLogger(__name__)


def sanitize_error(error: Exception) -> str:
    """Remove sensitive info from errors before logging"""
    msg = str(error)
    # Remove DB URLs with passwords
    msg = re.sub(r'postgresql://[^:]+:[^@]+@[^/]+', 'postgresql://[REDACTED]', msg)
    # Remove API keys
    msg = re.sub(r'(sk-|AIza)[a-zA-Z0-9_-]{20,}', '[REDACTED]', msg)
    return msg


class MCPServiceError(Exception):
    """Custom exception for MCP service errors"""
    def __init__(self, message: str, code: str = "internal_error"):
        self.message = message
        self.code = code
        super().__init__(message)


async def list_buckets_service(user: MCPUser) -> List[MCPBucketResponse]:
    """
    List all accessible buckets for a user.
    
    Args:
        user: Authenticated MCP user
        
    Returns:
        List of bucket responses
    """
    try:
        supabase = get_supabase()
        
        # Get all buckets for user
        response = supabase.table("buckets").select(
            "id, name, description, file_count, total_size_bytes, created_at"
        ).eq("user_id", user.user_id).order("created_at", desc=True).execute()
        
        buckets_data = response.data if response.data else []
        
        # Filter by allowed_buckets if restricted (API key access)
        if user.allowed_buckets is not None:
            allowed_set = set(user.allowed_buckets)
            buckets_data = [b for b in buckets_data if str(b["id"]) in allowed_set]
        
        return [
            MCPBucketResponse(
                id=str(bucket["id"]),
                name=bucket["name"],
                description=bucket.get("description"),
                file_count=bucket.get("file_count", 0),
                total_size_bytes=bucket.get("total_size_bytes", 0),
                created_at=datetime.fromisoformat(bucket["created_at"].replace("Z", "+00:00"))
            )
            for bucket in buckets_data
        ]
    except Exception as e:
        logger.error(f"Error listing buckets for user {user.user_id}: {sanitize_error(e)}")
        raise MCPServiceError("Failed to list buckets", "bucket_list_error")


async def list_files_service(bucket_id: str, user: MCPUser) -> List[MCPFileResponse]:
    """
    List files in a bucket.
    
    Args:
        bucket_id: Bucket UUID
        user: Authenticated MCP user
        
    Returns:
        List of file responses
    """
    try:
        supabase = get_supabase()
        
        # Get files
        response = supabase.table("files").select(
            "id, name, status, status_message, word_count, size_bytes, storage_path, created_at"
        ).eq("bucket_id", bucket_id).eq("user_id", user.user_id).order("created_at", desc=True).execute()
        
        files_data = response.data if response.data else []
        
        return [
            MCPFileResponse(
                id=str(file["id"]),
                name=file["name"],
                status=file.get("status", "unknown"),
                status_message=file.get("status_message"),
                word_count=file.get("word_count"),
                size_bytes=file.get("size_bytes", 0),
                created_at=datetime.fromisoformat(file["created_at"].replace("Z", "+00:00"))
            )
            for file in files_data
        ]
    except Exception as e:
        logger.error(f"Error listing files for bucket {bucket_id}: {sanitize_error(e)}")
        raise MCPServiceError("Failed to list files", "file_list_error")


async def query_bucket_service(
    bucket_id: str,
    query: str,
    user: MCPUser,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search/query bucket content using semantic search.
    
    Args:
        bucket_id: Bucket UUID
        query: Search query text
        user: Authenticated MCP user
        max_results: Maximum number of results
        
    Returns:
        Dict with results, total, and query
    """
    try:
        supabase = get_supabase()
        
        # Generate embedding for query
        query_embedding = None
        try:
            query_embedding = generate_embedding(query)
        except Exception as e:
            logger.warning(f"Failed to generate embedding for query: {e}")
        
        # Try vector search if embedding available
        chunks_data = []
        if query_embedding:
            try:
                chunks_res = supabase.rpc(
                    "match_chunks",
                    {
                        "query_embedding": query_embedding,
                        "bucket_id": bucket_id,
                        "match_threshold": 0.5,
                        "match_count": max_results
                    }
                ).execute()
                if chunks_res.data:
                    chunks_data = chunks_res.data
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to text search: {e}")
        
        # Fallback to text search if vector search fails
        if not chunks_data:
            query_lower = query.lower()
            all_chunks_res = supabase.table("chunks").select(
                "id, content, file_id, bucket_id"
            ).eq("bucket_id", bucket_id).eq("user_id", user.user_id).execute()
            
            if all_chunks_res.data:
                matching_chunks = []
                for chunk in all_chunks_res.data:
                    content = chunk.get("content", "").lower()
                    if query_lower in content:
                        matching_chunks.append(chunk)
                        if len(matching_chunks) >= max_results:
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
            content = chunk.get("content", "")[:1000]
            
            # Calculate relevance score
            if chunk.get("similarity"):
                relevance_score = float(chunk.get("similarity"))
            else:
                query_terms = query.lower().split()
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
        results = results[:max_results]
        
        return {
            "results": results,
            "total": len(results),
            "query": query
        }
    except Exception as e:
        logger.error(f"Error querying bucket {bucket_id}: {sanitize_error(e)}")
        raise MCPServiceError("Failed to query bucket", "query_error")


async def chat_bucket_service(
    bucket_id: str,
    message: str,
    user: MCPUser,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chat with bucket using AI.
    
    Args:
        bucket_id: Bucket UUID
        message: User message
        user: Authenticated MCP user
        conversation_id: Optional conversation ID for context
        
    Returns:
        Dict with response, sources, and conversation_id
    """
    # Import here to avoid circular imports
    from app.routers.chat import deepseek_client, SYSTEM_PROMPT
    
    if not deepseek_client:
        raise MCPServiceError("AI service is not available", "ai_unavailable")
    
    try:
        supabase = get_supabase()
        
        # Get bucket info
        bucket_res = supabase.table("buckets").select("id, name").eq(
            "id", bucket_id
        ).eq("user_id", user.user_id).single().execute()
        
        if not bucket_res.data:
            raise MCPServiceError("Bucket not found", "bucket_not_found")
        
        # Get ALL files from bucket (include storage_path for full file access)
        all_files_res = supabase.table("files").select(
            "id, name, status, status_message, folder_path, storage_path"
        ).eq("bucket_id", bucket_id).eq("user_id", user.user_id).execute()
        
        all_files = all_files_res.data if all_files_res.data else []
        file_names = {f["id"]: f["name"] for f in all_files}
        file_storage_paths = {f["id"]: f.get("storage_path") for f in all_files}
        all_file_ids = [f["id"] for f in all_files]
        
        # Get chunks and summaries
        chunks_res = supabase.table("chunks").select(
            "id, content, file_id"
        ).eq("bucket_id", bucket_id).eq("user_id", user.user_id).execute()
        
        summaries_res = supabase.table("summaries").select(
            "id, content, file_id, title"
        ).eq("bucket_id", bucket_id).eq("user_id", user.user_id).execute()
        
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
                for chunk in chunks_for_file[:20]:  # Increased from 5 to 20
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

                # INTELLIGENT FALLBACK: If chunks are insufficient, fetch full file
                if total_chunk_chars < 500 and storage_path:
                    logger.info(f"MCP Services: Chunks limited for '{file_name}'. Fetching full file...")
                    full_content = fetch_full_file_content(storage_path, supabase)
                    if full_content and len(full_content) > total_chunk_chars:
                        logger.info(f"  MCP Services: Full file fetched: {len(full_content)} chars")
                        context_parts.append(f"[FULL CONTENT: {file_name}]\n{full_content[:8000]}")
                        sources.append(MCPSource(
                            file_name=file_name,
                            file_id=str(file_id),
                            type="full_file"
                        ))
            elif storage_path:
                # No chunks? Try full file directly
                logger.info(f"MCP Services: No chunks for '{file_name}'. Fetching full file...")
                full_content = fetch_full_file_content(storage_path, supabase)
                if full_content:
                    logger.info(f"  MCP Services: Full file fetched: {len(full_content)} chars")
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
        if not conversation_id:
            conv_res = supabase.table("conversations").insert({
                "id": str(uuid.uuid4()),
                "user_id": user.user_id,
                "bucket_id": bucket_id,
                "title": message[:50],
                "mode": "mcp"
            }).execute()
            conversation_id = conv_res.data[0]["id"]
        
        # Get previous messages
        previous_messages = []
        if conversation_id:
            prev_msgs_res = supabase.table("messages").select(
                "role, content"
            ).eq("conversation_id", conversation_id).order("created_at", desc=False).limit(10).execute()
            
            if prev_msgs_res.data:
                previous_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in prev_msgs_res.data
                ]
        
        # Save user message
        supabase.table("messages").insert({
            "id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "conversation_id": conversation_id,
            "role": "user",
            "content": message
        }).execute()
        
        # Build AI messages
        ai_messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + full_context}
        ]
        ai_messages.extend(previous_messages)
        ai_messages.append({"role": "user", "content": message})
        
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
                raise MCPServiceError("AI service quota exceeded. Please try again later.", "quota_exceeded")
            logger.error(f"DeepSeek API error: {str(e)}")
            raise MCPServiceError("AI service error", "ai_error")
        
        # Save assistant message
        supabase.table("messages").insert({
            "id": str(uuid.uuid4()),
            "user_id": user.user_id,
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_response,
            "model_used": "deepseek-chat",
            "sources": [{"file_name": s.file_name, "file_id": s.file_id, "type": s.type} for s in sources[:10]]
        }).execute()
        
        return {
            "response": ai_response,
            "sources": sources[:10],
            "conversation_id": str(conversation_id)
        }
    except MCPServiceError:
        raise
    except Exception as e:
        logger.error(f"Error in chat for bucket {bucket_id}: {sanitize_error(e)}")
        raise MCPServiceError("Failed to process chat message", "chat_error")


async def get_bucket_info_service(bucket_id: str, user: MCPUser) -> Dict[str, Any]:
    """
    Get detailed bucket information.
    
    Args:
        bucket_id: Bucket UUID
        user: Authenticated MCP user
        
    Returns:
        Dict with bucket details
    """
    try:
        supabase = get_supabase()
        
        # Get bucket
        response = supabase.table("buckets").select("*").eq(
            "id", bucket_id
        ).eq("user_id", user.user_id).single().execute()
        
        if not response.data:
            raise MCPServiceError("Bucket not found", "bucket_not_found")
        
        bucket = response.data
        
        # Get file count by status
        files_res = supabase.table("files").select(
            "status"
        ).eq("bucket_id", bucket_id).eq("user_id", user.user_id).execute()
        
        status_counts = {}
        if files_res.data:
            for f in files_res.data:
                status = f.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "id": str(bucket["id"]),
            "name": bucket["name"],
            "description": bucket.get("description"),
            "file_count": bucket.get("file_count", 0),
            "total_size_bytes": bucket.get("total_size_bytes", 0),
            "created_at": bucket["created_at"],
            "updated_at": bucket.get("updated_at"),
            "file_status_breakdown": status_counts
        }
    except MCPServiceError:
        raise
    except Exception as e:
        logger.error(f"Error getting bucket info for {bucket_id}: {sanitize_error(e)}")
        raise MCPServiceError("Failed to get bucket info", "bucket_info_error")


async def get_file_content_service(
    bucket_id: str,
    file_id: str,
    user: MCPUser,
    include_raw: bool = False
) -> Dict[str, Any]:
    """
    Get the full extracted content for a specific file.

    Args:
        bucket_id: Bucket UUID
        file_id: File UUID
        user: Authenticated MCP user
        include_raw: If True, include base64 data for image files

    Returns:
        Dict with file name, content, summary, and optionally raw data
    """
    try:
        supabase = get_supabase()

        # Get file info
        file_res = supabase.table("files").select(
            "id, name, status, mime_type, size_bytes, storage_path, word_count"
        ).eq("id", file_id).eq("bucket_id", bucket_id).eq("user_id", user.user_id).single().execute()

        if not file_res.data:
            raise MCPServiceError("File not found", "file_not_found")

        file_data = file_res.data
        file_name = file_data["name"]
        storage_path = file_data.get("storage_path")
        mime_type = file_data.get("mime_type", "")

        result = {
            "file_id": str(file_id),
            "file_name": file_name,
            "mime_type": mime_type,
            "size_bytes": file_data.get("size_bytes", 0),
            "word_count": file_data.get("word_count"),
            "status": file_data.get("status", "unknown"),
        }

        # Get summary if available
        summary_res = supabase.table("summaries").select(
            "content, title"
        ).eq("file_id", file_id).eq("user_id", user.user_id).limit(1).execute()

        if summary_res.data:
            result["summary"] = summary_res.data[0].get("content", "")

        # Get all chunks for this file (full content)
        chunks_res = supabase.table("chunks").select(
            "content, chunk_index"
        ).eq("file_id", file_id).eq("user_id", user.user_id).order("chunk_index").execute()

        if chunks_res.data:
            # Combine all chunks into full text
            chunk_texts = [c.get("content", "") for c in chunks_res.data]
            result["content"] = "\n".join(chunk_texts)
            result["chunk_count"] = len(chunks_res.data)
        else:
            result["content"] = ""
            result["chunk_count"] = 0

        # If chunks are empty or insufficient, try fetching full file
        if len(result["content"]) < 500 and storage_path:
            full_content = fetch_full_file_content(storage_path, supabase)
            if full_content and len(full_content) > len(result["content"]):
                result["content"] = full_content
                result["source"] = "full_file"
            else:
                result["source"] = "chunks"
        else:
            result["source"] = "chunks"

        # For images, optionally include base64 data
        is_image = mime_type and mime_type.startswith("image/")
        if include_raw and is_image and storage_path:
            try:
                import base64
                file_bytes = supabase.storage.from_("files").download(storage_path)
                if file_bytes:
                    result["raw_base64"] = base64.b64encode(file_bytes).decode("utf-8")
                    result["raw_mime_type"] = mime_type
            except Exception as e:
                logger.warning(f"Failed to fetch raw file for {file_id}: {e}")

        return result

    except MCPServiceError:
        raise
    except Exception as e:
        logger.error(f"Error getting file content for {file_id}: {sanitize_error(e)}")
        raise MCPServiceError("Failed to get file content", "file_content_error")
