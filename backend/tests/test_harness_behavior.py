"""
End-to-end behavior tests for the harness brain.

One test per old-agent failure mode, proving the new brain handles it. The
LLM is scripted via `FakeLLM`. Tools are stubbed in a custom registry so we
can assert exactly which tools the brain chose and with what args.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from app.services.agent.harness.contract import TurnInput
from app.services.agent.harness.runner import AgentRunner
from app.services.agent.harness.state import AgentState
from app.services.agent.harness.tools import ToolDefinition, ToolResult

from tests.conftest import (
    FakeLLM,
    EventCapture,
    fake_file,
    make_turn,
    reply_text,
    reply_tools,
)


# ──────────────────────────────────────────────────────── stub tool registry ──
#
# Each stub records its calls so tests can assert the brain reached the right
# tool with the right args. Real registry behavior is covered separately in
# test_harness_tools_unit.py — here we just need a controlled surface.

@dataclass
class StubTool:
    """Pluggable stub. `result_fn(args) -> ToolResult` produces the response."""
    name: str
    description: str
    params_schema: dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})
    calls: list[dict[str, Any]] = field(default_factory=list)
    result_fn: Any = None       # callable(args) -> ToolResult
    static_result: ToolResult | None = None

    async def __call__(self, state: AgentState, turn: TurnInput, db, args: dict[str, Any]) -> ToolResult:
        self.calls.append(dict(args))
        if self.result_fn:
            return self.result_fn(args)
        return self.static_result or ToolResult(summary="ok")


def make_stub(name: str, description: str = "stub", **kwargs) -> tuple[ToolDefinition, StubTool]:
    stub = StubTool(name=name, description=description, **kwargs)
    definition = ToolDefinition(
        name=stub.name,
        description=stub.description,
        params_schema=stub.params_schema,
        fn=stub,
    )
    return definition, stub


def build_registry(*stubs) -> dict[str, ToolDefinition]:
    return {s[0].name: s[0] for s in stubs}


# ──────────────────────────────────────────────────────────────── test cases ──


class TestGreetingAnswersDirectly:
    """Old bug: every message went through RAG, even 'hi'."""

    async def test_hello_no_tool_calls(self, dummy_db, event_capture: EventCapture):
        """Model says 'hey, what's up?' immediately — zero tool calls."""
        llm = FakeLLM([reply_text("hey, what's up?")])
        registry = build_registry(
            make_stub("list_files", "list bucket files"),
            make_stub("search_documents", "search docs"),
        )
        runner = AgentRunner(llm_client=llm, tool_registry=registry)
        turn = make_turn(
            user_message="hello",
            bucket_files=[fake_file("tax_2024.pdf")],
        )

        output = await runner.run(turn, dummy_db, on_event=event_capture)

        # Greeted, no tools, falls back to general source.
        assert "hey" in output.assistant_message.lower()
        list_files_calls = registry["list_files"].fn.calls
        search_calls = registry["search_documents"].fn.calls
        assert list_files_calls == []
        assert search_calls == []
        assert output.sources == [{"kind": "general", "label": "From general knowledge"}]
        assert output.used_web is False


class TestChatContextMemory:
    """Old bug: 'my name is Juan' then 'what is my name?' searched docs
    instead of answering from chat history."""

    async def test_name_recall_uses_history_not_docs(self, dummy_db, event_capture):
        llm = FakeLLM([reply_text("Your name is Juan.")])
        registry = build_registry(
            make_stub("search_documents", "search docs"),
            make_stub("recall_memory", "recall memory"),
        )
        runner = AgentRunner(llm_client=llm, tool_registry=registry)

        turn = make_turn(
            user_message="what is my name?",
            conversation_history=[
                {"role": "user", "content": "my name is Juan"},
                {"role": "assistant", "content": "Hey Juan."},
            ],
            bucket_files=[fake_file("notes.pdf")],
        )

        output = await runner.run(turn, dummy_db, on_event=event_capture)

        assert "juan" in output.assistant_message.lower()
        assert registry["search_documents"].fn.calls == []
        assert registry["recall_memory"].fn.calls == []

    async def test_history_is_passed_into_llm_messages(self, dummy_db):
        """The runner must put the chat history in the LLM's `messages`."""
        llm = FakeLLM([reply_text("Sure.")])
        runner = AgentRunner(llm_client=llm, tool_registry={})

        turn = make_turn(
            user_message="what is my name?",
            conversation_history=[
                {"role": "user", "content": "my name is juan"},
                {"role": "assistant", "content": "Hey Juan."},
            ],
        )
        await runner.run(turn, None, on_event=None)

        history_in_call = llm.calls[0]["messages"]
        contents = [m.get("content", "") for m in history_in_call]
        assert any("my name is juan" in c for c in contents)
        assert any("hey juan" in c.lower() for c in contents)


