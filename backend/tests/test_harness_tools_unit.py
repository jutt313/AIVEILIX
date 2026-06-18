"""
Unit tests for the harness tool wrappers themselves.

Mocks the underlying retrieval/web/file functions so we can assert each
neutral tool builds the right ToolResult.
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.agent.harness.contract import TurnInput
from app.services.agent.harness.state import AgentState
from app.services.agent.harness.tools import (
    _t_ask_user,
    _t_make_plan,
    _t_search_web,
    _t_update_plan,
    build_registry,
)

from tests.conftest import fake_file, make_turn


# ─────────────────────────────────────────────────────────────── ask_user ──

class TestAskUserTool:
    async def test_sets_state_for_clarification(self):
        state = AgentState()
        turn = make_turn(user_message="explain it")
        result = await _t_ask_user(
            state, turn, MagicMock(),
            {"question": "Which file?", "options": ["a.pdf", "b.pdf"]},
        )
        assert state.action_required is True
        assert state.action_type == "clarify"
        assert state.clarifying_question == "Which file?"
        assert state.action_options == ["a.pdf", "b.pdf"]
        assert result.user_visible_label == "Which file?"

    async def test_rejects_empty_question(self):
        state = AgentState()
        turn = make_turn()
        result = await _t_ask_user(state, turn, MagicMock(), {})
        assert result.success is False
        assert state.action_required is False

    async def test_caps_options_at_four(self):
        state = AgentState()
        turn = make_turn()
        await _t_ask_user(
            state, turn, MagicMock(),
            {"question": "pick", "options": ["a", "b", "c", "d", "e", "f"]},
        )
        assert len(state.action_options) == 4


# ─────────────────────────────────────────────────────────── make_plan / update_plan ──

class TestPlanTools:
    async def test_make_plan_sets_state(self):
        state = AgentState()
        result = await _t_make_plan(
            state, make_turn(), MagicMock(),
            {"items": ["find files", "read year 1", "compare"]},
        )
        assert result.success is True
        assert len(state.plan) == 3
        assert state.plan[0].task == "find files"

    async def test_make_plan_rejects_empty(self):
        state = AgentState()
        result = await _t_make_plan(state, make_turn(), MagicMock(), {"items": []})
        assert result.success is False
        assert state.plan == []

    async def test_make_plan_caps_at_ten(self):
        state = AgentState()
        await _t_make_plan(
            state, make_turn(), MagicMock(),
            {"items": [f"task {i}" for i in range(20)]},
        )
        assert len(state.plan) == 10

    async def test_update_plan_changes_status(self):
        state = AgentState()
        state.set_plan(["a", "b"])
        result = await _t_update_plan(
            state, make_turn(), MagicMock(), {"id": 1, "status": "done"},
        )
        assert result.success is True
        assert state.plan[0].status == "done"

    async def test_update_plan_rejects_bad_status(self):
        state = AgentState()
        state.set_plan(["a"])
        result = await _t_update_plan(
            state, make_turn(), MagicMock(), {"id": 1, "status": "WAT"},
        )
        assert result.success is False
        assert state.plan[0].status == "pending"

    async def test_update_plan_rejects_non_integer_id(self):
        state = AgentState()
        state.set_plan(["a"])
        result = await _t_update_plan(
            state, make_turn(), MagicMock(), {"id": "abc", "status": "done"},
        )
        assert result.success is False


# ─────────────────────────────────────────────────────────── search_web ──

class TestSearchWebTool:
    async def test_returns_web_off_reply_when_bucket_only(self):
        state = AgentState()
        turn = make_turn(user_message="search btc", web_mode="bucket_only")
        result = await _t_search_web(state, turn, MagicMock(), {"query": "btc"})
        assert result.web_off_reply is not None
        assert "off" in result.web_off_reply.lower()
        assert result.success is False

    async def test_web_off_when_explicit_override_false(self):
        state = AgentState()
        turn = make_turn(
            user_message="search",
            web_mode="always_search",
            web_override=False,
        )
        result = await _t_search_web(state, turn, MagicMock(), {"query": "x"})
        assert result.web_off_reply is not None

    async def test_runs_search_when_web_enabled(self):
        state = AgentState()
        turn = make_turn(user_message="search", web_mode="always_search")

        class FakeRes:
            def __init__(self, t, u, s, sc):
                self.title, self.url, self.snippet, self.score = t, u, s, sc

        async def fake_search(query, max_results=5):
            assert query == "btc"
            return [FakeRes("BTC News", "https://btc.example/x", "...", 0.9)]

        from app.services.agent.harness import tools as tools_mod
        orig = tools_mod.web_mod.search_web
        tools_mod.web_mod.search_web = fake_search  # type: ignore
        try:
            result = await _t_search_web(state, turn, MagicMock(), {"query": "btc"})
        finally:
            tools_mod.web_mod.search_web = orig  # type: ignore
        assert result.success is True
        assert len(result.pending_web) == 1
        assert result.pending_web[0]["url"] == "https://btc.example/x"


# ──────────────────────────────────────────────────── registry shape ──

class TestRegistryShape:
    def test_all_tool_names_present(self):
        registry = build_registry()
        expected = {
            "list_files", "list_bucket_members", "get_file_summary", "read_file",
            "search_documents", "get_file_stats", "read_outline",
            "get_page", "get_visual", "list_visuals", "get_section",
            "read_all_chunks", "search_web", "fetch_url", "recall_memory",
            "ask_user", "make_plan", "update_plan",
        }
        assert set(registry.keys()) == expected

    def test_every_tool_has_required_schema(self):
        registry = build_registry()
        for name, tool in registry.items():
            assert tool.description, f"{name} missing description"
            assert tool.params_schema.get("type") == "object", f"{name} schema not object"
            assert "properties" in tool.params_schema, f"{name} schema missing properties"

    def test_every_tool_function_is_async(self):
        import inspect
        registry = build_registry()
        for name, tool in registry.items():
            assert inspect.iscoroutinefunction(tool.fn), f"{name}.fn not async"
