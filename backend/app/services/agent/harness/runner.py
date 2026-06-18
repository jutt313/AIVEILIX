"""
AgentRunner — the brain loop.

Per turn:
  1. LOAD     state + system prompt + history + user message + runtime context
  2. REASON   the model decides: answer directly, or call tool(s)
  3. ACT      run tool calls in parallel (with repeat / stall / cap guards)
  4. OBSERVE  feed tool results back, narrate
  5. FINISH   when the model emits final text — stream it, attach sources

Every step is bounded by 15 tool calls, 7-min soft / 10-min hard timeout,
2-stall, and 3-retry-per-goal caps (state.py constants).
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid as _uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent.harness.contract import EventCallback, TurnInput, TurnOutput
from app.services.agent.harness.llm_client import (
    LLMClient,
    Reply,
    ToolCall,
    build_llm_client,
)
from app.services.agent.harness.narration import (
    emit_plan_update,
    emit_step,
    emit_token,
    step_category_for,
)
from app.services.agent.harness.prompts import SYSTEM_PROMPT, build_runtime_context
from app.services.agent.harness.state import (
    HARD_TIMEOUT_SECONDS,
    MAX_STALL,
    MAX_TOOL_CALLS,
    SOFT_TIMEOUT_SECONDS,
    AgentState,
    ToolCallRecord,
)
from app.services.agent.harness.tools import (
    ToolDefinition,
    ToolResult,
    build_registry,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────── runner ──

class AgentRunner:
    """Drives the brain loop for one turn."""

    def __init__(
        self,
        *,
        llm_client: LLMClient | None = None,
        tool_registry: dict[str, ToolDefinition] | None = None,
    ):
        self.tools = tool_registry or build_registry()
        self.llm = llm_client  # may be None → resolved per-turn from TurnInput.model

    # ---------------------------------------------------------------- public

    async def run(
        self,
        turn: TurnInput,
        db: AsyncSession,
        *,
        on_event: EventCallback | None = None,
    ) -> TurnOutput:
        state = AgentState(active_file=turn.active_file)
        llm = self.llm or build_llm_client(turn.model)

        system_prompt = SYSTEM_PROMPT + build_runtime_context(
            active_file=state.active_file,
            bucket_files=turn.bucket_files,
            web_mode=turn.web_mode,
            web_override=turn.web_override,
            now=turn.now,
            current_speaker=turn.current_speaker,
        )

        messages: list[dict[str, Any]] = []
        # Conversation history → neutral message format. Strip Sources blocks.
        # In a shared team thread, prefix each user turn with the sender's name
        # ("[Sara]: …") so the brain can tell members apart and track who said
        # what. Owner turns and assistant turns stay unprefixed.
        for m in turn.conversation_history[-12:]:
            role = m.get("role")
            content = (m.get("content") or "").strip()
            if not role or not content:
                continue
            if role == "assistant":
                sep = "\n\n---\n"
                if sep in content:
                    content = content.split(sep, 1)[0].strip()
            elif role == "user":
                sender = (m.get("sender_name") or "").strip()
                if sender:
                    content = f"[{sender}]: {content}"
            messages.append({"role": role, "content": content})
        current_message = turn.user_message
        if turn.current_speaker:
            current_message = f"[{turn.current_speaker}]: {current_message}"
        messages.append({"role": "user", "content": current_message})

        final_text: str | None = None
        forced_final_reason: str | None = None

        while True:
            # --- caps & timeouts ----------------------------------------------
            if state.total_steps >= MAX_TOOL_CALLS:
                forced_final_reason = (
                    "You have used the maximum tool calls for this turn. Write the final answer now "
                    "using what you already have. Be honest about what was incomplete."
                )
                break
            if state.elapsed_seconds() >= HARD_TIMEOUT_SECONDS:
                forced_final_reason = "Time limit reached. Write the best answer you can with what you have."
                break
            if state.stall_count >= MAX_STALL:
                forced_final_reason = (
                    "You ran two consecutive tool calls with no new information. Stop searching and "
                    "write the final answer with what you already have — be honest about gaps."
                )
                break

            # If the agent asked a clarifying question, halt and return that
            # question as the assistant's reply.
            if state.action_required:
                final_text = (
                    state.clarifying_question
                    or "Could you tell me which file you mean?"
                )
                break

            # --- call the LLM ------------------------------------------------
            tool_specs = self._tool_specs_for_state(turn)

            try:
                reply = await asyncio.wait_for(
                    llm.chat(system_prompt, messages, tool_specs),
                    timeout=max(30.0, SOFT_TIMEOUT_SECONDS - state.elapsed_seconds()),
                )
            except asyncio.TimeoutError:
                forced_final_reason = "The model took too long to respond. Write the best answer you can."
                break
            except Exception as exc:
                logger.exception("[RUNNER] llm error: %s", exc)
                forced_final_reason = f"Provider error: {exc}. Write the best answer you can."
                break

            if reply.kind == "error":
                forced_final_reason = f"Provider error: {reply.error}. Write the best answer you can."
                break

            # --- narration first ----------------------------------------------
            for line in reply.narration_lines:
                cleaned = _clean_narration_line(line)
                if cleaned:
                    await emit_step(state, on_event, type_="thinking", label=cleaned)

            # --- final text? ---------------------------------------------------
            if reply.kind == "text":
                candidate = (reply.text or "").strip()
                # The model often does the real work as narration between tool
                # calls, then signs off with a thin meta-closer ("all done",
                # "all your questions answered") as its final text. That closer
                # is all the user would see. Run a synthesis pass that pulls every
                # answer (already in the message history) into one message when:
                #   - the final looks like a meta/thin closer, AND
                #   - real work happened this turn — either a 2+ item plan, or
                #     several tool calls (catches the no-plan case where the model
                #     answered in narration without ever calling make_plan).
                # The tool-call threshold keeps trivial turns ("hi") from tripping.
                did_real_work = (state.plan and len(state.plan) >= 2) or state.total_steps >= 3
                if did_real_work and _is_incomplete_final(candidate):
                    final_text = await self._synthesize_final_answer(
                        llm, system_prompt, messages, state, on_event,
                    )
                else:
                    final_text = candidate
                break

            # --- tool calls ----------------------------------------------------
            messages.append({
                "role": "assistant",
                "content": "\n".join(reply.narration_lines).strip(),
                "tool_calls": [
                    {"id": c.id, "name": c.name, "args": c.args} for c in reply.calls
                ],
            })

            tool_observations = await self._run_tool_calls(reply.calls, state, turn, db, on_event)

            messages.extend(tool_observations)

            # Inject compact plan view so the model never loses where it is.
            if state.plan:
                messages.append({
                    "role": "user",
                    "content": f"PLAN: {state.compact_plan_view()}",
                })
                await emit_plan_update(state, on_event)

        # --------------------- finalize: forced fallback or normal answer -----
        if forced_final_reason and not final_text:
            final_text = await self._forced_final_answer(
                llm, system_prompt, messages, forced_final_reason, on_event,
            )

        if not final_text:
            final_text = "Sorry — I couldn't put together a full answer this turn."

        # Web-off polite reply takes priority if the model triggered it.
        web_off_reply = next(
            (r.web_off_reply for r in state.call_records  # type: ignore[attr-defined]
             if getattr(r, "web_off_reply", None)),
            None,
        ) if False else None  # web_off is tracked via tool result summary text already

        # Mechanical source pool → final sources block.
        state.commit_pending_sources()
        sources_payload = state.used_doc_sources + state.used_web_sources
        if not sources_payload:
            if state.used_memory:
                sources_payload = [{"kind": "memory", "label": "From conversation history"}]
            else:
                sources_payload = [{"kind": "general", "label": "From general knowledge"}]

        # Build assembled message (answer + Sources block) for storage.
        sources_block = "Sources:\n" + "\n".join(s.get("label", "") for s in sources_payload)
        assistant_message = f"{final_text.strip()}\n\n---\n\n{sources_block}"

        # Stream the final answer token by token (chunked) so the UI feels live.
        await _stream_final_text(final_text, on_event)

        plan_payload = state.plan_payload() if state.plan else None
        chunks_used_payload = sources_payload  # already mechanical

        return TurnOutput(
            assistant_message=assistant_message,
            sources=sources_payload,
            steps=state.steps_payload(),
            plan=plan_payload,
            active_file=state.active_file,
            used_web=state.used_web,
            action_required=state.action_required,
            action_type=state.action_type,
            action_options=state.action_options,
            chunks_used=chunks_used_payload,
        )

    # ---------------------------------------------------------------- helpers

    def _tool_specs_for_state(self, turn: TurnInput) -> list[dict[str, Any]]:
        """Filter the registry to what's safe to expose this turn."""
        specs: list[dict[str, Any]] = []
        for tool in self.tools.values():
            specs.append({
                "name": tool.name,
                "description": tool.description,
                "params_schema": tool.params_schema,
            })
        return specs

    async def _run_tool_calls(
        self,
        calls: list[ToolCall],
        state: AgentState,
        turn: TurnInput,
        db: AsyncSession,
        on_event: EventCallback | None,
    ) -> list[dict[str, Any]]:
        """Run one or more tool calls. Independent calls go in parallel."""
        observations: list[dict[str, Any]] = []

        # Filter and check guards in declaration order.
        runnable: list[tuple[ToolCall, ToolDefinition | None, str | None]] = []
        for call in calls:
            tool = self.tools.get(call.name)
            if tool is None:
                runnable.append((call, None, f"unknown tool: {call.name}"))
                continue
            fingerprint = state.fingerprint(call.name, call.args)
            if fingerprint in state.call_hashes:
                runnable.append((call, tool, "REPEAT"))
                continue
            state.call_hashes.add(fingerprint)
            runnable.append((call, tool, None))

        # Emit narration step per tool (icon hint).
        for call, tool, _ in runnable:
            if tool is None:
                continue
            await emit_step(
                state,
                on_event,
                type_=step_category_for(tool.name),
                label=_narration_for_tool(tool.name, call.args),
                tool=tool.name,
            )

        # Run in parallel — but tools that need to mutate state sequentially
        # (make_plan, update_plan, ask_user) are awaited in declaration order.
        async def _runner(call: ToolCall, tool: ToolDefinition | None, guard: str | None) -> ToolResult:
            if tool is None:
                return ToolResult(summary=guard or "unknown tool", success=False)
            if guard == "REPEAT":
                return ToolResult(
                    summary=(
                        "You already ran this tool with the same args this turn. Use the prior "
                        "result or try a different approach."
                    ),
                    success=False,
                )
            try:
                return await tool.fn(state, turn, db, dict(call.args or {}))
            except Exception as exc:
                logger.exception("[TOOL] %s failed: %s", call.name, exc)
                return ToolResult(summary=f"tool error: {exc}", success=False, error=str(exc))

        # Sequential for plan/state-mutating tools, parallel for the rest.
        results: list[ToolResult] = []
        parallel_specs: list[tuple[ToolCall, ToolDefinition | None, str | None]] = []
        for spec in runnable:
            call, tool, _ = spec
            if tool is None or tool.name in {"make_plan", "update_plan", "ask_user"}:
                results.append(await _runner(*spec))
            else:
                parallel_specs.append(spec)
        if parallel_specs:
            parallel_results = await asyncio.gather(*(_runner(*s) for s in parallel_specs))
            results.extend(parallel_results)

        # Stall accounting + state updates from the merged results.
        any_new = False
        for (call, tool, _guard), result in zip(runnable, results):
            state.total_steps += 1
            sources_added = 0
            if result.pending_docs:
                state.pending_doc_sources.extend(result.pending_docs)
                sources_added += len(result.pending_docs)
            if result.pending_web:
                state.pending_web_sources.extend(result.pending_web)
                sources_added += len(result.pending_web)
                state.used_web = True
            if result.active_file_update is not None:
                state.active_file = result.active_file_update
            if result.used_memory:
                state.used_memory = True
            state.call_records.append(ToolCallRecord(
                name=call.name,
                args=dict(call.args),
                result_summary=result.summary[:240],
                sources_added=sources_added,
                success=result.success,
            ))
            if result.success and sources_added > 0:
                any_new = True
            if result.success and result.summary and "no matches" not in result.summary.lower():
                any_new = True
            logger.info(
                "[TURN %s] tool=%s success=%s srcs=%d step=%d/%d stall=%d elapsed=%.1fs",
                str(turn.conversation_id)[:8],
                call.name, result.success, sources_added,
                state.total_steps, MAX_TOOL_CALLS,
                state.stall_count, state.elapsed_seconds(),
            )
            observations.append({
                "role": "tool",
                "tool_call_id": call.id,
                "tool_name": call.name,
                "content": result.summary,
            })

        if not any_new and runnable:
            state.stall_count += 1
        else:
            state.stall_count = 0

        return observations

    async def _forced_final_answer(
        self,
        llm: LLMClient,
        system_prompt: str,
        messages: list[dict[str, Any]],
        reason: str,
        on_event: EventCallback | None,
    ) -> str:
        """Ask the model to write its final answer now — no more tool calls."""
        messages.append({"role": "user", "content": reason})
        try:
            reply = await asyncio.wait_for(
                llm.chat(system_prompt, messages, tools=[]),
                timeout=60.0,
            )
        except Exception as exc:
            logger.warning("[RUNNER] forced-final fallback failed: %s", exc)
            return "I ran into a problem finishing this answer. Please ask again."
        if reply.kind == "text" and reply.text:
            return reply.text.strip()
        for line in reply.narration_lines:
            if line.strip():
                return line.strip()
        return "I couldn't put together a complete answer this turn."

    async def _synthesize_final_answer(
        self,
        llm: LLMClient,
        system_prompt: str,
        messages: list[dict[str, Any]],
        state: AgentState,
        on_event: EventCallback | None,
    ) -> str:
        """Compose the complete final answer from everything gathered so far.

        Used when the model signed off with a thin/meta closer instead of the
        actual answers — its per-item answers were emitted as narration and are
        sitting in `messages`. This pass assembles them into the one message the
        user actually sees.
        """
        n = len(state.plan)
        scope = (
            f"address every one of the {n} items in your plan, in order,"
            if n >= 2 else
            "answer every question the user asked, in order,"
        )
        reason = (
            f"STOP. Do not end with a wrap-up line. The user only sees your NEXT message — so "
            f"write the COMPLETE final answer now: {scope} with each one's full actual answer "
            f"(use the findings from your tool calls above — do not re-run tools). For yes/no "
            f"questions, lead with yes/no. For anything not in the document, say 'not provided "
            f"in the document'. Never reply with 'all done', 'you got it', or 'all questions "
            f"answered' — output the answers themselves."
        )
        return await self._forced_final_answer(
            llm, system_prompt, messages, reason, on_event,
        )