class TestActiveFileFollowUp:
    """Old bug: follow-up 'draw it' lost track of the file."""

    async def test_follow_up_uses_active_file(self, dummy_db, event_capture):
        active = uuid.uuid4()
        section_result = ToolResult(
            summary="Section 'Methods' on pages 3-5: ...",
            pending_docs=[{
                "kind": "document",
                "label": "[doc] paper.pdf — Section 'Methods'",
                "file_id": str(active),
            }],
            active_file_update=active,
        )
        registry = build_registry(
            make_stub("get_section", "open a section", static_result=section_result,
                      params_schema={"type": "object", "properties": {
                          "file_id": {"type": "string"},
                          "heading": {"type": "string"},
                      }, "required": ["file_id", "heading"]}),
        )

        llm = FakeLLM([
            reply_tools(("get_section", {"file_id": str(active), "heading": "Methods"})),
            reply_text("Drawing it now — Methods is on pages 3-5..."),
        ])
        runner = AgentRunner(llm_client=llm, tool_registry=registry)

        turn = make_turn(
            user_message="draw it",
            active_file=active,
            bucket_files=[fake_file("paper.pdf")],
            conversation_history=[
                {"role": "user", "content": "summarize paper.pdf"},
                {"role": "assistant", "content": "It is about X."},
            ],
        )

        output = await runner.run(turn, dummy_db, on_event=event_capture)

        # The model received the active file in the system prompt
        sys_prompt = llm.calls[0]["system_prompt"]
        assert str(active) in sys_prompt
        assert "paper.pdf" in sys_prompt
        # It then passed that file_id into get_section
        assert registry["get_section"].fn.calls[0]["file_id"] == str(active)
        # active_file persisted
        assert output.active_file == active

    async def test_prompt_signals_no_active_file_when_unset(self, dummy_db):
        llm = FakeLLM([reply_text("ok")])
        runner = AgentRunner(llm_client=llm, tool_registry={})
        turn = make_turn(
            user_message="hi",
            bucket_files=[fake_file("a.pdf"), fake_file("b.pdf")],
        )
        await runner.run(turn, dummy_db, on_event=None)
        sys_prompt = llm.calls[0]["system_prompt"]
        assert "Active file: (none" in sys_prompt


class TestWrongDocumentPrevention:
    """Old bug: vague 'this file' grabbed a random doc. New brain asks."""

    async def test_ask_user_halts_loop_and_returns_question(self, dummy_db, event_capture):
        ask_q = "Which file do you mean — paper.pdf or notes.pdf?"
        registry = build_registry(
            make_stub("ask_user", "ask the user",
                      params_schema={"type": "object", "properties": {
                          "question": {"type": "string"},
                          "options": {"type": "array", "items": {"type": "string"}},
                      }, "required": ["question"]},
                      result_fn=lambda args: ToolResult(summary=f"(asked: {args['question']})")),
            make_stub("search_documents", "search"),
        )

        # Tool stubs DON'T set state.clarifying_question — the real tool does.
        # Bypass: hijack ask_user via a wrapper that mimics the real tool.
        async def ask_user_real(state, turn, db, args):
            state.action_required = True
            state.action_type = "clarify"
            state.action_options = args.get("options") or None
            state.clarifying_question = args["question"]
            return ToolResult(summary=f"(asked: {args['question']})",
                              user_visible_label=args["question"])
        registry["ask_user"].fn = ask_user_real

        llm = FakeLLM([
            reply_tools(("ask_user", {"question": ask_q, "options": ["paper.pdf", "notes.pdf"]})),
        ])
        runner = AgentRunner(llm_client=llm, tool_registry=registry)

        turn = make_turn(
            user_message="explain this file",
            bucket_files=[fake_file("paper.pdf"), fake_file("notes.pdf")],
        )

        output = await runner.run(turn, dummy_db, on_event=event_capture)

        assert output.action_required is True
        assert output.action_type == "clarify"
        assert ask_q in output.assistant_message
        # No random doc grabbed
        assert registry["search_documents"].fn.calls == []


