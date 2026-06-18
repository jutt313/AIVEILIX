# AIveilix Agent System Plan

> This document covers the full agent design, current implementation status, problems, todos, and examples.
> **No internal credentials, keys, or secrets are included here.**

---

## How the Agent Currently Works (Existing Implementation)

### Entry Points
- `POST /buckets/{bucket_id}/conversations/{conversation_id}/messages` → `run_conversation_turn()` in `service.py`
- `POST /buckets/{bucket_id}/query` → `answer_bucket_query()` in `service.py`

### Current Flow (per message)
```
User sends message
  → search_conversation_memory (Qdrant dense search)
  → vague check → maybe return clarification question
  → search_bucket_documents (Qdrant hybrid: dense + sparse BM25, RRF fusion)
  → web search decision (auto-triggered by keywords OR low confidence score)
  → build_answer_prompt → call LLM (Claude / Gemini / OpenAI / DeepSeek / Kimi)
  → format_sources_section → append sources footer
  → persist both messages to Qdrant memory
  → return AgentReplyResponse
```

### Files
| File | Role |
|---|---|
| `backend/app/services/agent/service.py` | Orchestrator, conversation CRUD, memory persistence |
| `backend/app/services/agent/llm.py` | Multi-provider LLM, system prompt, style guidance |
| `backend/app/services/agent/retrieval.py` | Qdrant search (bucket docs + conversation memory) |
| `backend/app/services/agent/web.py` | DuckDuckGo web search |
| `backend/app/api/v1/endpoints/conversations.py` | API routes for conversations and messages |
| `backend/app/api/v1/endpoints/search.py` | API routes for bucket search and query |
| `backend/app/schemas/agent.py` | Request/response schemas |
| `backend/app/models/conversation.py` | DB models: Conversation, Message, ConversationChunk |
| `backend/app/services/pipeline/orchestrator.py` | File ingestion pipeline (upload → chunk → embed → Qdrant) |

### DB Models
- `Conversation` — has `web_search_mode` (smart/bucket_only/always_search), `follow_up_mode`, `is_pinned`
- `Message` — has `role`, `content`, `chunks_used` (JSONB), `embedding_status`, `token_count`
- `ConversationChunk` — Qdrant memory mirror in Postgres

---

## Current Problems (Bad Behavior)

### 1. Web Search Always Auto-Triggers
**Bad example:**
> User: "What is machine learning?"
> Agent silently searches DuckDuckGo even though bucket has ML docs.

**Why bad:** User didn't ask for web. Agent should use bucket first, ask permission before going online.

**Current code:** `_should_use_web()` in `service.py` auto-triggers on keywords like "latest", "today", "price" OR when bucket confidence score is low.

---

### 2. System Prompt is Rigid and Robotic
**Bad example:**
> User: "What's the revenue target?"
> Agent: "I don't have enough information in this bucket to answer that."

Dead end. No guidance. User doesn't know what to do next.

**Current code:** `build_answer_prompt()` in `llm.py:100` — system prompt is static rules list, no graceful fallback.

---

### 3. No Action Buttons / User Permission Flow
**Bad example:**
> Agent silently searches web without asking user.
> OR
> Agent dead-ends with "I don't know" without offering to search online.

**What's needed:** Agent returns `action_required` response type with clickable buttons in frontend.

---

### 4. No Feedback Mechanism
Agent has no way to know if user liked or disliked a response. No 👍/👎. No alignment learning.

---

### 5. No Thinking / Progress Display
User sends message, sees nothing until full response arrives. No visibility into what agent is doing (fetching file, searching web, etc.)

---

### 6. No Tools (Fetch URL, Write File, Calculate, etc.)
Agent can only read RAG + search web. Cannot:
- Fetch a URL the user pastes
- Write a .md file to the bucket
- List files in bucket
- Get a file summary quickly

---

### 7. No File Summaries
Every query does a full Qdrant vector search across all chunks. No fast "which file is relevant?" pre-check.

---

## New Agent Design

---

### Layer 1 — Knowledge (What the agent knows)

| Source | When Used |
|---|---|
| Bucket docs (RAG) | Always — checked first, every query |
| Conversation memory (RAG) | Always — checked first, every query |
| LLM own training knowledge | When bucket + memory have nothing relevant |
| Web search | Only when user explicitly asks OR pastes a URL |

**Source Priority (highest → lowest):**
```
Bucket docs → Conversation memory → LLM knowledge → Web (explicit only)
```

