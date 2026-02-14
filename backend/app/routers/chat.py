from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
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
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission, get_team_member_context, log_team_activity
        effective_uid = get_effective_user_id(user_id)
        team_ctx = get_team_member_context(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_chat"):
            raise HTTPException(status_code=403, detail="You don't have chat permission for this bucket")

        # Use service role for backend operations
        supabase = get_supabase()

        # Verify bucket belongs to effective user (owner)
        bucket_res = supabase.table("buckets").select("id, name").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        if not bucket_res.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Get ALL files from bucket first (so we know about everything, even if processing failed)
        # Include storage_path so we can fetch full file if needed
        all_files_res = supabase.table("files").select("id, name, status, status_message, folder_path, storage_path").eq("bucket_id", bucket_id).eq("user_id", effective_uid).execute()
        all_files = all_files_res.data if all_files_res.data else []
        file_names = {f["id"]: f["name"] for f in all_files}
        file_storage_paths = {f["id"]: f.get("storage_path") for f in all_files}
        all_file_ids = [f["id"] for f in all_files]
        
        # Get all chunks from bucket (for files that were successfully processed)
        chunks_res = supabase.table("chunks").select("id, content, file_id").eq("bucket_id", bucket_id).eq("user_id", effective_uid).execute()

        # Get all summaries from bucket (for files that were successfully processed)
        summaries_res = supabase.table("summaries").select("id, content, file_id, title").eq("bucket_id", bucket_id).eq("user_id", effective_uid).execute()
        
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
        # NEW: Intelligent fallback - if chunks are limited/insufficient, fetch full file
        for file_id in all_file_ids:
            file_name = file_names.get(file_id, "Unknown")
            storage_path = file_storage_paths.get(file_id)
            
            # Add comprehensive analysis if available
            if file_id in summaries_by_file:
                summary = summaries_by_file[file_id]
                analysis_content = summary.get("content", "")
                context_parts.append(f"[Analysis: {file_name}]\n{analysis_content}")
            
            # Add raw chunks if available
            has_chunks = file_id in chunks_by_file
            if has_chunks:
                chunks_for_file = chunks_by_file[file_id]
                chunk_contents = []
                total_chunk_chars = 0
                for chunk in chunks_by_file[file_id]:
                    content = chunk.get("content", "")
                    chunk_contents.append(content[:1000])  # Limit each chunk
                    total_chunk_chars += len(content)
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
            elif storage_path:
                # No chunks at all? Try to fetch full file directly
                logger.info(f"📥 No chunks found for '{file_name}'. Attempting to fetch full file...")
                full_content = fetch_full_file_content(storage_path, supabase)
                if full_content:
                    logger.info(f"  ✅ Full file fetched: {len(full_content)} chars")
                    context_parts.append(f"[FULL CONTENT: {file_name}]\n{full_content[:10000]}")  # Cap at 10k chars
        
        # Combine file inventory with content
        if context_parts:
            full_context = file_inventory + "\n\n" + "\n\n".join(context_parts)
        else:
            full_context = file_inventory + "\n\nNo file content available for analysis."
        
        # Check if web search would be helpful and perform it
        web_search_context = ""
        search_results = None
        web_search_triggered = should_search_web(request.message)
        logger.info(f"🔍 Web search check: {web_search_triggered} for message: '{request.message[:80]}'")

        if web_search_triggered:
            logger.info(f"🌐 TRIGGERING WEB SEARCH for: {request.message[:100]}")
            try:
                search_results = await search_web(request.message, num_results=5)
                logger.info(f"🌐 Web search returned {len(search_results) if search_results else 0} results")

                if search_results:
                    web_search_context = format_search_results_for_context(search_results)
                    logger.info(f"✅ Web search context prepared with {len(search_results)} results")
            except Exception as e:
                logger.error(f"❌ Web search failed: {e}")
        
        # Create conversation if new
        conversation_id = request.conversation_id
        if not conversation_id:
            conv_res = supabase.table("conversations").insert({
                "id": str(uuid.uuid4()),
                "user_id": effective_uid,
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

        logger.info(f"📚 Sources prepared: {len(used_sources)} total ({len(files_with_content)} docs, {len(search_results) if search_results else 0} web)")

        async def generate_stream():
            nonlocal used_sources
            try:
                full_response = ""
                thinking_content = ""
                use_reasoner = True  # Try deepseek-reasoner first

                # STEP 1: Quick AI call to check if search needed and get keywords
                logger.info("🤖 Step 1: Checking if web search needed...")
                search_check_prompt = f"""Analyze this user question: "{request.message}"

If this question needs current/real-time information (current events, people in office, recent news, prices, weather, etc.), respond with ONLY search keywords (3-5 words).
If it doesn't need web search, respond with: NO_SEARCH

Examples:
"who is the prime minister of japan now" → japan prime minister 2026
"what is the weather" → weather today
"explain quantum physics" → NO_SEARCH
"summarize this document" → NO_SEARCH

Your response (keywords only or NO_SEARCH):"""

                search_check = deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": search_check_prompt}],
                    temperature=0.3,
                    max_tokens=50
                )

                search_decision = search_check.choices[0].message.content.strip()
                logger.info(f"🔍 AI search decision: '{search_decision}'")

                # STEP 2: If AI wants search, do it
                if search_decision != "NO_SEARCH" and len(search_decision) > 0:
                    keywords = search_decision
                    logger.info(f"🌐 Searching with keywords: '{keywords}'")

                    # Send "searching" status to frontend
                    yield f"data: {json.dumps({'type': 'searching', 'keywords': keywords})}\n\n"

                    # Perform web search
                    search_results_data = await search_web(keywords, num_results=5)
                    logger.info(f"✅ Found {len(search_results_data)} results")

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

                # STEP 3: Try deepseek-reasoner first for 3-phase streaming
                logger.info("💭 Attempting deepseek-reasoner for thinking + response...")

                try:
                    # Try deepseek-reasoner (has native reasoning_content)
                    stream = deepseek_client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=ai_messages,
                        temperature=0.7,
                        stream=True
                    )
                    model_used_actual = "deepseek-reasoner"

                    # Phase 1: Stream thinking content
                    in_thinking_phase = True
                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'thinking'})}\n\n"

                    for chunk in stream:
                        # Check for reasoning_content (thinking)
                        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                            content = chunk.choices[0].delta.reasoning_content
                            thinking_content += content
                            yield f"data: {json.dumps({'type': 'thinking', 'content': content})}\n\n"

                        # Check for regular content (response)
                        if chunk.choices[0].delta.content:
                            # Switch to response phase on first content
                            if in_thinking_phase:
                                in_thinking_phase = False
                                yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'response'})}\n\n"

                            content = chunk.choices[0].delta.content
                            full_response += content

                            # Clean markdown from chunk before sending
                            clean_content = content.replace('**', '').replace('###', '').replace('__', '')
                            yield f"data: {json.dumps({'type': 'response', 'content': clean_content})}\n\n"

                except Exception as reasoner_error:
                    # Fallback to deepseek-chat if reasoner fails
                    logger.warning(f"⚠️ deepseek-reasoner failed ({reasoner_error}), falling back to deepseek-chat")
                    use_reasoner = False
                    model_used_actual = "deepseek-chat"

                    # Simulate thinking phase with a brief delay message
                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'thinking'})}\n\n"
                    thinking_content = "Analyzing your question and searching through documents..."
                    yield f"data: {json.dumps({'type': 'thinking', 'content': thinking_content})}\n\n"

                    yield f"data: {json.dumps({'type': 'phase_change', 'phase': 'response'})}\n\n"

                    stream = deepseek_client.chat.completions.create(
                        model="deepseek-chat",
                        messages=ai_messages,
                        temperature=0.7,
                        stream=True
                    )

                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content

                            # Clean markdown from chunk before sending
                            clean_content = content.replace('**', '').replace('###', '').replace('__', '')
                            yield f"data: {json.dumps({'type': 'response', 'content': clean_content})}\n\n"

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

                # Prepare metadata for database
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

                # Send done signal with cleaned message, sources, conversation ID, and thinking
                logger.info(f"✅ Sending {len(used_sources)} sources to frontend (thinking: {len(thinking_content)} chars)")
                yield f"data: {json.dumps({'type': 'done', 'message': message_text, 'sources': used_sources[:10], 'conversation_id': conversation_id, 'thinking': thinking_content, 'file_draft': file_draft})}\n\n"

            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "rate limit" in error_str or "429" in error_str:
                    yield f"data: {json.dumps({'type': 'error', 'error': 'API quota exceeded'})}\n\n"
                else:
                    logger.error(f"DeepSeek API error: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")
        
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
        from app.services.team_service import get_effective_user_id, check_bucket_permission
        effective_uid = get_effective_user_id(user_id)

        if not check_bucket_permission(user_id, bucket_id, "can_view"):
            raise HTTPException(status_code=403, detail="You don't have access to this bucket")

        supabase = get_supabase()

        # Verify bucket belongs to effective user
        try:
            bucket_res = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        except PostgrestAPIError:
            raise HTTPException(status_code=404, detail="Bucket not found")

        convs_res = supabase.table("conversations").select("*").eq("bucket_id", bucket_id).eq("user_id", effective_uid).order("updated_at", desc=True).execute()
        
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
        from app.services.team_service import get_effective_user_id
        effective_uid = get_effective_user_id(user_id)

        supabase = get_supabase()

        # Verify conversation belongs to effective user
        logger.info(f"📨 Loading messages for conversation {conversation_id}, user={user_id}, effective_uid={effective_uid}")

        try:
            conv_res = supabase.table("conversations").select("id, user_id, bucket_id").eq("id", conversation_id).single().execute()
        except PostgrestAPIError as e:
            logger.warning(f"⚠️ Conversation {conversation_id} not found in DB: {e}")
            raise HTTPException(status_code=404, detail="Conversation not found")

        if not conv_res.data:
            logger.warning(f"⚠️ Conversation {conversation_id} returned no data")
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Check ownership
        conv_owner = conv_res.data.get("user_id")
        if conv_owner != effective_uid:
            logger.warning(f"⚠️ Conversation {conversation_id} belongs to {conv_owner}, not {effective_uid}")
            raise HTTPException(status_code=403, detail="Access denied to this conversation")

        messages_res = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()

        logger.info(f"✅ Loaded {len(messages_res.data) if messages_res.data else 0} messages for conversation {conversation_id}")
        return {"messages": messages_res.data or []}

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"❌ Error loading messages for conversation {conversation_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load messages: {str(e)}"
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