class TestWebOffBehavior:
    """Old bug: agent could trigger web searches even when toggle was off."""

    async def test_web_off_returns_polite_reply_and_does_not_search(self, dummy_db, event_capture):
        # We use the REAL search_web tool here because the web-off check is in
        # the tool body itself.
        from app.services.agent.harness.tools import build_registry as build_real_registry
        real_registry = build_real_registry()

        # Patch the web search so a stray call would explode the test.
        called: list[str] = []
        from app.services.agent.harness import tools as tools_mod
        original_web = tools_mod.web_mod.search_web

        async def boom(*a, **k):
            called.append("called")
            raise AssertionError("search_web should NOT be invoked when web is off")

        tools_mod.web_mod.search_web = boom  # type: ignore
        try:
            llm = FakeLLM([
                reply_tools(("search_web", {"query": "latest crypto news"})),
                reply_text("Your web mode is off — turn it on from the icon in the input bar."),
            ])
            runner = AgentRunner(llm_client=llm, tool_registry=real_registry)

            turn = make_turn(
                user_message="search the web for crypto news",
                web_mode="bucket_only",
                bucket_files=[fake_file("notes.pdf")],
            )
            output = await runner.run(turn, dummy_db, on_event=event_capture)
        finally:
            tools_mod.web_mod.search_web = original_web  # type: ignore

        assert called == []
        assert "web mode is off" in output.assistant_message.lower()
        assert output.used_web is False

    async def test_web_override_true_lets_search_run(self, dummy_db):
        """If the user toggled web on for this message, the bucket_only setting
        is overridden."""
        from app.services.agent.harness.tools import build_registry as build_real_registry
        real_registry = build_real_registry()

        from app.services.agent.harness import tools as tools_mod

        class _FakeWebResult:
            def __init__(self, title, url, snippet, score):
                self.title = title
                self.url = url
                self.snippet = snippet
                self.score = score

        async def fake_search(query, max_results=5):
            return [_FakeWebResult("BTC News", "https://example.com/btc", "btc snippet", 0.9)]

        original_web = tools_mod.web_mod.search_web
        tools_mod.web_mod.search_web = fake_search  # type: ignore
        try:
            llm = FakeLLM([
                reply_tools(("search_web", {"query": "btc"})),
                reply_text("Here's the latest from the web: ..."),
            ])
            runner = AgentRunner(llm_client=llm, tool_registry=real_registry)
            turn = make_turn(
                user_message="latest btc",
                web_mode="bucket_only",
                web_override=True,
                bucket_files=[],
            )
            output = await runner.run(turn, dummy_db, on_event=None)
        finally:
            tools_mod.web_mod.search_web = original_web  # type: ignore

        assert output.used_web is True
        assert any(s.get("kind") == "web" for s in output.sources)


class TestPlanAndTodoEvents:
    """Old bug: no live plan/TODO. New brain emits plan_update events."""

    async def test_make_plan_emits_plan_update(self, dummy_db, event_capture):
        # Use REAL make_plan + update_plan tools (they mutate state correctly)
        from app.services.agent.harness.tools import (
            _t_make_plan, _t_update_plan,
        )
        registry = build_registry(
            make_stub("noop", "noop"),
        )
        registry["make_plan"] = ToolDefinition(
            name="make_plan",
            description="make a plan",
            params_schema={"type": "object", "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
            }, "required": ["items"]},
            fn=_t_make_plan,
        )
        registry["update_plan"] = ToolDefinition(
            name="update_plan",
            description="update plan",
            params_schema={"type": "object", "properties": {
                "id": {"type": "integer"},
                "status": {"type": "string"},
            }, "required": ["id", "status"]},
            fn=_t_update_plan,
        )

        llm = FakeLLM([
            reply_tools(("make_plan", {"items": ["find tax files", "read 2024 return", "compare"]})),
            reply_tools(("update_plan", {"id": 1, "status": "done"})),
            reply_tools(("update_plan", {"id": 2, "status": "in_progress"})),
            reply_text("Done — the $20k jump is from X."),
        ])
        runner = AgentRunner(llm_client=llm, tool_registry=registry)

        turn = make_turn(user_message="compare my 2023 vs 2024 taxes")
        output = await runner.run(turn, dummy_db, on_event=event_capture)

        plan_snapshots = event_capture.plan_snapshots()
        assert len(plan_snapshots) >= 3  # one per iteration where plan exists

        # Final plan must be on the TurnOutput
        assert output.plan is not None
        assert len(output.plan) == 3
        statuses = {item["id"]: item["status"] for item in output.plan}
        assert statuses[1] == "done"
        assert statuses[2] == "in_progress"
        assert statuses[3] == "pending"

        # Compact plan view must be injected into the LLM messages
        all_msgs_text = "\n".join(
            str(m.get("content", ""))
            for call in llm.calls for m in call["messages"]
        )
        assert "PLAN:" in all_msgs_text