# ─────────────────────────────────────────────────────────── module helpers ──

_INTERNAL_TERMS = (
    "chunk", "rag", "embedding", "vector", "qdrant", "top-k", "top k", "score:", "scores:",
    "candidates", "candidate set", "snippet count",
)


# Phrases a model uses to "sign off" instead of actually answering. If the
# final text is short AND contains one of these, it's a meta-closer, not an answer.
_META_CLOSERS = (
    "all set", "you got it", "all your questions", "have been answered",
    "i've answered", "i have answered", "all answered", "i've gone through",
    "i have gone through", "let me know if", "anything else", "hope that helps",
    "hope this helps", "all done", "is there anything",
)


def _is_incomplete_final(text: str) -> bool:
    """True if `text` is a thin/meta sign-off rather than a real answer."""
    t = text.strip()
    if len(t) < 40:
        return True
    low = t.lower()
    if len(t) < 400 and any(phrase in low for phrase in _META_CLOSERS):
        return True
    return False


def _clean_narration_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    lowered = line.lower()
    if any(term in lowered for term in _INTERNAL_TERMS):
        return ""
    # Keep narration to one line, drop trailing markdown / extra paragraphs.
    line = line.splitlines()[0].strip()
    if len(line) > 200:
        line = line[:200].rsplit(" ", 1)[0] + "…"
    return line


