# Aiveilix Agent Builder — Implementation Notes

Date: 2026-04-01

## What Was Implemented

The internal bucket agent flow is now wired into the FastAPI backend with:

- thread conversations backed by PostgreSQL models and Pydantic schemas
- bucket document retrieval from stored chunks
- bucket document retrieval from Qdrant `text_chunks`
- thread-memory retrieval from Qdrant `conversation_chunks`
- per-thread web modes:
  - `smart`
  - `bucket_only`
  - `always_search`
- follow-up question handling for unclear prompts
- answer generation through the selected user/profile LLM preference with safe fallbacks
- mandatory `Sources` section appended to responses
- message memory chunking and persistence back into PostgreSQL
- best-effort Qdrant persistence for conversation memory embeddings

## Main Files Added

- `backend/app/models/bucket.py`
- `backend/app/models/conversation.py`
- `backend/app/models/summary.py`
- `backend/app/schemas/agent.py`
- `backend/app/services/agent/retrieval.py`
- `backend/app/services/agent/web.py`
- `backend/app/services/agent/llm.py`
- `backend/app/services/agent/service.py`
- `backend/app/services/embeddings/service.py`

## Main Files Updated

- `backend/app/api/v1/endpoints/conversations.py`
- `backend/app/api/v1/endpoints/search.py`
- `backend/app/api/v1/endpoints/files.py`
- `backend/app/models/__init__.py`
- `backend/app/models/file.py`
- `backend/app/models/user.py`
- `backend/app/models/investigation_event.py`
- `backend/app/services/pipeline/orchestrator.py`
- `backend/app/services/pipeline/upload.py`
- `backend/app/config.py`

## Behavior Notes

- Bucket retrieval always runs first.
- Bucket retrieval is served from Qdrant, with hybrid dense+sparse search when BGE sparse weights are available and dense search fallback otherwise.
- Conversation memory retrieval is scoped to the current thread only and is served from Qdrant.
- Smart mode uses bucket evidence first and adds web search when the query looks time-sensitive or bucket evidence is weak.
- Bucket-only mode blocks web search.
- Always-search mode always includes web retrieval.
- Sources are shown at the bottom of every generated answer.
- When no document or web source was used, the source block renders exactly:
  - `Sources:`
  - `No document or web sources were used.`
- Conversation memory is chunked and saved after both user and assistant messages.
- `/buckets/{bucket_id}/query` now returns a follow-up question directly when clarification is needed, matching thread chat behavior.

## Runtime Fallbacks

The current implementation degrades safely when optional runtime dependencies are missing:

- if `tiktoken` is unavailable, token estimation falls back to a word-based approximation
- if provider SDKs or API keys are unavailable, answer generation falls back to an extractive local answer
- if DuckDuckGo search is unavailable, web search returns no results instead of crashing
- if Qdrant memory upsert fails, the message still saves and the embedding status is marked failed

## Review Fixes Made During Implementation

While verifying the backend, two pre-existing runtime issues were fixed because they blocked the new agent flow:

- SQLAlchemy model attribute `metadata` in `InvestigationEvent` was renamed to `event_metadata` with the column still stored as `metadata`
- file endpoints no longer import the full processing orchestrator at module import time, avoiding heavy startup imports of Docling/Gemini/embedding services

## Verification Performed

- `backend/venv/bin/python -m compileall backend/app`
- router import smoke check for:
  - `/buckets/{bucket_id}/conversations`
  - `/buckets/{bucket_id}/conversations/{conversation_id}/messages`
  - `/buckets/{bucket_id}/search`
  - `/buckets/{bucket_id}/query`
- service smoke check for web-mode decision logic

## Remaining Practical Limits

- bucket retrieval does not yet include a reranker stage after Qdrant retrieval
- external web and LLM behavior still depends on valid API keys and installed optional dependencies
- bucket, notification, and MCP endpoints outside this agent scope still contain stubs
