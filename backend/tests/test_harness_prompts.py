"""
Tests for the runtime-context block injected into every system prompt.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.services.agent.harness.contract import BucketFile
from app.services.agent.harness.prompts import (
    SYSTEM_PROMPT,
    build_runtime_context,
)


def _file(name: str, *, status: str = "ready", agent: bool = False) -> BucketFile:
    return BucketFile(file_id=uuid.uuid4(), name=name, status=status, is_agent_written=agent)


NOW = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc)


class TestSystemPrompt:
    def test_prompt_warns_against_leaking_internals(self):
        assert '"chunks"' in SYSTEM_PROMPT or "chunks" in SYSTEM_PROMPT
        assert "RAG" in SYSTEM_PROMPT or "rag" in SYSTEM_PROMPT.lower()

    def test_prompt_has_two_channels_rule(self):
        assert "Two channels" in SYSTEM_PROMPT or "two channels" in SYSTEM_PROMPT.lower()

    def test_prompt_mentions_ask_user_for_ambiguity(self):
        assert "ask_user" in SYSTEM_PROMPT


class TestRuntimeContext:
    def test_empty_bucket_message(self):
        ctx = build_runtime_context(
            active_file=None, bucket_files=[],
            web_mode="smart", web_override=None, now=NOW,
        )
        assert "(this bucket is empty right now" in ctx

    def test_active_file_resolved_to_name_and_id(self):
        f = _file("paper.pdf")
        ctx = build_runtime_context(
            active_file=f.file_id, bucket_files=[f],
            web_mode="smart", web_override=None, now=NOW,
        )
        assert "paper.pdf" in ctx
        assert str(f.file_id) in ctx

    def test_active_file_unknown_id_is_treated_as_unset(self):
        ghost = uuid.uuid4()
        ctx = build_runtime_context(
            active_file=ghost, bucket_files=[_file("a.pdf")],
            web_mode="smart", web_override=None, now=NOW,
        )
        assert "no longer exists" in ctx

    def test_web_mode_smart_label(self):
        ctx = build_runtime_context(
            active_file=None, bucket_files=[], web_mode="smart",
            web_override=None, now=NOW,
        )
        assert "AUTO" in ctx

    def test_web_mode_bucket_only_label(self):
        ctx = build_runtime_context(
            active_file=None, bucket_files=[], web_mode="bucket_only",
            web_override=None, now=NOW,
        )
        assert "OFF" in ctx
        assert "turn it on" in ctx.lower()

    def test_web_override_true(self):
        ctx = build_runtime_context(
            active_file=None, bucket_files=[], web_mode="bucket_only",
            web_override=True, now=NOW,
        )
        assert "ON" in ctx
        assert "user opted in" in ctx

    def test_processing_files_notice(self):
        files = [
            _file("ready.pdf", status="ready"),
            _file("proc.pdf", status="processing"),
            _file("up.pdf", status="uploading"),
        ]
        ctx = build_runtime_context(
            active_file=None, bucket_files=files, web_mode="smart",
            web_override=None, now=NOW,
        )
        assert "still processing" in ctx
        assert "[processing]" in ctx
        assert "[uploading]" in ctx

    def test_agent_written_files_tagged(self):
        f = _file("note.md", agent=True)
        ctx = build_runtime_context(
            active_file=None, bucket_files=[f], web_mode="smart",
            web_override=None, now=NOW,
        )
        assert "[agent-written]" in ctx

    def test_now_included(self):
        ctx = build_runtime_context(
            active_file=None, bucket_files=[], web_mode="smart",
            web_override=None, now=NOW,
        )
        assert "2026-06-10" in ctx
