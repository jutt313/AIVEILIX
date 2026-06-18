# Agentic RAG Loop Implementation Plan

## Goal

Add a bounded planner-executor loop for large multi-question prompts so the agent does not run one messy retrieval against a mixed question. The loop should split the user request into subquestions, retrieve evidence per subquestion from bucket documents and optionally web, retry weak subsearches once or twice, then synthesize one cited final answer.

Do not build an infinite "run until perfect" loop. That will create latency, cost, and failure problems. Build a capped loop that is visible to the user through the existing streaming step events.

## Current Repo Facts

- Main turn entry point: `backend/app/services/agent/service.py::run_conversation_turn`.
- Streaming progress already exists through `on_step` and `StepEvent`.
- Current step event types are simple strings like `thinking`, `reading_memory`, `searching_web`, and `retrieving_files`.
- Bucket retrieval entry points:
  - `search_bucket_documents(db, bucket_id, query, limit=5, allowed_file_ids=scope)`
  - `search_bucket_documents_for_files(db, bucket_id, query, mentioned_file_ids, limit=5)`
- Web search entry point: `search_web(query, max_results=5)`.
- Final answer generation entry point: `generate_answer(...)`.
- Citation filtering depends on `extract_used_marker(...)`, then `format_sources_section(...)`.
- Structural questions are already handled before normal RAG through `maybe_route_structural(...)`; keep that path authoritative.
- Current `smart` web mode only searches when the user explicitly asks for web. `always_search` searches every turn. `bucket_only` blocks web.

## High Level Flow

```text
run_conversation_turn()
  greeting check
  memory search
  vague-message check
  URL fetch
  live file-list injection
  structural router
  if agentic loop should run:
      plan subquestions
      for each subquestion:
          emit progress
          retrieve bucket evidence
          optionally search web
          verify evidence
          retry with rewritten query if weak
      synthesize final answer from grouped evidence
      append sources and persist messages
  else:
      existing single-pass RAG flow
```

## Activation

Add settings in `backend/app/config.py`:

```python
agentic_rag_loop_enabled: bool = False
agentic_rag_loop_max_subquestions: int = 8
agentic_rag_loop_max_retries_per_subquestion: int = 1
agentic_rag_loop_doc_limit_per_subquestion: int = 4
agentic_rag_loop_web_limit_per_subquestion: int = 3
agentic_rag_loop_max_total_searches: int = 20
```

Use `.env` to enable:

```env
AGENTIC_RAG_LOOP_ENABLED=true
AGENTIC_RAG_LOOP_MAX_SUBQUESTIONS=8
AGENTIC_RAG_LOOP_MAX_RETRIES_PER_SUBQUESTION=1
AGENTIC_RAG_LOOP_DOC_LIMIT_PER_SUBQUESTION=4
AGENTIC_RAG_LOOP_WEB_LIMIT_PER_SUBQUESTION=3
AGENTIC_RAG_LOOP_MAX_TOTAL_SEARCHES=20
```

Keep the default disabled until tests pass.

## New Module

Create:

```text
backend/app/services/agent/agentic_loop.py
```

Suggested dataclasses:

```python
@dataclass
class AgentSubQuestion:
    id: int
    question: str
    search_query: str
    needs_web: bool = False
    reason: str = ""


@dataclass
class SubQuestionEvidence:
    subquestion: AgentSubQuestion
    document_chunks: list[RetrievedDocumentChunk]
    web_results: list[RetrievedWebResult]
    attempts: int
    status: Literal["answered", "weak", "not_found"]
    notes: str = ""


@dataclass
class AgenticLoopResult:
    evidence_items: list[SubQuestionEvidence]
    document_chunks: list[RetrievedDocumentChunk]
    web_results: list[RetrievedWebResult]
    used_web: bool
    plan_summary: str
```

Functions to implement:

```python
def should_use_agentic_loop(content: str) -> bool:
    ...

async def plan_subquestions(
    *,
    content: str,
    preferred_llm: str | None,
    max_subquestions: int,
) -> list[AgentSubQuestion]:
    ...

async def execute_agentic_loop(
    *,
    db: AsyncSession,
    conversation: Conversation,
    content: str,
    preferred_llm: str | None,
    mentioned_file_ids: list[uuid.UUID],
    mentioned_names: list[str],
    allowed_file_ids: list[uuid.UUID] | None,
    web_enabled: bool,
    force_web: bool,
    emit: Callable[[str, str], Awaitable[None]],
) -> AgenticLoopResult:
    ...
```

