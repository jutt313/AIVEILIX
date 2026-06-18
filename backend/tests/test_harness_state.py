"""
Unit tests for AgentState — fingerprint, plan, stall, source pool.
"""
from __future__ import annotations

import uuid

import pytest

from app.services.agent.harness.state import (
    AgentState,
    PlanItem,
    MAX_STALL,
    MAX_TOOL_CALLS,
)


class TestFingerprint:
    def test_same_args_same_hash(self):
        state = AgentState()
        h1 = state.fingerprint("search_documents", {"query": "abc"})
        h2 = state.fingerprint("search_documents", {"query": "abc"})
        assert h1 == h2

    def test_different_args_different_hash(self):
        state = AgentState()
        h1 = state.fingerprint("search_documents", {"query": "abc"})
        h2 = state.fingerprint("search_documents", {"query": "xyz"})
        assert h1 != h2

    def test_arg_order_insensitive(self):
        state = AgentState()
        h1 = state.fingerprint("get_page", {"file_id": "f", "start": 1, "end": 3})
        h2 = state.fingerprint("get_page", {"end": 3, "start": 1, "file_id": "f"})
        assert h1 == h2

    def test_different_tool_different_hash(self):
        state = AgentState()
        h1 = state.fingerprint("a", {"x": 1})
        h2 = state.fingerprint("b", {"x": 1})
        assert h1 != h2

    def test_uuid_args_normalized_to_string(self):
        """`default=str` in fingerprint() must convert UUIDs cleanly."""
        state = AgentState()
        u = uuid.UUID("11111111-1111-1111-1111-111111111111")
        h1 = state.fingerprint("t", {"file_id": u})
        h2 = state.fingerprint("t", {"file_id": str(u)})
        assert h1 == h2


class TestPlan:
    def test_set_plan_creates_pending_items(self):
        state = AgentState()
        state.set_plan(["first", "second", "third"])
        assert len(state.plan) == 3
        assert all(item.status == "pending" for item in state.plan)
        assert [i.id for i in state.plan] == [1, 2, 3]

    def test_update_plan_item(self):
        state = AgentState()
        state.set_plan(["a", "b"])
        state.update_plan_item(2, "in_progress")
        assert state.plan[1].status == "in_progress"
        assert state.plan[0].status == "pending"

    def test_next_pending(self):
        state = AgentState()
        state.set_plan(["a", "b", "c"])
        state.update_plan_item(1, "done")
        assert state.next_pending().id == 2

    def test_next_pending_returns_none_when_done(self):
        state = AgentState()
        state.set_plan(["a"])
        state.update_plan_item(1, "done")
        assert state.next_pending() is None

    def test_all_done_includes_blocked(self):
        state = AgentState()
        state.set_plan(["a", "b"])
        state.update_plan_item(1, "done")
        state.update_plan_item(2, "blocked")
        assert state.all_done() is True

    def test_compact_view_uses_glyphs(self):
        state = AgentState()
        state.set_plan(["find tax files", "compare"])
        state.update_plan_item(1, "done")
        state.update_plan_item(2, "in_progress")
        view = state.compact_plan_view()
        assert "✓" in view and "▶" in view
        assert "1." in view and "2." in view

    def test_compact_view_empty_when_no_plan(self):
        state = AgentState()
        assert state.compact_plan_view() == ""

    def test_plan_payload_is_jsonable(self):
        state = AgentState()
        state.set_plan(["x"])
        payload = state.plan_payload()
        assert payload == [{"id": 1, "task": "x", "status": "pending"}]


class TestSourcePool:
    def test_commit_promotes_pending_to_used(self):
        state = AgentState()
        state.pending_doc_sources.append({"kind": "document", "file_id": "f1"})
        state.pending_web_sources.append({"kind": "web", "url": "https://x"})
        state.commit_pending_sources()
        assert state.used_doc_sources == [{"kind": "document", "file_id": "f1"}]
        assert state.used_web_sources == [{"kind": "web", "url": "https://x"}]

    def test_commit_does_not_dupe(self):
        state = AgentState()
        src = {"kind": "document", "file_id": "f1"}
        state.pending_doc_sources.append(src)
        state.commit_pending_sources()
        # Commit a second time — same item shouldn't double up
        state.pending_doc_sources.append(src)
        state.commit_pending_sources()
        assert state.used_doc_sources == [src]

    def test_reset_clears_pending(self):
        state = AgentState()
        state.pending_doc_sources.append({"file_id": "x"})
        state.pending_web_sources.append({"url": "y"})
        state.reset_pending_sources()
        assert state.pending_doc_sources == []
        assert state.pending_web_sources == []


class TestBudgetConstants:
    def test_caps_match_design(self):
        # Current harness cap: 30 calls, 7-min soft / 10-min hard, 2 stall.
        # Raised from 15 so multi-question and paged full-scan turns can finish.
        assert MAX_TOOL_CALLS == 30
        assert MAX_STALL == 2
