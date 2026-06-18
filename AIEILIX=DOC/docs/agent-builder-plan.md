# Aiveilix — Internal Agent Builder Plan

> This file is a full handoff brief for the agent responsible for building the Aiveilix internal AI agent.

---

## Mission

Build the full internal Aiveilix agent that lives inside each bucket and can:

- answer from bucket documents
- retrieve from conversation memory
- use web search when allowed and needed
- adapt tone and response style over time
- ask follow-up questions when needed
- show sources on every response
- support thread-level web modes

The core target flow is:

```text
user message -> retrieve bucket context + retrieve conversation memory + optional web search -> rerank/merge -> generate answer -> attach sources -> save conversation memory
```

This agent is separate from:

- the backend product/API agent
- the frontend UI agent
- the document pipeline agent

This worker owns the internal AI orchestration layer.

---

## Goal

When finished, Aiveilix should have a working internal agent that can:

1. receive a user message in a conversation thread
2. understand the current thread mode
3. retrieve from bucket documents
4. retrieve from current thread memory
5. decide whether web search is needed
6. combine the evidence correctly
7. generate a useful answer using the selected LLM
8. show sources at the bottom of every answer
9. save the exchange back into conversation memory for later retrieval

---

## Docs To Follow First

Read these docs before writing code:

- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/agent.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/rag-pipeline.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/mcp-layer.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/system-flow.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/database-schema.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/api-endpoints.md`

---

## Current Project State

Already available:

- PostgreSQL working locally
- Qdrant working locally
- Valkey working locally
- backend connected to all three stores
- auth system already built
- conversation memory schema already added:
  - `conversations`
  - `messages`
  - `conversation_chunks`
- Qdrant collections already exist:
  - `text_chunks`
  - `image_chunks`
  - `conversation_chunks`

This agent should build on top of that work, not replace it.

---

## Product Behavior To Implement

The internal agent must support these behaviors from the docs.

### Intelligence sources

The agent combines:

1. **Bucket RAG**
   - user’s uploaded documents in the current bucket

2. **Conversation memory RAG**
   - relevant prior messages from the current thread only

3. **Web search**
   - optional, depending on thread mode and message need

---

## Thread Rules

The agent works per conversation thread.

Each thread is separate.

Important rules:

- max 20 threads per bucket is already part of the product rules
- memory must stay inside the current thread
- no cross-thread tone carryover
- no cross-thread memory carryover
- new thread starts fresh except for user profile preferences

---

## Web Search Modes

Implement all 3 thread modes exactly.

### 1. Smart Mode

Default behavior.

Rules:

- always retrieve bucket context first
- if bucket is enough, answer from bucket + thread memory only
- if bucket is missing information or the answer may be outdated, use web search too

Smart mode must not waste web calls when the bucket already answers the question well.

---

### 2. Bucket Only Mode

Rules:

- no web search under any condition
- retrieve from bucket + current thread memory only
- if answer is not in bucket, say so clearly

---

### 3. Always Search Mode

Rules:

- use bucket retrieval and web search for every message
- still include conversation memory retrieval
- answer should merge both
- sources section should show both document and web sources used

---

## Memory Rules

Conversation memory is thread-level RAG, not just raw message replay.

Requirements:

- after each user message and assistant response, save the conversation
- chunk messages into `conversation_chunks`
- embed them into Qdrant collection `conversation_chunks`
- on future messages, retrieve relevant prior context from `conversation_chunks`
- do not rely only on “last N messages”

Conversation memory should help with:

- follow-up questions
- continuation of long threads
- maintaining user context over time
- preserving earlier decisions or clarifications

Memory must support long conversations without the agent collapsing because of context-window size.

---

## Source Rules

Every response must include a `Sources` section.

User-facing source types:

- document sources
- web sources

Conversation memory supports the answer internally but is not shown as a separate source type.

### Document source format

Examples:

```text
Sources:
📄 company-report.pdf — Page 4
📄 product-manual.docx — Page 12
```

### Web source format

Examples:

```text
Sources:
🌐 openai.com/blog/...
🌐 example.com/article/...
```

### Rules

- show only sources actually used
- if 10 docs were used, show all 10
- if web was used, show all links used
- always place sources at the bottom
- do not invent sources

---

## Follow-Up Question Behavior

The agent must ask follow-up questions when the user request is too unclear to answer correctly.

Trigger conditions:

- ambiguous request
- too little detail
- multiple possible interpretations
- needed scope not clear

The system must support 2 follow-up styles:

- `all_at_once`
- `one_by_one`

This preference comes from:

- thread override if later added
- otherwise user profile preference

Behavior:

- `all_at_once`: ask the needed clarifying questions together
- `one_by_one`: ask one clarification, wait, then continue

Do not ask unnecessary follow-ups if retrieval already makes the answer clear.

---

## Tone / Style Adaptation

The agent should adapt to the user over time inside the current thread.

Adaptation targets:

- tone
- detail level
- question style
- language style

The goal is not “human personality simulation.” The goal is better answer formatting and alignment with the user’s style.

Implement this practically:

- infer preferred verbosity from recent thread messages
- infer whether the user prefers direct vs explanatory answers
- preserve user language patterns when useful

Do not over-engineer this into a large profile-learning system first.

Version 1 should likely infer from:

- recent thread message patterns
- profile language/timezone preferences
- explicit user asks like “short”, “brief”, “detailed”

---

## LLM Routing

The user selects an LLM in settings.

The agent must use the configured LLM for answer generation.

Supported providers from docs:

- Claude
- Gemini
- GPT-4o
- Kimi

Version 1 should build a provider abstraction layer, even if only one provider is fully wired first.

Do not hardcode one vendor into the orchestration flow.

---

## Agent Architecture To Build

Build the internal agent as a set of small services, not one giant file.

Recommended architecture:

### 1. Orchestrator

Owns the high-level flow:

- load conversation and thread settings
- run retrieval
- decide on web search
- assemble final generation input
- call LLM
- save outputs

Suggested file:

- `backend/app/services/agent/orchestrator.py`

---

### 2. Retrieval service

Owns:

- bucket document retrieval from Qdrant + Postgres
- conversation memory retrieval from Qdrant + Postgres
- result normalization

Suggested files:

- `backend/app/services/agent/retrieval.py`
- `backend/app/services/agent/document_retrieval.py`
- `backend/app/services/agent/conversation_retrieval.py`

---

### 3. Web search service

Owns:

- search execution
- result normalization
- safe filtering / cleanup
- future retry logic

Suggested file:

- `backend/app/services/agent/web_search.py`

---

### 4. Prompt builder

Owns:

- system instructions
- source inclusion rules
- thread mode rules
- answer format rules
- tone/verbosity shaping

Suggested file:

- `backend/app/services/agent/prompt_builder.py`

---

### 5. Response formatter

Owns:

- final answer cleanup
- sources block generation
- bucket/web source formatting

Suggested file:

- `backend/app/services/agent/response_formatter.py`

---

### 6. Memory writer

Owns:

- save messages to Postgres
- chunk assistant/user messages into conversation chunks
- embed conversation chunks
- write to Qdrant `conversation_chunks`

Suggested file:

- `backend/app/services/agent/memory_writer.py`

---

### 7. Provider layer

Owns:

- LLM-specific API calls
- provider-specific request/response translation

Suggested files:

- `backend/app/services/llm/base.py`
- `backend/app/services/llm/claude.py`
- `backend/app/services/llm/gemini.py`
- `backend/app/services/llm/openai.py`
- `backend/app/services/llm/kimi.py`

---

## Write Scope

Preferred directories to use:

- `backend/app/services/agent/`
- `backend/app/services/llm/`
- `backend/app/services/search/`
- `backend/app/services/embeddings/`
- `backend/app/schemas/`
- `backend/app/models/`
- `backend/app/api/v1/endpoints/conversations.py`
- `backend/app/api/v1/endpoints/search.py`

If needed, also update:

- `backend/app/config.py`
- `backend/app/qdrant_client.py`
- `backend/app/database.py`

Only make minimal changes to unrelated files.

---

## Database Usage Requirements

Use existing schema, especially:

- `conversations`
- `messages`
- `conversation_chunks`
- `chunks`
- `files`
- `summaries`
- `profiles`

Expected reads:

- current thread settings from `conversations`
- user preferences from `profiles`
- file/chunk metadata from `files` and `chunks`

Expected writes:

- new `messages`
- new `conversation_chunks`
- maybe conversation title updates if implemented

If new columns are needed, document them before changing schema.

Do not create a second parallel memory system outside the schema already prepared.

---

## Qdrant Usage Requirements

Use existing Qdrant collections:

- `text_chunks`
- `image_chunks`
- `conversation_chunks`

Rules:

- do not create duplicate collections for the same purpose
- use the shared Qdrant client from:
  - `backend/app/qdrant_client.py`

Expected retrieval behavior:

- document retrieval from `text_chunks`
- optional image-context retrieval from `image_chunks`
- thread memory retrieval from `conversation_chunks`

---

## Valkey Usage Requirements

Valkey is optional support for agent orchestration, not permanent memory.

Possible uses:

- short-lived streaming state
- temporary web-search cache
- short-lived tool-call cache
- throttling / retry state

Do not use Valkey for permanent agent memory.

Permanent memory belongs in:

- PostgreSQL
- Qdrant

---

## Retrieval Strategy To Implement

### Bucket retrieval

For each message:

- search relevant chunks from `text_chunks`
- include nearby image metadata if available
- optionally fetch file/page info from Postgres
- normalize into agent-ready evidence objects

### Conversation retrieval

For each message:

- search relevant items from `conversation_chunks`
- restrict retrieval to current `conversation_id`
- rank and normalize results

### Merge

After retrieval:

- combine document evidence + memory evidence
- if web search runs, include web evidence too
- deduplicate
- preserve source metadata

---

## Web Search Decision Logic

Implement explicit decision logic.

### Smart mode behavior

Use web search when:

- bucket retrieval is weak or empty
- user asks for clearly current/live information
- answer likely depends on recent external facts
- user asks for comparison between bucket info and outside info

Do not use web search when:

- bucket already directly answers the question
- user explicitly wants only bucket content

### Bucket only mode behavior

- never use web search

### Always search mode behavior

- always perform web search

The decision function should be explicit and testable, not hidden deep inside prompt text.

Suggested file:

- `backend/app/services/agent/web_mode.py`

---

## Prompting Requirements

Build prompts that clearly separate:

- user question
- thread mode
- bucket evidence
- conversation memory evidence
- web evidence
- answer formatting rules

The prompt builder must tell the model:

- do not invent facts
- prefer retrieved evidence
- state uncertainty when evidence is weak
- always provide sources section
- use document and web sources only in user-facing output

Suggested prompt sections:

1. system instructions
2. mode instructions
3. formatting instructions
4. retrieved evidence
5. user question

---

## API Endpoints To Make Real

At minimum, the agent build should make these real:

- `POST /v1/buckets/{bucket_id}/query`
- `POST /v1/buckets/{bucket_id}/search`
- `POST /v1/buckets/{bucket_id}/conversations`
- `GET /v1/buckets/{bucket_id}/conversations`
- `GET /v1/buckets/{bucket_id}/conversations/{conversation_id}/messages`
- `POST /v1/buckets/{bucket_id}/conversations/{conversation_id}/messages`

Expected behavior:

- create thread
- send message
- run agent
- save assistant response
- return answer and sources

If full thread APIs are already partly implemented by another backend agent, coordinate and only fill the missing internal-agent logic.

---

## Minimum Version 1 Feature Set

Version 1 is successful if it supports:

- create conversation
- send user message
- retrieve from bucket
- retrieve from thread memory
- use smart/bucket_only/always_search modes
- generate answer from LLM
- show sources every time
- save messages and conversation memory

This is enough for a real internal agent v1.

---

## Nice-To-Have If Time Allows

- auto conversation title generation
- web result caching
- answer streaming
- long-thread summarization checkpoints
- confidence scoring
- source deduplication improvements
- better tone adaptation logic
- token budget manager

These are good, but do not delay the core agent path.

---

## Acceptance Criteria

This work is complete only when all are true:

1. A user can send a message in a thread and get an agent answer.
2. The agent can retrieve bucket context from Qdrant.
3. The agent can retrieve thread memory from `conversation_chunks`.
4. Smart mode, bucket-only mode, and always-search mode work.
5. The response always contains a `Sources` section.
6. The sources shown match actual evidence used.
7. User/assistant messages are persisted.
8. Conversation memory is embedded and stored for later retrieval.
9. Failure paths return useful errors instead of silent crashes.
10. The architecture is modular enough for the rest of the backend to build on.

---

## Testing Expectations

The agent worker should test at least these cases:

### Case 1 — Bucket answer only

- bucket contains the answer
- smart mode
- no web search used
- document sources shown

### Case 2 — Not in bucket, web allowed

- smart mode
- bucket weak/empty
- web search used
- web sources shown

### Case 3 — Bucket only mode

- answer not in bucket
- web disabled
- agent says it was not found in bucket

### Case 4 — Thread follow-up

- second message references prior thread context
- agent retrieves from conversation memory
- answer remains coherent

### Case 5 — Follow-up clarification

- ambiguous question
- agent asks clarifying question in the configured style

---

## Parallel Work Safety

This agent is not alone in the codebase.

Rules:

- do not revert other agents’ work
- assume auth and frontend work may keep changing
- keep write scope focused on internal-agent logic
- if touching shared files like routers or config, keep changes minimal and compatible

---

## Delivery Order

Recommended build order:

1. models and schemas needed for conversations/messages if missing
2. conversation APIs
3. retrieval services
4. web mode decision service
5. web search service
6. prompt builder
7. LLM provider abstraction
8. orchestrator
9. response formatter
10. memory writer
11. endpoint integration
12. tests / verification

---

## Deliverables

When finished, the agent worker should provide:

- the list of files changed
- the agent flow implemented
- env vars added or changed
- commands needed to run locally
- supported thread modes
- supported source output behavior
- known limitations and next TODOs

---

## Short Mission Statement

Build the Aiveilix internal agent so it can reason over:

- bucket knowledge
- thread memory
- optional web context

and return useful answers with sources every time.
