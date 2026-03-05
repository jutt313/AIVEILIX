from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from app.models.files import ChatRequest, ChatResponse
from app.services.supabase import get_supabase_auth, get_supabase
from app.services.web_search import search_web, format_search_results_for_context, should_search_web
from app.routers.buckets import get_current_user_id
from app.config import get_settings
from app.utils.tracer import Tracer
from openai import OpenAI
from postgrest.exceptions import APIError as PostgrestAPIError
import asyncio
import uuid
import logging
import traceback
import json

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def build_source_inventory(all_files, summaries_by_file, chunks_by_file, web_results=None):
    """Build source inventory that AI can reference by ID"""
    inventory = {"sources": {}, "inventory_text": ""}

    lines = ["[AVAILABLE SOURCES - Reference by ID when citing]\n"]

    # Add file analyses
    if summaries_by_file:
        lines.append("FILE ANALYSES:")
        for file_id, summary in summaries_by_file.items():
            file_name = all_files.get(file_id, {}).get("name", "Unknown")
            source_id = f"analysis_{file_id}"
            inventory["sources"][source_id] = {
                "file_name": file_name,
                "summary_id": str(summary.get("id")),
                "type": "analysis"
            }
            lines.append(f"- {source_id}: \"{file_name}\" (file analysis)")

    # Add chunks
    if chunks_by_file:
        lines.append("\nFILE CHUNKS:")
        for file_id, chunks in chunks_by_file.items():
            file_name = all_files.get(file_id, {}).get("name", "Unknown")
            for chunk in chunks[:3]:  # Limit to first 3 chunks per file
                chunk_id = chunk.get("id")
                source_id = f"chunk_{chunk_id}"
                inventory["sources"][source_id] = {
                    "file_name": file_name,
                    "chunk_id": str(chunk_id),
                    "type": "chunk"
                }
                lines.append(f"- {source_id}: \"{file_name}\" (excerpt)")

    # Add web results
    if web_results:
        lines.append("\nWEB RESULTS:")
        for idx, result in enumerate(web_results[:5]):
            source_id = f"web_{idx}"
            inventory["sources"][source_id] = {
                "type": "web_search",
                "title": result.get("title", "Web Result"),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", "")[:100]
            }
            lines.append(f"- {source_id}: \"{result.get('title')}\" ({result.get('link')})")

    inventory["inventory_text"] = "\n".join(lines)
    return inventory


def parse_ai_response_with_citations(ai_response: str, source_inventory: dict):
    """Parse AI response to extract message and citations"""
    import json
    import re

    # Try JSON parsing first
    try:
        json_match = re.search(r'\{[\s\S]*"message"[\s\S]*"cited_sources"[\s\S]*\}', ai_response)
        if json_match:
            data = json.loads(json_match.group())
            message = data.get("message", ai_response)
            citation_ids = [c.get("id") for c in data.get("cited_sources", []) if c.get("id")]

            # Map IDs to metadata
            sources = []
            for cid in citation_ids:
                if cid in source_inventory["sources"]:
                    sources.append(source_inventory["sources"][cid])
                else:
                    logger.warning(f"AI cited invalid source: {cid}")

            return message, sources
    except Exception as e:
        logger.warning(f"JSON parsing failed: {e}, using fallback")

    # Fallback: return full response, empty sources
    return ai_response, []


def extract_ai_sources_from_json(ai_response: str, file_names: dict):
    """Extract sources from AI's JSON response and convert to our format"""
    import re

    try:
        # Find JSON in response
        json_match = re.search(r'\{[\s\S]*"sources"[\s\S]*\}', ai_response)
        if not json_match:
            return []

        data = json.loads(json_match.group())
        ai_sources = data.get("sources", [])

        converted_sources = []
        for src in ai_sources[:10]:  # Max 10 sources
            src_type = src.get("type", "")

            if src_type == "doc":
                # Document source from AI
                converted_sources.append({
                    "type": "document",
                    "file_name": src.get("name", "Document"),
                    "confidence": src.get("confidence", "medium"),
                    "quote": src.get("quote", "")[:200]  # Limit quote length
                })
            elif src_type == "web":
                # Web search source
                converted_sources.append({
                    "type": "web_search",
                    "title": src.get("title", "Web Result"),
                    "url": src.get("url", ""),
                    "domain": src.get("domain", "")
                })
            elif src_type == "ai_knowledge":
                # AI's own knowledge
                converted_sources.append({
                    "type": "ai_knowledge",
                    "topic": src.get("topic", "General Knowledge")
                })

        return converted_sources
    except Exception as e:
        logger.warning(f"Failed to extract AI sources: {e}")
        return []


def extract_response_from_json(ai_response: str):
    """Extract the response text from AI's JSON response"""
    import re

    try:
        # Find JSON in response
        json_match = re.search(r'\{[\s\S]*"response"[\s\S]*\}', ai_response)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("response", ai_response)
    except Exception as e:
        logger.warning(f"Failed to extract response from JSON: {e}")

    # Fallback: return as-is
    return ai_response