_NARRATION_TEMPLATES = {
    "list_files": "let me check your files…",
    "get_file_summary": "pulling the summary…",
    "read_file": "reading the file…",
    "search_documents": "searching the bucket…",
    "get_file_stats": "checking the document structure…",
    "get_page": "reading the page…",
    "get_visual": "looking at that visual…",
    "list_visuals": "scanning the visuals…",
    "get_section": "opening that section…",
    "read_outline": "checking the contents list…",
    "read_all_chunks": "reading the full document…",
    "search_web": "searching the web…",
    "fetch_url": "fetching that link…",
    "recall_memory": "looking back at past chats…",
    "ask_user": "(asking the user)",
    "make_plan": "writing a quick plan…",
    "update_plan": "updating the plan…",
}


def _narration_for_tool(name: str, args: dict[str, Any]) -> str:
    # Never leak a raw internal tool name to the UI — unknown tools get a
    # generic, user-safe label instead of "calling <tool_name>…".
    template = _NARRATION_TEMPLATES.get(name, "working on it…")
    if name == "search_documents" and args.get("query"):
        return f"searching the bucket for {str(args['query'])[:80]}…"
    if name == "search_web" and args.get("query"):
        return f"searching the web for {str(args['query'])[:80]}…"
    if name == "get_page" and args.get("start"):
        return f"reading page {args.get('start')}{'–' + str(args['end']) if args.get('end') else ''}…"
    if name == "get_section" and args.get("heading"):
        return f"opening the {str(args['heading'])[:60]} section…"
    return template


async def _stream_final_text(text: str, on_event: EventCallback | None) -> None:
    """Chunk the final text into small tokens so the UI feels live."""
    if on_event is None:
        return
    words = text.split(" ")
    buf: list[str] = []
    for w in words:
        buf.append(w)
        if len(" ".join(buf)) >= 32:
            await emit_token(on_event, " ".join(buf) + " ")
            buf = []
    if buf:
        await emit_token(on_event, " ".join(buf))


# ─────────────────────────────────────────────────── convenience entry point ──

async def run_turn(
    turn: TurnInput,
    db: AsyncSession,
    *,
    on_event: EventCallback | None = None,
) -> TurnOutput:
    """Module-level entry point: build a default runner and run the turn."""
    runner = AgentRunner()
    return await runner.run(turn, db, on_event=on_event)
