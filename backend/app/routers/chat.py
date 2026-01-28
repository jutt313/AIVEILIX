from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.files import ChatRequest, ChatResponse
from app.services.supabase import get_supabase_auth, get_supabase
from app.services.web_search import search_web, format_search_results_for_context, should_search_web
from app.services.file_processor import fetch_full_file_content
from app.routers.buckets import get_current_user_id
from app.config import get_settings
from openai import OpenAI
from postgrest.exceptions import APIError as PostgrestAPIError
import uuid
import logging
import traceback

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize DeepSeek client (OpenAI-compatible)
deepseek_client = None
if settings.deepseek_api_key:
    deepseek_client = OpenAI(
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com/v1"
    )

# Basic system prompt (now includes web search capability)
SYSTEM_PROMPT = """You are AIveilix, an AI assistant that helps users understand and work with their knowledge buckets. 
You have access to all the documents and files the user has uploaded to their bucket.
You can also search the web when the user needs current information or information not in their documents.

When answering questions, always:
1. Use information from the uploaded documents when relevant
2. Cite which documents or sections you're referencing
3. If web search results are provided, you may use them and cite the source URL
4. Be concise but thorough
5. If you don't know something, say so rather than guessing

CRITICAL FORMATTING RULES - YOU MUST FOLLOW THESE:
- DO NOT use ### headers
- DO NOT use ** for bold text
- DO NOT use excessive markdown symbols
- Write in plain, conversational language
- Format responses as simple paragraphs
- Only use basic formatting when absolutely essential
Your responses should read like natural conversation, not formatted documents.

The user can ask you questions about their documents, request summaries, ask you to help organize their knowledge, or search the web for external information."""