class TestMechanicalSourceTracking:
    """Old bug: sources came from the LLM's USED: marker (often missing).
    New brain tracks them from what tools actually returned."""

    async def test_sources_collected_from_tool_results(self, dummy_db):
        file_id = uuid.uuid4()
        search_result = ToolResult(
            summary="found something on page 7",
            pending_docs=[{
                "kind": "document",
                "label": "[doc] tax_2024.pdf — Page 7",
                "file_id": str(file_id),
                "page": 7,
            }],
            active_file_update=file_id,
        )
        registry = build_registry(
            make_stub("search_documents", "search", static_result=search_result,
                      params_schema={"type": "object", "properties": {
                          "query": {"type": "string"},
                      }, "required": ["query"]}),
        )

        llm = FakeLLM([
            reply_tools(("search_documents", {"query": "deductions"})),
            reply_text("You claimed $X in deductions on page 7."),
            # ^ note: no USED: marker — sources are mechanical
        ])
        runner = AgentRunner(llm_client=llm, tool_registry=registry)
        turn = make_turn(user_message="what deductions did I claim?")

        output = await runner.run(turn, dummy_db, on_event=None)

        # The doc source is in the output even though the LLM never wrote USED:.
        assert any(s.get("file_id") == str(file_id) and s.get("page") == 7
                   for s in output.sources)
        # No fallback general source — we used a real doc.
        assert not any(s.get("kind") == "general" for s in output.sources)


class TestRepeatToolCallGuard:
    """Old bug: the loop could re-run the same tool forever. New brain
    fingerprints calls and blocks the duplicate."""

    async def test_duplicate_call_short_circuits(self, dummy_db, event_capture):
        registry = build_registry(
            make_stub("search_documents", "search",
                      params_schema={"type": "object", "properties": {
                          "query": {"type": "string"},
                      }, "required": ["query"]},
                      static_result=ToolResult(summary="hit", pending_docs=[{
                          "kind": "document", "label": "[doc] x", "file_id": str(uuid.uuid4()),
                      }])),
        )

        llm = FakeLLM([
            reply_tools(("search_documents", {"query": "renewal"})),
            reply_tools(("search_documents", {"query": "renewal"})),  # DUPE
            reply_text("Final answer."),
        ])
        runner = AgentRunner(llm_client=llm, tool_registry=registry)
        turn = make_turn(user_message="find renewal date")

        await runner.run(turn, dummy_db, on_event=event_capture)

        # The TOOL only ran once even though the LLM emitted the call twice.
        assert len(registry["search_documents"].fn.calls) == 1
        # The repeat observation should have been fed back to the LLM
        repeat_msgs = []
        for call in llm.calls:
            for msg in call["messages"]:
                if msg.get("role") == "tool" and "already ran" in str(msg.get("content", "")):
                    repeat_msgs.append(msg)
        assert len(repeat_msgs) >= 1