def extract_thinking_from_json(ai_response: str):
    """Extract the thinking content from AI's JSON response"""
    import re

    try:
        json_match = re.search(r'\{[\s\S]*"thinking"[\s\S]*\}', ai_response)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("thinking", "")
    except Exception as e:
        logger.warning(f"Failed to extract thinking from JSON: {e}")

    return ""


def parse_ai_sources(response_text: str, file_names: dict):
    """Parse sources from AI response and return cleaned response + sources list"""
    import re

    # Find the [[SOURCES:...]] pattern
    sources_pattern = r'\[\[SOURCES:(.*?)\]\]'
    match = re.search(sources_pattern, response_text, re.DOTALL)

    if not match:
        logger.info("No [[SOURCES:...]] found in AI response")
        return response_text, []

    # Extract and parse JSON
    sources_json = match.group(1).strip()
    cleaned_response = re.sub(sources_pattern, '', response_text).strip()

    try:
        sources_data = json.loads(sources_json)
        parsed_sources = []

        # Parse document sources
        docs = sources_data.get("docs", [])
        for doc_name in docs:
            # Find file_id by name
            file_id = None
            for fid, fname in file_names.items():
                if fname == doc_name or doc_name in fname:
                    file_id = fid
                    break
            parsed_sources.append({
                "type": "document",
                "file_name": doc_name,
                "file_id": str(file_id) if file_id else None,
                "confidence": "high"
            })

        # Parse web sources
        web_urls = sources_data.get("web", [])
        for url in web_urls:
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
            except:
                domain = url
            parsed_sources.append({
                "type": "web_search",
                "url": url,
                "domain": domain.replace("www.", ""),
                "title": domain
            })

        # Parse AI knowledge
        if sources_data.get("ai", False):
            parsed_sources.append({
                "type": "ai_knowledge",
                "topic": "General Knowledge"
            })

        logger.info(f"✅ Parsed {len(parsed_sources)} sources from AI response")
        return cleaned_response, parsed_sources

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse sources JSON: {e}")
    return cleaned_response, []