**Conflict rule:** If bucket doc says X and LLM training says Y → bucket doc always wins. It is the user's own data.

---

### Layer 2 — Tools (What the agent can do)

#### Already Implemented
| Tool | Status |
|---|---|
| `search_bucket_documents` | ✅ Done — hybrid Qdrant search |
| `search_conversation_memory` | ✅ Done — Qdrant dense search |
| `search_web` | ✅ Done — DuckDuckGo (needs trigger rule change) |

#### To Build
| Tool | What it does |
|---|---|
| `fetch_url` | Agent reads any URL the user pastes. Auto-triggers when URL detected in message. |
| `search_web_and_summarize` | Searches web AND summarizes findings in one step. Only on explicit user request. |
| `write_file` | Agent writes a `.md` file → auto saved to bucket → auto indexed into RAG. User can download it. |
| `read_file` | Agent reads raw `.md` file content from bucket. |
| `list_files` | Agent lists all files in the bucket with names and statuses. |
| `download_file` | Returns a download link for any `.md` file agent wrote. |
| `get_file_summary` | Returns pre-computed AI summary of a file instantly (no full RAG search needed). |

**`.md` File Auto Flow:**
```
Agent writes .md file
  → Saved to bucket storage
  → Auto-indexed into RAG (same pipeline as uploaded files)
  → User can download anytime via download_file tool
```

**File Summary Flow (on upload):**
```
File uploaded
  → Pipeline processes file
  → AI summary generated and stored in Summary table (already exists in models)
  → get_file_summary reads this instantly
  → Agent uses summaries to decide which files to search before doing full RAG
```

---

### Layer 3 — Thinking (How the agent responds)

#### Step-by-step thinking process per message:

```
1. Is the question clear?
   → Vague + no memory context → ask ONE clarifying question
   → Clear → continue

2. Does the message contain a URL?
   → Yes → auto-call fetch_url tool (no permission needed, user sent the URL)
   → No → continue

3. Check file summaries first (get_file_summary)
   → Decide which files are likely relevant before full RAG search
   → Only deep-search relevant files

4. Search bucket documents (RAG)
5. Search conversation memory (RAG)

6. Confidence check:
   → High confidence (score ≥ 0.65) → answer from bucket
   → Low confidence but has some results → use LLM reasoning + flag uncertainty
   → No results at all → show action button: "Want me to search online?"

7. Web search?
   → User explicitly said "search online" / "find latest" / "web results" → search
   → User pasted URL → fetch_url (already handled in step 2)
   → No results found → show action buttons [Allow Web Search] [Don't Search]
   → Otherwise → do NOT search web

8. Tool needed?
   → Write file request → call write_file tool
   → Math/calculation → call calculate tool
   → List files → call list_files tool

9. Generate answer:
   → Style guidance: short message → short answer, "explain/detail" → structured response
   → Show thinking steps in frontend as agent works (which file fetching, searching, etc.)
   → Format: headers for complex, code blocks for code, full .md for write requests

10. Feedback + follow-up:
    → Append 👍 👎 buttons to every response
    → Suggest next action if relevant: "Want me to save this as a file?"
    → Two versions option: if agent unsure of format, show [Option A] [Option B] buttons
```

---

### Action Button Types (Frontend)

**Type 1 — Action Buttons** (agent wants to DO something):
```
"I couldn't find this in your bucket."
  → [Allow Web Search]  [Don't Search]

"Want me to fetch this URL and create a .md file?"
  → [Fetch & Save]  [Just Fetch]  [Skip]

"Save this summary as a .md file to your bucket?"
  → [Save to Bucket]  [No Thanks]
```

**Type 2 — Feedback Buttons** (agent wants to LEARN):
```
"Was this helpful?"
  → [👍]  [👎]

"Which response style do you prefer?"
  → [Option A — Brief]  [Option B — Detailed]
```

All button clicks are:
- Sent back to backend as a follow-up message or feedback event
- Saved to DB for alignment learning
- Read by agent to adjust future responses per user

---

### Thinking Display (Frontend)

While agent is working, show live status in chat:
```
🔍 Searching bucket documents...
📄 Reading: marketing_strategy.pdf
🌐 Fetching: https://example.com/report
✍️ Generating answer...
```

This gives user visibility instead of blank waiting.

---

### Feedback Storage

- Every 👍/👎 saved to DB with: `message_id`, `user_id`, `rating`, `timestamp`
- Two-version preference saved: which style the user picked
- Agent reads this context when generating future responses in same conversation
- Global feedback (across all conversations) used for alignment per user profile