## Planner Rules

`should_use_agentic_loop(content)` should be conservative. Trigger when at least one is true:

- The message has 3 or more question marks.
- The message has 3 or more numbered or bulleted question lines.
- The message is long, for example more than 500 characters, and contains multi-part connectors like "also", "compare", "and", "risks", "pricing", "timeline", "requirements".
- The user explicitly asks to "break down", "handle each question", "answer all questions", or similar.

Do not trigger for:

- Pure greetings.
- Vague short follow-ups.
- Structural-only questions where `suppress_rag` is true.
- File-list or file-existence verification turns.

`plan_subquestions(...)` should first use a cheap deterministic splitter for obvious numbered or bullet lists. Use the LLM planner only when deterministic splitting is not enough.

Planner output must be strict JSON:

```json
{
  "subquestions": [
    {
      "question": "What does the contract say about renewal?",
      "search_query": "contract renewal terms",
      "needs_web": false,
      "reason": "Bucket document fact"
    }
  ]
}
```

Validation rules:

- Clamp to `agentic_rag_loop_max_subquestions`.
- Drop duplicates.
- Drop vague subquestions under 4 words unless they include a specific file or entity.
- Preserve original user intent. Do not invent extra questions.
- If planning fails, fall back to existing single-pass RAG.

## LLM Support

Add a raw LLM helper in `backend/app/services/agent/llm.py` rather than forcing `generate_answer(...)` to do planning.

Suggested helper:

```python
async def generate_raw_completion(
    *,
    system_prompt: str,
    user_prompt: str,
    preferred_llm: str | None,
    chat_history: list[dict[str, str]] | None = None,
) -> str | None:
    ...
```

Reuse the existing provider selection and private provider functions:

- `_generate_with_claude`
- `_generate_with_gemini`
- `_generate_with_openai`

This avoids duplicating provider fallback logic.

## Web Mode Rules

Use the existing conversation modes:

- `bucket_only`: no web search for subquestions.
- `always_search`: web search each subquestion, capped by settings.
- `smart`: web search only if the user explicitly asked for web or the planner marks the subquestion `needs_web`.
- Per-turn `web_search_override=True`: force web search for subquestions.
- Per-turn `web_search_override=False`: block web search for subquestions.

Important: in `smart` mode, do not automatically search web just because bucket evidence is weak unless the user explicitly requested web or you add a separate product decision to allow that.

## Evidence Loop

For each subquestion:

```text
emit "Working on part i/n: <short label>"
retrieve mentioned-file chunks first, if any
retrieve general bucket chunks
dedupe chunks by chunk_id
trim to doc_limit_per_subquestion
if web enabled for this subquestion:
    search web
verify evidence
if weak and retries remain:
    rewrite/broaden search query
    retry retrieval
record status
```

Evidence is "strong enough" when at least one is true:

- There are document chunks with relevant content.
- There are web results and the subquestion is allowed to use web.
- There is authoritative structural or fetched URL context passed into final synthesis.

Evidence is "weak" when:

- No chunks and no web results.
- Only summary chunks are found for a very specific question.
- Top chunks come from unrelated files or have empty content.

Keep verification heuristic first. Add an LLM verifier only later if needed, because calling an LLM per subquestion can get expensive.

## Source Handling

Final source formatting can reuse the current path:

```python
sources_block, source_payload = format_sources_section(cited_docs, cited_web)
```

But document chunks and web results must be merged across subquestions before calling `generate_answer(...)`.

Dedup rules:

- Documents: dedupe by `chunk_id`.
- Web: dedupe by normalized URL.
- Preserve grouping information in the final prompt, but pass the flat deduped lists to `generate_answer(...)` so `USED: D1,W2` still maps correctly.

## Final Synthesis Prompt

Build an enriched question that includes the subquestion evidence report:

```text
Original user request:
<content>

Agent plan:
1. <subquestion>
2. <subquestion>

Evidence gathered:
[Part 1] <subquestion>
Documents available: D1, D2
Web available: W1
Status: answered

[Part 2] <subquestion>
Documents available: none
Web available: W2, W3
Status: weak

Instructions:
- Answer each part clearly.
- Use only the provided bucket/web evidence for factual claims.
- If a part has weak or missing evidence, say that directly.
- Do not pretend every part was answered if evidence was missing.
- Keep citations compatible with the final USED line.
```

Then call existing `generate_answer(...)` with:

- `question=enriched_content`
- grouped/deduped `document_chunks`
- grouped/deduped `web_results`
- existing `memory_chunks`
- existing `chat_history`