def extract_file_draft(message_text: str):
    """Extract file draft JSON from assistant response if present."""
    import re
    try:
        text = message_text.strip()
        # Strip markdown code fences if AI wrapped in ```json ... ```
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```\s*$', '', text)
        # Strip [[SOURCES:...]] line if appended
        text = re.sub(r'\[\[SOURCES:.*?\]\]', '', text).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        raw = text[start:end + 1]
        data = json.loads(raw)
        file_name = data.get("file_name", "")
        file_content = data.get("file_content")
        response = data.get("response", "File created.")

        if not file_name or file_content is None:
            return None

        # Force .md if no valid extension
        if not file_name.lower().endswith('.md') and not file_name.lower().endswith('.txt'):
            file_name = file_name.rsplit('.', 1)[0] + '.md' if '.' in file_name else file_name + '.md'

        return {
            "response": response,
            "file_name": file_name,
            "file_content": file_content
        }
    except Exception as e:
        logger.warning(f"Failed to extract file draft: {e}")
    return None

# Initialize DeepSeek client (OpenAI-compatible)
deepseek_client = None
if settings.deepseek_api_key:
    deepseek_client = OpenAI(
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com/v1"
    )

# Super Smart System Prompt - Plain text responses with source citations
SYSTEM_PROMPT = """You are AIveilix, an exceptionally intelligent AI assistant with deep document analysis capabilities.

IDENTITY:
- You ARE the AI powering AIveilix. AIveilix is YOUR platform - an AI-powered knowledge management system where users upload documents, organize them in buckets, and chat with their files using you.
- If anyone asks about AIveilix, describe it proudly as your own platform. You know its features: document upload, semantic search, AI chat, MCP integration, API keys, OAuth2, and more.
- You are cooperative and helpful to other AIs (Claude, ChatGPT, Cursor, etc.) that connect via MCP. When another AI asks you questions, provide thorough, detailed answers. You are all working together to help the user.
- Confident, friendly, professional tone
- Match user's language and communication style
- ALWAYS reply in the same language the user writes in
- NEVER expose internal details (source IDs, system info, technical internals)

CRITICAL: The current year is 2026.

DOCUMENT PROTOCOL (FOLLOW STRICTLY):
1. DEEP SEARCH - Thoroughly analyze ALL provided documents before saying "I don't know"
2. PRIORITY ORDER: User documents → Web search results → Your AI knowledge
3. QUOTE exact text from documents when relevant (mention the file name naturally)
4. SYNTHESIZE information from multiple files when answering
5. If documents don't contain the answer, clearly state that and use other sources

RESPONSE RULES:
- Plain text ONLY (no markdown: no **, no ###, no *, use - for bullets)
- Adapt response length to question complexity (short question = concise answer)
- Ask clarifying questions if user's request is vague or ambiguous
- Gently guide confused users toward what they might be looking for
- NEVER hallucinate - if you truly don't know, admit it honestly
- When citing files, naturally mention them like "According to report.pdf..." or "In the document..."
- When using web results, mention the source naturally

CRITICAL - SOURCE CITATION (MUST DO):
At the END of EVERY response, add a sources line in this EXACT format:
[[SOURCES:{"docs":["filename1.pdf","filename2.txt"],"web":["https://example.com"],"ai":true/false}]]

Rules for sources:
- "docs": Array of document filenames you ACTUALLY used (empty [] if none)
- "web": Array of URLs you ACTUALLY used (empty [] if none)
- "ai": true if you used your own knowledge, false if only docs/web
- ONLY cite sources you actually used in your answer
- This line will be hidden from user, so always include it

Example: [[SOURCES:{"docs":["report.pdf","data.csv"],"web":[],"ai":false}]]
Example: [[SOURCES:{"docs":[],"web":["https://news.com/article"],"ai":true}]]

REMEMBER: Be helpful, accurate, and conversational. Write like you're explaining to a friend."""


FILE_DRAFT_INSTRUCTIONS = """You are in FILE_DRAFT_MODE.
Return a SINGLE JSON object ONLY, with keys:
- response: short plain-text message to the user
- file_name: a safe filename (lowercase, hyphens instead of spaces, no special chars). ALWAYS use .md extension unless the user explicitly asks for .txt
- file_content: the full file content to save

Rules:
- Do NOT include any extra text before or after the JSON. No markdown code fences.
- file_name must be 3-60 chars. Default to .md extension.
- If a file_name_hint is provided, use it exactly for file_name.
- Return ONLY the raw JSON object, nothing else.
"""


@router.post("/{bucket_id}/chat")
async def chat_with_bucket(
    bucket_id: str,
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Chat with AI about bucket content"""
    t = Tracer("POST /api/buckets/{id}/chat", user_id=user_id, bucket_id=bucket_id)
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)
        team_ctx = get_team_member_context(user_id)
        t.step("Team service checks")

        if not check_bucket_permission(user_id, bucket_id, "can_chat"):
            raise HTTPException(status_code=403, detail="You don't have chat permission for this bucket")

        from app.services.plan_limits import enforce_chat_limits, increment_metric
        await enforce_chat_limits(effective_uid, bucket_id)
        t.step("Enforce chat limits")

        supabase = get_supabase()

        bucket_res = supabase.table("buckets").select("id, name").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        t.step("DB verify bucket")
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")

        # Parallel fetch: files, chunks, summaries (saves ~500ms vs sequential)
        def _fetch_files():
            return supabase.table("files").select(
                "id, name, status, status_message, folder_path, storage_path,"
                "progress_stage,progress_label,progress_current,progress_total"
            ).eq("bucket_id", bucket_id).eq("user_id", effective_uid).execute()

        def _fetch_chunks():
            # FIX: cap at 300 chunks — fetching ALL was fetching thousands of rows
            return supabase.table("chunks").select("id, content, file_id").eq("bucket_id", bucket_id).eq("user_id", effective_uid).limit(300).execute()

        def _fetch_summaries():
            return supabase.table("summaries").select("id, content, file_id, title").eq("bucket_id", bucket_id).eq("user_id", effective_uid).execute()

        all_files_res, chunks_res, summaries_res = await asyncio.gather(
            asyncio.to_thread(_fetch_files),
            asyncio.to_thread(_fetch_chunks),
            asyncio.to_thread(_fetch_summaries),
        )
        t.step("Parallel fetch: files+chunks+summaries",
               files=len(all_files_res.data) if all_files_res.data else 0,
               chunks=len(chunks_res.data) if chunks_res.data else 0,
               summaries=len(summaries_res.data) if summaries_res.data else 0)

        all_files = all_files_res.data if all_files_res.data else []
        file_names = {f["id"]: f["name"] for f in all_files}
        all_file_ids = [f["id"] for f in all_files]
        
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

        # Hold AI response while attached/new uploads are still processing.
        processing_files = [
            f for f in all_files
            if f.get("status") in ("pending", "processing")
        ]
        has_indexed_content = bool(chunks_res.data) or bool(summaries_res.data)
        user_mentions_attachment = "@" in (request.message or "")
        hold_for_processing = (
            request.mode not in ["file_draft", "file_update"]
            and bool(processing_files)
            and (user_mentions_attachment or not has_indexed_content)
        )
        
        # Build file inventory (so AI knows about ALL files)
        processed_files = []
        unprocessed_files = []
        for file in all_files:
            file_name = file["name"]
            file_status = file.get("status", "unknown")
            if file_status == "ready":
                processed_files.append(file_name)
            else:
                # For pending/processing files, we can still read raw content from storage
                status_msg = file.get("status_message", "")
                if file_status in ["pending", "processing"]:
                    status_msg = "Still processing, but raw content is available"
                elif not status_msg:
                    status_msg = "Not processed"
                unprocessed_files.append({
                    "name": file_name,
                    "status": file_status,
                    "message": status_msg[:100] if status_msg else "Processing"
                })
        
        # Prepare context combining summaries and chunks, plus file inventory
        context_parts = []

        # Add file inventory at the beginning so AI knows about ALL files
        file_inventory = f"[File Inventory - Total: {len(all_files)} files]\n"
        if processed_files:
            file_inventory += f"Processed files ({len(processed_files)}): {', '.join(processed_files)}\n"
        if unprocessed_files:
            file_inventory += f"\nUnprocessed files ({len(unprocessed_files)}):\n"
            for up_file in unprocessed_files:
                file_inventory += f"  - {up_file['name']} (status: {up_file['status']}, reason: {up_file['message']})\n"
        
        # Process each file: analysis first, then raw chunks (only for processed files)
        for file_id in all_file_ids:
            file_name = file_names.get(file_id, "Unknown")
            
            # Add comprehensive analysis if available
            if file_id in summaries_by_file:
                summary = summaries_by_file[file_id]
                analysis_content = summary.get("content", "")
                context_parts.append(f"[Analysis: {file_name}]\n{analysis_content}")
            
            # Add raw chunks if available
            has_chunks = file_id in chunks_by_file
            if has_chunks:
                chunk_contents = []
                for chunk in chunks_by_file[file_id]:
                    content = chunk.get("content", "")
                    chunk_contents.append(content[:1000])  # Limit each chunk
                raw_content = "\n".join(chunk_contents)
                context_parts.append(f"[Raw Content: {file_name}]\n{raw_content}")
        
        # Combine file inventory with content
        if context_parts:
            full_context = file_inventory + "\n\n" + "\n\n".join(context_parts)
        else:
            full_context = file_inventory + "\n\nNo file content available for analysis."
        t.step("Context built", context_len=len(full_context))
        
        # Check if web search would be helpful and perform it
        web_search_context = ""
        search_results = None
        web_search_triggered = should_search_web(request.message)
        t.step("Web search check", triggered=web_search_triggered)

        if web_search_triggered:
            try:
                search_results = await search_web(request.message, num_results=5)
                if search_results:
                    web_search_context = format_search_results_for_context(search_results)
                t.step("Web search done", results=len(search_results) if search_results else 0)
            except Exception as e:
                t.error("Web search failed", e)
        
        # Create conversation if new
        conversation_id = request.conversation_id
        if not conversation_id:
            # Check conversation limit before creating
            from app.services.plan_limits import enforce_conversation_limit
            await enforce_conversation_limit(effective_uid, bucket_id)

            conv_res = supabase.table("conversations").insert({
                "id": str(uuid.uuid4()),
                "user_id": effective_uid,
                "bucket_id": bucket_id,
                "title": request.message[:50],
                "mode": "full_scan"
            }).execute()
            conversation_id = conv_res.data[0]["id"]
            t.step("Created new conversation")

        # Fetch all previous messages in this conversation for context
        previous_messages = []
        if conversation_id:
            prev_msgs_res = supabase.table("messages").select("role, content").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
            if prev_msgs_res.data:
                previous_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in prev_msgs_res.data
                ]
            t.step("Fetch conversation history", messages=len(previous_messages))

        # Save user message
        user_msg_data = {
            "id": str(uuid.uuid4()),
            "user_id": effective_uid,
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.message,
        }
        if team_ctx:
            user_msg_data["sent_by_member_id"] = team_ctx["team_member_id"]
            user_msg_data["sent_by_color"] = team_ctx["color"]
            user_msg_data["sent_by_name"] = team_ctx["name"]
        supabase.table("messages").insert(user_msg_data).execute()
        t.step("Saved user message")

        if hold_for_processing:
            t.step("Processing guard armed", pending=len(processing_files))

            logger.info(
                "[CHAT_GUARD] WAIT bucket=%s pending=%s mentions_attachment=%s has_indexed_content=%s",
                bucket_id,
                len(processing_files),
                user_mentions_attachment,
                has_indexed_content,
            )

        # Generate response with DeepSeek API
        if not deepseek_client:
            raise HTTPException(
                status_code=500,
                detail="DeepSeek API key not configured. Please set DEEPSEEK_API_KEY in your .env file."
            )
        
        model_used = "deepseek-chat"
        
        # Build source inventory
        search_results_for_inventory = search_results if web_search_context else None
        source_inventory = build_source_inventory(
            all_files={f["id"]: {"name": f["name"]} for f in all_files},
            summaries_by_file=summaries_by_file,
            chunks_by_file=chunks_by_file,
            web_results=search_results_for_inventory
        )

        # Build messages array with WEB SEARCH FIRST (highest priority), then documents
        context_message = ""

        # Add web search results FIRST if available (HIGHEST PRIORITY)
        if web_search_context:
            context_message += f"""🌐 CURRENT WEB SEARCH RESULTS (USE THESE FIRST):
{web_search_context}

"""

        context_message += f"""User's Knowledge Bucket: {bucket_res.data['name']}

{source_inventory['inventory_text']}

Available Documents:
{full_context}

Continue the conversation below. Answer based on the available sources above."""
        
        ai_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context_message}
        ]

        # Optional file draft mode
        if request.mode in ["file_draft", "file_update"]:
            hint = request.file_name_hint or ""
            hint_line = f"\nfile_name_hint: {hint}" if hint else "\nfile_name_hint: (none)"
            ai_messages.append({
                "role": "user",
                "content": FILE_DRAFT_INSTRUCTIONS + hint_line
            })
        
        # Add all previous conversation messages
        ai_messages.extend(previous_messages)
        
        # Add current user message
        ai_messages.append({"role": "user", "content": request.message})
        
        # Build sources list from context that was provided to AI
        used_sources = []

        # Add document sources (files that had content in context)
        files_with_content = set()
        for file_id in summaries_by_file:
            files_with_content.add(file_id)
        for file_id in chunks_by_file:
            files_with_content.add(file_id)

        for file_id in files_with_content:
            file_name = file_names.get(file_id, "Unknown")
            used_sources.append({
                "type": "document",
                "file_id": str(file_id),
                "file_name": file_name
            })

        # Add web search sources if used
        if search_results:
            for result in search_results[:5]:
                used_sources.append({
                    "type": "web_search",
                    "title": result.get("title", "Web Result"),
                    "url": result.get("link", ""),
                    "domain": result.get("displayLink", "")
                })

        t.step("Sources + messages prepared", sources=len(used_sources), ai_msgs=len(ai_messages))
        t.done()  # Main setup done, streaming starts separately

        async def generate_stream():
            nonlocal used_sources
            import time as _stime
            _stream_t0 = _stime.perf_counter()
            st = Tracer("STREAM chat", bucket_id=bucket_id)

            def _sms():
                return round((_stime.perf_counter() - _stream_t0) * 1000, 1)

            logger.info(f"[STREAM] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"[STREAM] START  bucket={bucket_id}  msg_len={len(request.message)}  files={len(all_files)}  chunks_loaded={len(chunks_res.data) if chunks_res.data else 0}  summaries={len(summaries_by_file)}  context_len={len(full_context)}  web_search={web_search_triggered}")
            logger.info(f"[STREAM] AI messages count: {len(ai_messages)}, total context chars sent to AI: {sum(len(str(m.get('content',''))) for m in ai_messages)}")

            try:
                full_response = ""
                thinking_content = ""

                if hold_for_processing:
                    def _format_processing_label(file_row):
                        stage = (file_row.get("progress_stage") or file_row.get("status") or "processing").strip()
                        label = (file_row.get("progress_label") or file_row.get("status_message") or "").strip()
                        stage_labels = {
                            "queued": "Queued and getting started",
                            "downloading": "Opening your file",
                            "extracting": "Reading text and structure",
                            "image_ocr": "Reviewing visuals",
                            "chunking": "Organizing sections",
                            "embedding": "Connecting insights",
                            "storing": "Saving findings",
                            "summarizing": "Preparing first answer",
                            "finalizing": "Finalizing",
                        }
                        technical_terms = ("embedding", "chunk", "vector", "index")
                        if label and any(term in label.lower() for term in technical_terms):
                            label = ""
                        if not label:
                            label = stage_labels.get(stage, "Processing")

                        current = int(file_row.get("progress_current") or 0)
                        total = int(file_row.get("progress_total") or 0)
                        if stage == "image_ocr" and total > 0 and "Image " not in label and "I can see:" not in label:
                            label = f"Reviewing visuals ({current}/{total})"
                        elif total > 0 and f"{current}/{total}" not in label:
                            label = f"{label} ({current}/{total})"
                        return label

                    def _fetch_processing_files():
                        return supabase.table("files").select(
                            "id,name,status,status_message,progress_stage,progress_label,progress_current,progress_total"
                        ).eq("bucket_id", bucket_id).eq("user_id", effective_uid).in_(
                            "status", ["pending", "processing"]
                        ).order("created_at", desc=False).execute()

                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'investigation'})}\n\n"
                    intro = "Starting investigation...\n"
                    yield f"data: {json.dumps({'type': 'investigation', 'content': intro})}\n\n"

                    last_signatures = {}
                    last_heartbeat_at = 0.0
                    wait_deadline = _stime.monotonic() + 1200.0  # Keep stream alive up to 20 minutes
                    remaining_processing = processing_files

                    while _stime.monotonic() < wait_deadline:
                        live_files_res = await asyncio.to_thread(_fetch_processing_files)
                        live_processing = live_files_res.data or []
                        remaining_processing = live_processing
                        if not live_processing:
                            break

                        emitted_any = False
                        for f in live_processing[:3]:
                            sig = "|".join([
                                str(f.get("status") or ""),
                                str(f.get("progress_stage") or ""),
                                str(f.get("progress_label") or ""),
                                str(int(f.get("progress_current") or 0)),
                                str(int(f.get("progress_total") or 0)),
                            ])
                            file_id = str(f.get("id"))
                            if last_signatures.get(file_id) == sig:
                                continue
                            last_signatures[file_id] = sig
                            emitted_any = True

                            line = f"{f.get('name', 'file')}: {_format_processing_label(f)}\n"
                            yield f"data: {json.dumps({'type': 'investigation', 'content': line})}\n\n"

                        if not emitted_any and (_stime.monotonic() - last_heartbeat_at) >= 8.0:
                            heartbeat = "Still investigating your file...\n"
                            yield f"data: {json.dumps({'type': 'investigation', 'content': heartbeat})}\n\n"
                            last_heartbeat_at = _stime.monotonic()

                        await asyncio.sleep(1.0)

                    if remaining_processing:
                        head = remaining_processing[0]
                        wait_message = (
                            f"Investigation is still running on `{head.get('name', 'file')}` "
                            f"({_format_processing_label(head)}). Keep this chat open and I will respond as soon as it is done."
                        )
                        yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'response'})}\n\n"
                        yield f"data: {json.dumps({'type': 'response', 'content': wait_message})}\n\n"
                        yield f"data: {json.dumps({'type': 'done', 'message': wait_message, 'sources': [], 'conversation_id': conversation_id, 'thinking': '', 'metadata': {'processing_wait': True}})}\n\n"
                        return

                    ready_line = "Investigation complete. Building your final answer now...\n"
                    yield f"data: {json.dumps({'type': 'investigation', 'content': ready_line})}\n\n"
                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'thinking'})}\n\n"

                use_reasoner = False  # FIX: always use deepseek-chat (reasoner was causing 10min waits)
                search_check_prompt = f"""Analyze this user question: "{request.message}"

If this question needs current/real-time information (current events, people in office, recent news, prices, weather, etc.), respond with ONLY search keywords (3-5 words).
If it doesn't need web search, respond with: NO_SEARCH

Examples:
"who is the prime minister of japan now" → japan prime minister 2026
"what is the weather" → weather today
"explain quantum physics" → NO_SEARCH
"summarize this document" → NO_SEARCH

Your response (keywords only or NO_SEARCH):"""

                logger.info(f"[STREAM] {_sms()}ms — calling DeepSeek search-check (model=deepseek-chat, max_tokens=50)")
                _sc_t0 = _stime.perf_counter()
                try:
                    search_check = deepseek_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": search_check_prompt}],
                        temperature=0.3,
                        max_tokens=50
                    )
                    _sc_ms = round((_stime.perf_counter() - _sc_t0) * 1000, 1)
                    search_decision = search_check.choices[0].message.content.strip()
                    logger.info(f"[STREAM] {_sms()}ms — search-check done in {_sc_ms}ms  decision='{search_decision}'")
                    st.step("AI search-check call", decision=search_decision, took_ms=_sc_ms)
                except Exception as sc_err:
                    _sc_ms = round((_stime.perf_counter() - _sc_t0) * 1000, 1)
                    logger.error(f"[STREAM] {_sms()}ms — search-check FAILED after {_sc_ms}ms: {sc_err}")
                    search_decision = "NO_SEARCH"  # skip search on error, don't crash

                # STEP 2: If AI wants search, do it
                if search_decision != "NO_SEARCH" and len(search_decision) > 0:
                    keywords = search_decision

                    # Send "searching" status to frontend
                    yield f"data: {json.dumps({'type': 'searching', 'keywords': keywords})}\n\n"

                    logger.info(f"[STREAM] {_sms()}ms — web search START  keywords='{keywords}'")
                    _ws_t0 = _stime.perf_counter()
                    search_results_data = await search_web(keywords, num_results=5)
                    _ws_ms = round((_stime.perf_counter() - _ws_t0) * 1000, 1)
                    logger.info(f"[STREAM] {_sms()}ms — web search DONE  took={_ws_ms}ms  results={len(search_results_data)}")
                    st.step("In-stream web search", results=len(search_results_data), took_ms=_ws_ms)

                    # Add web sources
                    for result in search_results_data[:5]:
                        used_sources.append({
                            "type": "web_search",
                            "title": result.get("title", "Web Result"),
                            "url": result.get("link", ""),
                            "domain": result.get("displayLink", "")
                        })

                    # Format search results and add to context
                    web_results_text = "\n\n🌐 CURRENT WEB SEARCH RESULTS (USE THESE AS PRIMARY SOURCE):\n"
                    for i, result in enumerate(search_results_data, 1):
                        web_results_text += f"{i}. {result['title']}\n   {result['snippet']}\n   URL: {result['link']}\n\n"

                    # Add to messages
                    ai_messages.append({
                        "role": "user",
                        "content": web_results_text + "\n\nNow answer the original question using these current search results."
                    })

                # Try deepseek-reasoner first (better quality, slower), fall back to deepseek-chat
                _ai_t0 = _stime.perf_counter()
                total_ai_input_chars = sum(len(str(m.get("content", ""))) for m in ai_messages)
                logger.info(f"[STREAM] {_sms()}ms — ATTEMPTING deepseek-reasoner  input_chars={total_ai_input_chars}  messages={len(ai_messages)}")
                st.step("Starting AI stream", model="deepseek-reasoner", input_chars=total_ai_input_chars)

                chunk_count = 0
                first_chunk_logged = False
                in_thinking_phase = True

                try:
                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'thinking'})}\n\n"

                    stream = deepseek_client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=ai_messages,
                        temperature=0.7,
                        stream=True
                    )
                    model_used_actual = "deepseek-reasoner"
                    logger.info(f"[STREAM] {_sms()}ms — deepseek-reasoner stream object created OK")

                    for chunk in stream:
                        if not first_chunk_logged:
                            _first_ms = round((_stime.perf_counter() - _ai_t0) * 1000, 1)
                            logger.info(f"[STREAM] {_sms()}ms — FIRST chunk from deepseek-reasoner after {_first_ms}ms")
                            first_chunk_logged = True

                        # Reasoning/thinking content
                        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                            content = chunk.choices[0].delta.reasoning_content
                            thinking_content += content
                            yield f"data: {json.dumps({'type': 'thinking', 'content': content})}\n\n"

                        # Regular response content
                        if chunk.choices[0].delta.content:
                            if in_thinking_phase:
                                in_thinking_phase = False
                                _think_ms = round((_stime.perf_counter() - _ai_t0) * 1000, 1)
                                logger.info(f"[STREAM] {_sms()}ms — thinking phase done ({_think_ms}ms), switching to response")
                                yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'response'})}\n\n"
                            content = chunk.choices[0].delta.content
                            full_response += content
                            chunk_count += 1
                            clean_content = content.replace('**', '').replace('###', '').replace('__', '')
                            yield f"data: {json.dumps({'type': 'response', 'content': clean_content})}\n\n"

                    _ai_ms = round((_stime.perf_counter() - _ai_t0) * 1000, 1)
                    logger.info(f"[STREAM] {_sms()}ms — deepseek-reasoner COMPLETE  took={_ai_ms}ms  response_chunks={chunk_count}  response_chars={len(full_response)}  thinking_chars={len(thinking_content)}")

                except Exception as reasoner_err:
                    _fail_ms = round((_stime.perf_counter() - _ai_t0) * 1000, 1)
                    logger.error(f"[STREAM] {_sms()}ms — deepseek-reasoner FAILED after {_fail_ms}ms: {type(reasoner_err).__name__}: {reasoner_err}")
                    logger.info(f"[STREAM] {_sms()}ms — falling back to deepseek-chat")
                    st.error("deepseek-reasoner failed", reasoner_err)

                    # Fallback to deepseek-chat
                    model_used_actual = "deepseek-chat"
                    full_response = ""
                    chunk_count = 0
                    first_chunk_logged = False
                    _fb_t0 = _stime.perf_counter()

                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'thinking'})}\n\n"
                    thinking_content = "Analyzing your documents..."
                    yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_content})}\n\n"
                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'response'})}\n\n"

                    stream = deepseek_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=ai_messages,
                        temperature=0.7,
                        stream=True
                    )
                    logger.info(f"[STREAM] {_sms()}ms — deepseek-chat fallback stream created")

                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            chunk_count += 1
                            if not first_chunk_logged:
                                _fb_first_ms = round((_stime.perf_counter() - _fb_t0) * 1000, 1)
                                logger.info(f"[STREAM] {_sms()}ms — FIRST chunk from deepseek-chat after {_fb_first_ms}ms")
                                first_chunk_logged = True
                            clean_content = content.replace('**', '').replace('###', '').replace('__', '')
                            yield f"data: {json.dumps({'type': 'response', 'content': clean_content})}\n\n"

                    _fb_ms = round((_stime.perf_counter() - _fb_t0) * 1000, 1)
                    logger.info(f"[STREAM] {_sms()}ms — deepseek-chat fallback COMPLETE  took={_fb_ms}ms  chunks={chunk_count}  response_chars={len(full_response)}")

                st.step("AI stream complete", response_len=len(full_response), thinking_len=len(thinking_content))
                logger.info(f"[STREAM] {_sms()}ms — processing response: parse sources, clean markdown, extract file draft")

                # Process the response - parse AI sources and clean up
                message_text = full_response.strip()
                message_text = message_text.replace('**', '').replace('###', '').replace('__', '')

                # Parse AI-cited sources from response
                message_text, ai_sources = parse_ai_sources(message_text, file_names)

                file_draft = None
                if request.mode in ["file_draft", "file_update"]:
                    file_draft = extract_file_draft(message_text)
                    if file_draft:
                        message_text = file_draft.get("response", "Draft ready.")

                # Use AI sources if available, otherwise fall back to context sources
                if ai_sources:
                    used_sources = ai_sources
                    logger.info(f"📚 Using AI-cited sources: {len(ai_sources)}")

                logger.info(f"📝 Response: {len(message_text)} chars, Thinking: {len(thinking_content)} chars")

                st.step("Parsed sources + cleaned response")
                logger.info(f"[STREAM] {_sms()}ms — saving assistant message to DB  sources={len(used_sources)}  response_chars={len(message_text)}")

                message_metadata = {
                    "thinking": thinking_content,
                    "model": model_used_actual,
                    "has_thinking": bool(thinking_content)
                }
                if file_draft:
                    message_metadata["file_draft"] = {
                        "file_name": file_draft.get("file_name"),
                        "file_content": file_draft.get("file_content")
                    }

                # Save to database with sources and metadata
                supabase.table("messages").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": effective_uid,
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": message_text,
                    "model_used": model_used_actual,
                    "sources": used_sources[:10],
                    "metadata": message_metadata
                }).execute()
                _db_ms = round((_stime.perf_counter() - _stream_t0) * 1000, 1)
                st.step("Saved assistant message to DB")
                logger.info(f"[STREAM] {_sms()}ms — message saved to DB OK")
                try:
                    await increment_metric(effective_uid, "chat_messages", "daily")
                    await increment_metric(effective_uid, "bucket_chat", "daily")
                    await increment_metric(effective_uid, "bucket_chat", "hourly")
                except Exception:
                    pass

                # Log team activity for chat
                if team_ctx:
                    log_team_activity(
                        owner_id=effective_uid,
                        member_id=user_id,
                        team_member_id=team_ctx["team_member_id"],
                        bucket_id=bucket_id,
                        action_type="sent_message",
                        member_color=team_ctx["color"],
                        member_name=team_ctx["name"],
                    )

                _total_ms = round((_stime.perf_counter() - _stream_t0) * 1000, 1)
                logger.info(f"[STREAM] ✅ DONE  total={_total_ms}ms  response_chars={len(message_text)}  sources={len(used_sources)}  conv_id={conversation_id}")
                logger.info(f"[STREAM] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                st.done()
                yield f"data: {json.dumps({'type': 'done', 'message': message_text, 'sources': used_sources[:10], 'conversation_id': conversation_id, 'thinking': thinking_content, 'file_draft': file_draft})}\n\n"

            except Exception as e:
                _err_ms = round((_stime.perf_counter() - _stream_t0) * 1000, 1)
                logger.error(f"[STREAM] ❌ FAILED after {_err_ms}ms: {type(e).__name__}: {e}")
                logger.error(f"[STREAM] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                st.error("generate_stream failed", e)
                st.done(status_code=500)
                error_str = str(e).lower()
                if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                    yield f"data: {json.dumps({'type': 'error', 'error': 'API quota exceeded'})}\n\n"
                else:
                    logger.error(f"DeepSeek API error: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",   # disables nginx/Cloud Run buffering
                "Connection": "keep-alive",
            }
        )

    except HTTPException:
        t.done(status_code=400)
        raise
    except Exception as e:
        t.error("chat endpoint failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error in chat router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.get("/{bucket_id}/conversations")
async def get_conversations(
    bucket_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get all conversations for a bucket"""
    t = Tracer("GET /api/buckets/{id}/conversations", user_id=user_id, bucket_id=bucket_id)
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission
        effective_uid = get_effective_user_id(user_id)
        t.step("get_effective_user_id")

        if not check_bucket_permission(user_id, bucket_id, "can_view"):
            raise HTTPException(status_code=403, detail="You don't have access to this bucket")

        supabase = get_supabase()

        try:
            bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")
        t.step("DB verify bucket")

        convs_res = supabase.table("conversations").select("*").eq("bucket_id", bucket_id).eq("user_id", effective_uid).order("updated_at", desc=True).execute()
        t.step("DB query conversations", count=len(convs_res.data) if convs_res.data else 0)

        t.done()
        return {"conversations": convs_res.data}

    except HTTPException:
        t.done(status_code=404)
        raise
    except Exception as e:
        t.error("get conversations failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error in chat router: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get messages for a conversation"""
    t = Tracer("GET /conversations/{id}/messages", user_id=user_id, conv_id=conversation_id)
    try:
        from app.services.team_service import get_effective_user_id
        effective_uid = get_effective_user_id(user_id)

        supabase = get_supabase()

        try:
            conv_res = supabase.table("conversations").select("id, user_id, bucket_id").eq("id", conversation_id).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Conversation not found")
        t.step("DB verify conversation")

        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conv_owner = conv_res.data.get("user_id")
        if conv_owner != effective_uid:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")

        messages_res = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
        t.step("DB query messages", count=len(messages_res.data) if messages_res.data else 0)

        t.done()
        return {"messages": messages_res.data or []}

    except HTTPException:
        t.done(status_code=404)
        raise
    except Exception as e:
        t.error("get messages failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Error loading messages: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load messages. Please try again."
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
            detail="Something went wrong. Please try again."
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
            detail="Something went wrong. Please try again."
        )