@router.post("/{bucket_id}/chat", response_model=ChatResponse)
async def chat_with_bucket(
    bucket_id: str,
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Chat with AI about bucket content"""
    try:
        # Use service role for backend operations
        supabase = get_supabase()
        
        # Verify bucket belongs to user
        bucket_res = supabase.table("buckets").select("id, name").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Get ALL files from bucket first (so we know about everything, even if processing failed)
        # Include storage_path so we can fetch full file if needed
        all_files_res = supabase.table("files").select("id, name, status, status_message, folder_path, storage_path").eq("bucket_id", bucket_id).eq("user_id", user_id).execute()
        all_files = all_files_res.data if all_files_res.data else []
        file_names = {f["id"]: f["name"] for f in all_files}
        file_storage_paths = {f["id"]: f.get("storage_path") for f in all_files}
        all_file_ids = [f["id"] for f in all_files]
        
        # Get all chunks from bucket (for files that were successfully processed)
        chunks_res = supabase.table("chunks").select("id, content, file_id").eq("bucket_id", bucket_id).eq("user_id", user_id).execute()
        
        # Get all summaries from bucket (for files that were successfully processed)
        summaries_res = supabase.table("summaries").select("id, content, file_id, title").eq("bucket_id", bucket_id).eq("user_id", user_id).execute()
        
        # Organize chunks and summaries by file
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
        
        # Build file inventory (so AI knows about ALL files)
        processed_files = []
        unprocessed_files = []
        for file in all_files:
            file_name = file["name"]
            file_status = file.get("status", "unknown")
            if file_status == "ready":
                processed_files.append(file_name)
            else:
                status_msg = file.get("status_message", "Not processed")
                unprocessed_files.append({
                    "name": file_name,
                    "status": file_status,
                    "message": status_msg[:100] if status_msg else "Not processed"
                })
        
        # Prepare context combining summaries and chunks, plus file inventory
        context_parts = []
        sources = []
        
        # Add file inventory at the beginning so AI knows about ALL files
        file_inventory = f"[File Inventory - Total: {len(all_files)} files]\n"
        if processed_files:
            file_inventory += f"Processed files ({len(processed_files)}): {', '.join(processed_files)}\n"
        if unprocessed_files:
            file_inventory += f"\nUnprocessed files ({len(unprocessed_files)}):\n"
            for up_file in unprocessed_files:
                file_inventory += f"  - {up_file['name']} (status: {up_file['status']}, reason: {up_file['message']})\n"
        
        # Process each file: analysis first, then raw chunks (only for processed files)
        # NEW: Intelligent fallback - if chunks are limited/insufficient, fetch full file
        for file_id in all_file_ids:
            file_name = file_names.get(file_id, "Unknown")
            storage_path = file_storage_paths.get(file_id)
            
            # Add comprehensive analysis if available
            if file_id in summaries_by_file:
                summary = summaries_by_file[file_id]
                analysis_content = summary.get("content", "")
                summary_id = summary.get("id")
                context_parts.append(f"[Analysis: {file_name}]\n{analysis_content}")
                sources.append({
                    "file_name": file_name,
                    "summary_id": str(summary_id),
                    "type": "analysis"
                })
            
            # Add raw chunks if available
            has_chunks = file_id in chunks_by_file
            if has_chunks:
                chunks_for_file = chunks_by_file[file_id]
                chunk_contents = []
                total_chunk_chars = 0
                for chunk in chunks_by_file[file_id]:
                    content = chunk.get("content", "")
                    chunk_id = chunk.get("id")
                    chunk_contents.append(content[:1000])  # Limit each chunk
                    total_chunk_chars += len(content)
                    sources.append({
                        "file_name": file_name,
                        "chunk_id": str(chunk_id),
                        "type": "chunk"
                    })
                raw_content = "\n".join(chunk_contents)
                context_parts.append(f"[Raw Content: {file_name}]\n{raw_content}")
                
                # INTELLIGENT FALLBACK: If chunks seem insufficient (too small), fetch full file
                # This helps when user asks detailed questions about specific content
                if total_chunk_chars < 500 and storage_path:  # Less than 500 chars? Probably truncated
                    logger.info(f"🔍 Chunks seem limited for '{file_name}' ({total_chunk_chars} chars). Fetching full file...")
                    full_content = fetch_full_file_content(storage_path, supabase)
                    if full_content and len(full_content) > total_chunk_chars:
                        logger.info(f"  ✅ Full file fetched: {len(full_content)} chars (was {total_chunk_chars})")
                        context_parts.append(f"[FULL CONTENT: {file_name}]\n{full_content[:10000]}")  # Cap at 10k chars
                        sources.append({
                            "file_name": file_name,
                            "type": "full_file"
                        })
            elif storage_path:
                # No chunks at all? Try to fetch full file directly
                logger.info(f"📥 No chunks found for '{file_name}'. Attempting to fetch full file...")
                full_content = fetch_full_file_content(storage_path, supabase)
                if full_content:
                    logger.info(f"  ✅ Full file fetched: {len(full_content)} chars")
                    context_parts.append(f"[FULL CONTENT: {file_name}]\n{full_content[:10000]}")  # Cap at 10k chars
                    sources.append({
                        "file_name": file_name,
                        "type": "full_file"
                    })
        
        # Combine file inventory with content
        if context_parts:
            full_context = file_inventory + "\n\n" + "\n\n".join(context_parts)
        else:
            full_context = file_inventory + "\n\nNo file content available for analysis."
        
        # Check if web search would be helpful and perform it
        web_search_context = ""
        if should_search_web(request.message):
            logger.info(f"Performing web search for: {request.message[:50]}...")
            try:
                search_results = await search_web(request.message, num_results=5)
                if search_results:
                    web_search_context = format_search_results_for_context(search_results)
                    sources.append({
                        "type": "web_search",
                        "query": request.message,
                        "results_count": len(search_results)
                    })
                    logger.info(f"Web search returned {len(search_results)} results")
            except Exception as e:
                logger.warning(f"Web search failed: {e}")
        
        # Create conversation if new
        conversation_id = request.conversation_id
        if not conversation_id:
            conv_res = supabase.table("conversations").insert({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "bucket_id": bucket_id,
                "title": request.message[:50],
                "mode": "full_scan"
            }).execute()
            conversation_id = conv_res.data[0]["id"]
        
        # Fetch all previous messages in this conversation for context
        previous_messages = []
        if conversation_id:
            prev_msgs_res = supabase.table("messages").select("role, content").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
            if prev_msgs_res.data:
                previous_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in prev_msgs_res.data
                ]
        
        # Save user message
        supabase.table("messages").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.message
        }).execute()
        
        # Generate response with DeepSeek API
        if not deepseek_client:
            raise HTTPException(
                status_code=500,
                detail="DeepSeek API key not configured. Please set DEEPSEEK_API_KEY in your .env file."
            )
        
        model_used = "deepseek-chat"
        
        # Build messages array with system prompt, documents context, web search, conversation history, and current message
        context_message = f"""User's Knowledge Bucket: {bucket_res.data['name']}

Available Documents:
{full_context}"""
        
        # Add web search results if available
        if web_search_context:
            context_message += f"\n\n{web_search_context}"
        
        context_message += "\n\nContinue the conversation below. Answer based on the documents above. If web search results are provided, you may also use them and cite the source URL."
        
        ai_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context_message}
        ]
        
        # Add all previous conversation messages
        ai_messages.extend(previous_messages)
        
        # Add current user message
        ai_messages.append({"role": "user", "content": request.message})
        
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
                    detail="API quota exceeded. Please wait a few minutes and try again."
                )
            logger.error(f"DeepSeek API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"AI service error: {str(e)}"
            )
        
        # Save assistant message
        supabase.table("messages").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": ai_response,
            "model_used": model_used,
            "sources": sources[:10]  # Limit to top 10 sources
        }).execute()
        
        return ChatResponse(
            message=ai_response,
            sources=sources[:10],
            conversation_id=conversation_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in chat router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{bucket_id}/conversations")
async def get_conversations(
    bucket_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get all conversations for a bucket"""
    try:
        supabase = get_supabase_auth()
        
        # Verify bucket belongs to user
        try:
            bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        convs_res = supabase.table("conversations").select("*").eq("bucket_id", bucket_id).order("updated_at", desc=True).execute()
        
        return {"conversations": convs_res.data}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in chat router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get messages for a conversation"""
    try:
        supabase = get_supabase_auth()
        
        # Verify conversation belongs to user
        conv_res = supabase.table("conversations").select("id").eq("id", conversation_id).eq("user_id", user_id).single().execute()
        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages_res = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
        
        return {"messages": messages_res.data}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error in chat router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    request: dict,
    user_id: str = Depends(get_current_user_id)
):
    """Update conversation title"""
    try:
        supabase = get_supabase()
        
        # Verify conversation belongs to user
        conv_res = supabase.table("conversations").select("id").eq("id", conversation_id).eq("user_id", user_id).single().execute()
        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update title
        title = request.get("title", "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        supabase.table("conversations").update({"title": title}).eq("id", conversation_id).execute()
        
        return {"message": "Conversation updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error updating conversation: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a conversation and all its messages"""
    try:
        supabase = get_supabase()
        
        # Verify conversation belongs to user
        conv_res = supabase.table("conversations").select("id").eq("id", conversation_id).eq("user_id", user_id).single().execute()
        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete all messages in conversation
        supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()
        
        # Delete conversation
        supabase.table("conversations").delete().eq("id", conversation_id).execute()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error deleting conversation: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