## Progress UI

Use existing `on_step` events. No frontend schema change is required at first.

Example labels:

```text
Breaking your request into 6 parts...
Working on part 1/6: renewal terms
Searching bucket documents for part 1/6...
Found evidence in 2 document chunk(s)
Working on part 2/6: latest market context
Searching web for part 2/6...
Evidence was weak, retrying with a broader query...
Preparing final answer from 6 parts...
```

Optional later improvement: add fields to `StepEvent` like `part`, `total`, and `status`. Do not do this in the first pass unless the frontend needs richer progress bars.

## Integration Point In `service.py`

Insert the loop after:

- URL fetch
- live file-list injection
- mentioned file resolution
- structural router
- ready file count
- conversation file scope resolution

Insert before the current single-pass `search_bucket_documents(...)` call.

Pseudo-code:

```python
use_agentic = (
    settings.agentic_rag_loop_enabled
    and not suppress_rag
    and should_use_agentic_loop(content)
)

if use_agentic:
    await _emit("thinking", "Breaking your request into parts...")
    loop_result = await execute_agentic_loop(...)
    document_chunks = loop_result.document_chunks
    web_results = loop_result.web_results
    enriched_content = build_agentic_synthesis_content(
        content=content,
        fetched_url_contexts=fetched_url_contexts,
        structural_blocks=structural_blocks,
        evidence_items=loop_result.evidence_items,
    )
    skip_single_pass_retrieval = True
else:
    existing single-pass retrieval
```

Do not bypass existing persistence, source filtering, save-file action, or message memory logic. Only replace the retrieval and web-search section when the loop runs.

## Answer API Compatibility

The non-streaming response already returns:

- `thinking_steps`
- `thinking_step_events`
- `used_web_search`
- `sources`

The streaming endpoint already sends step events and a final `done` payload. No schema migration is required for the first version.

## Tests

Add tests under:

```text
backend/tests/test_agentic_loop.py
```

Minimum tests:

- `should_use_agentic_loop` returns false for greetings and one normal question.
- `should_use_agentic_loop` returns true for numbered multi-question prompts.
- deterministic splitter returns ordered subquestions.
- planner clamps to max subquestions.
- executor dedupes document chunks by `chunk_id`.
- executor respects `bucket_only` and does not call `search_web`.
- executor respects `always_search` and calls `search_web` per subquestion until capped.
- weak evidence triggers one retry and then records `weak` or `not_found`.

Add one service-level test if practical:

- With `AGENTIC_RAG_LOOP_ENABLED=true`, a multi-question prompt emits progress events for each part and still returns a normal `AgentTurnResult`.

## Implementation TODO

- [ ] Add agentic loop settings to `backend/app/config.py`.
- [ ] Add `generate_raw_completion(...)` to `backend/app/services/agent/llm.py`.
- [ ] Create `backend/app/services/agent/agentic_loop.py`.
- [ ] Implement `should_use_agentic_loop(...)`.
- [ ] Implement deterministic subquestion splitter.
- [ ] Implement LLM JSON planner fallback.
- [ ] Implement plan validation and max-subquestion clamping.
- [ ] Implement document/web evidence execution per subquestion.
- [ ] Implement retry query generation with max retry cap.
- [ ] Implement document and web dedupe helpers.
- [ ] Implement evidence report builder for final synthesis.
- [ ] Integrate loop into `run_conversation_turn(...)` before existing single-pass retrieval.
- [ ] Preserve structural-router suppression so authoritative manifest answers do not get polluted by RAG.
- [ ] Preserve live file-list injection for file existence/list questions.
- [ ] Preserve current `format_sources_section(...)` and `extract_used_marker(...)` behavior.
- [ ] Add step events for planning, each subquestion, retry, and final synthesis.
- [ ] Add unit tests for planner, executor caps, web mode behavior, and dedupe.
- [ ] Run backend tests.
- [ ] Enable in `.env` only after tests pass.

## Rollout

1. Ship behind `AGENTIC_RAG_LOOP_ENABLED=false`.
2. Test locally with synthetic 5 to 10 question prompts.
3. Enable for development only.
4. Watch logs for:
   - total subquestions
   - total retrieval calls
   - total web calls
   - weak evidence count
   - total latency
5. If latency is too high, lower max subquestions or retries before widening rollout.

## Main Risk

The biggest risk is not decomposition itself. The risk is letting the loop become another hallucination source. The final answer must explicitly say when a subquestion had weak or missing evidence, and the loop must stay capped.