class TestEmptyBucketBehavior:
    """Old bug: agent invented files when the bucket was empty.
    New brain sees the empty state in its system prompt."""

    async def test_prompt_says_bucket_is_empty(self, dummy_db):
        llm = FakeLLM([reply_text("Your bucket is empty — upload something.")])
        runner = AgentRunner(llm_client=llm, tool_registry={})
        turn = make_turn(user_message="what files do I have?", bucket_files=[])

        await runner.run(turn, dummy_db, on_event=None)

        sys_prompt = llm.calls[0]["system_prompt"]
        assert "(this bucket is empty right now" in sys_prompt

    async def test_processing_files_notice_in_prompt(self, dummy_db):
        llm = FakeLLM([reply_text("ok")])
        runner = AgentRunner(llm_client=llm, tool_registry={})
        turn = make_turn(
            user_message="hi",
            bucket_files=[
                fake_file("ready.pdf", status="ready"),
                fake_file("upping.pdf", status="processing"),
                fake_file("up2.pdf", status="uploading"),
            ],
        )
        await runner.run(turn, dummy_db, on_event=None)

        sys_prompt = llm.calls[0]["system_prompt"]
        assert "2 files still processing" in sys_prompt or "2 file" in sys_prompt
        assert "[processing]" in sys_prompt
        assert "[uploading]" in sys_prompt


class TestMetaCloserSynthesis:
    """Old bug (49-step case): the model did the real work as narration between
    tool calls, then ended its turn with a thin meta-closer ("You got it. All
    your questions have been answered.") — which was ALL the user saw. The runner
    must reject that closer and synthesize the real answer instead."""

    def _doc_result(self):
        return ToolResult(
            summary="found relevant text",
            pending_docs=[{
                "kind": "document", "label": "[doc] f.pdf — Page 1",
                "file_id": str(uuid.uuid4()), "page": 1, "is_summary": False,
            }],
        )

    async def test_meta_closer_triggers_synthesis(self, dummy_db, event_capture):
        # 3 tool calls (real work, no plan needed) → meta-closer → synthesized answer.
        synthesized = "1. Addresses: 701 Tillery St. 2. Reviews: mention teens. 3. Claims: 79%."
        llm = FakeLLM([
            reply_tools(("search_documents", {"query": "addresses"})),
            reply_tools(("search_documents", {"query": "teen reviews"})),
            reply_tools(("search_documents", {"query": "number claims"})),
            reply_text("You got it. All your questions from the plan have been answered."),
            reply_text(synthesized),
        ])
        stub = make_stub("search_documents", "search docs", static_result=self._doc_result())
        runner = AgentRunner(llm_client=llm, tool_registry=build_registry(stub))
        turn = make_turn(user_message="five questions in one", bucket_files=[fake_file("f.pdf")])

        output = await runner.run(turn, dummy_db, on_event=event_capture)

        # The synthesized answer wins; the meta-closer is NOT what the user sees.
        assert "701 Tillery St" in output.assistant_message
        assert "79%" in output.assistant_message
        assert "all your questions from the plan have been answered" not in output.assistant_message.lower()

    async def test_real_answer_is_not_replaced(self, dummy_db, event_capture):
        # Control: a genuine, substantive final answer must pass through untouched
        # (no wasted synthesis call).
        real = (
            "Here are your answers:\n1. Ingredient list: not provided in the document.\n"
            "2. Addresses: 701 Tillery Street, Texas.\n3. The page contrasts mainstream "
            "skincare (70% water) with Norse Organics (0% water) at length."
        )
        llm = FakeLLM([
            reply_tools(("search_documents", {"query": "stuff"})),
            reply_text(real),
        ])
        stub = make_stub("search_documents", "search docs", static_result=self._doc_result())
        runner = AgentRunner(llm_client=llm, tool_registry=build_registry(stub))
        turn = make_turn(user_message="a question", bucket_files=[fake_file("f.pdf")])

        output = await runner.run(turn, dummy_db, on_event=event_capture)

        assert "701 Tillery Street" in output.assistant_message
        # Only 2 LLM calls happened — no synthesis pass was triggered.
        assert len(llm.calls) == 2


class TestMetaCloserDetector:
    """Unit coverage for the _is_incomplete_final heuristic."""

    def test_flags_meta_closers_and_thin_text(self):
        from app.services.agent.harness.runner import _is_incomplete_final
        assert _is_incomplete_final("You got it. All your questions from the plan have been answered.")
        assert _is_incomplete_final("All set!")
        assert _is_incomplete_final("Done.")
        # Real answers pass through.
        assert not _is_incomplete_final("No, the full ingredient list is not provided in the document.")
        assert not _is_incomplete_final("1. A is x. 2. B is y. 3. C is z. " * 10)