---

### Truthfulness Rule

Agent must never agree with a false premise to please the user.

**Bad example:**
> User: "The sky is green, right?"
> Agent: "Yes, the sky is green!" ← WRONG

**Good example:**
> User: "The sky is green, right?"
> Agent: "Actually, the sky is blue. Happy to explain why if you'd like."

Even if user dislikes the answer — agent stays truthful. Feedback (👎) is noted and response style adjusted, but facts are never changed.

---

## TODOs

### Backend
- [ ] Change web search trigger — remove auto-trigger, only fire on explicit user request or URL detection
- [ ] Add `action_required` response type to `AgentReplyResponse` schema with `action_type` and `options` fields
- [ ] Build `fetch_url` tool — detect URLs in message, fetch page content, pass to LLM
- [ ] Build `write_file` tool — agent writes .md, saves to bucket, triggers RAG indexing pipeline
- [ ] Build `read_file` tool — reads raw .md content from bucket storage
- [ ] Build `list_files` tool — lists all files in bucket with name, status, summary
- [ ] Build `download_file` tool — returns signed download URL for .md files agent wrote
- [ ] Build `search_web_and_summarize` tool — search + LLM summary in one call
- [ ] Build `get_file_summary` tool — reads pre-computed summary from Summary table
- [ ] Add feedback endpoint — `POST /messages/{message_id}/feedback` saves 👍/👎 + style preference
- [ ] Add thinking/progress streaming — emit step events via SSE or WebSocket during agent turn
- [ ] Rewrite system prompt in `llm.py:100` — make it smart, layered, truthful, graceful fallback
- [ ] Add file summary generation to upload pipeline (already has Summary model, needs LLM call)
- [ ] Use file summaries in retrieval — pre-filter relevant files before full RAG search
- [ ] Add feedback reading to `generate_answer` — pass user's past feedback as context

### Frontend
- [ ] Render action buttons inline in chat (Type 1 + Type 2)
- [ ] Handle `action_required` response type — show buttons, send user choice back
- [ ] Show agent thinking steps live while generating (file fetching, searching, etc.)
- [ ] Add 👍/👎 to every assistant message
- [ ] Show two-option style picker when agent returns dual responses
- [ ] Add download button on .md files agent wrote
- [ ] Show which files / URLs agent used while generating (live status)

### Schema Changes
- [ ] Add `action_required: bool` to `AgentReplyResponse`
- [ ] Add `action_type: str | None` (e.g. "web_search_permission", "save_file", "style_choice")
- [ ] Add `action_options: list[str] | None` (button labels)
- [ ] Add `thinking_steps: list[str] | None` (what agent did, for display)
- [ ] Add `feedback_id: UUID | None` to `MessageResponse`
- [ ] New schema: `MessageFeedbackRequest` with `rating` (like/dislike) + `style_preference`

### DB Changes
- [ ] New table: `message_feedback` — `id`, `message_id`, `user_id`, `rating`, `style_choice`, `created_at`
- [ ] New column on `Message`: `agent_wrote_file_id` (UUID, nullable) — tracks if agent created a file
- [ ] New column on `File`: `is_agent_written` (bool) — marks files created by agent vs uploaded by user

---

## Good vs Bad Examples

### Web Search
| Bad | Good |
|---|---|
| Agent auto-searches DuckDuckGo silently | Agent asks: "Want me to search online?" with buttons |
| Agent searches even when bucket has the answer | Agent uses bucket first, only offers web if nothing found |

### Fallback
| Bad | Good |
|---|---|
| "I don't have enough information in this bucket." (dead end) | "I couldn't find this in your bucket. [Allow Web Search] [Don't Search]" |
| Agent guesses / hallucinates | Agent says "I'm not certain — here's what I found, please verify" |

### Truthfulness
| Bad | Good |
|---|---|
| User likes strawberries → agent calls them blue to please user | Agent always states facts correctly, adjusts tone not truth |
| Agent agrees with false premise to avoid conflict | Agent gently corrects with explanation |

### Thinking Display
| Bad | Good |
|---|---|
| User waits 10 seconds seeing nothing | "🔍 Searching bucket... 📄 Reading report.pdf... ✍️ Generating..." |

### File Writing
| Bad | Good |
|---|---|
| Agent outputs markdown in chat — user has to copy it manually | Agent writes .md to bucket, shows download button, file is auto-indexed into RAG |
