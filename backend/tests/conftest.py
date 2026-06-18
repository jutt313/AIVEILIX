"""
Shared pytest config + fixtures for harness tests.

Provides:
- `FakeLLM` — a scripted LLM client. Hand it a queue of `Reply` objects and it
  pops one per `chat()` call. Lets us test the runner's loop without ever
  talking to a real provider.
- `make_turn` — convenience builder for `TurnInput`.
- `event_capture` — records every SSE `on_event` payload the runner emits.
- `dummy_db` — an `AsyncMock` posing as `AsyncSession`. The custom tool
  registries in tests don't touch it; the real harness tools that do touch it
  are tested separately with explicit mocks.
"""
from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable
from unittest.mock import AsyncMock

import pytest

# pytest-asyncio is configured via pytest.ini (asyncio_mode=auto).

from app.services.agent.harness.contract import BucketFile, TurnInput
from app.services.agent.harness.llm_client import LLMClient, Reply, ToolCall


# ─────────────────────────────────────────────────────────────── fake client ──

class FakeLLM(LLMClient):
    """Scripted LLM. `replies` is a deque drained in order. If exhausted,
    falls back to a generic final-text reply so tests don't deadlock."""

    native_tools = True

    def __init__(self, replies: list[Reply], provider: str = "fake"):
        self.provider = provider
        self.replies: deque[Reply] = deque(replies)
        self.calls: list[dict[str, Any]] = []   # every (system, messages, tools) tuple
        self.fallback_text = "Done."

    async def chat(self, system_prompt, messages, tools):
        # Deep-ish copy of inputs so later test assertions see the original state
        self.calls.append({
            "system_prompt": system_prompt,
            "messages": [dict(m) for m in messages],
            "tools": list(tools),
        })
        if self.replies:
            return self.replies.popleft()
        return Reply(kind="text", text=self.fallback_text)


def reply_text(text: str) -> Reply:
    return Reply(kind="text", text=text)


def reply_tools(*calls: tuple[str, dict[str, Any]], narration: list[str] | None = None) -> Reply:
    """Helper: `reply_tools(("search_documents", {"query": "x"}), ...)`."""
    tool_calls = [
        ToolCall(id=f"call_{i}", name=name, args=dict(args))
        for i, (name, args) in enumerate(calls, start=1)
    ]
    return Reply(kind="tool_calls", calls=tool_calls, narration_lines=narration or [])


# ─────────────────────────────────────────────────────────────── turn builder ──

def make_turn(
    *,
    user_message: str = "hello",
    conversation_history: list[dict[str, str]] | None = None,
    active_file: uuid.UUID | None = None,
    bucket_files: list[BucketFile] | None = None,
    web_mode: str = "smart",
    web_override: bool | None = None,
    scope_file_ids: list[uuid.UUID] | None = None,
) -> TurnInput:
    return TurnInput(
        user_message=user_message,
        conversation_history=conversation_history or [],
        active_file=active_file,
        bucket_files=bucket_files or [],
        web_mode=web_mode,
        web_override=web_override,
        model="fake",
        now=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
        bucket_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        conversation_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        scope_file_ids=scope_file_ids,
    )


def fake_file(name: str, *, status: str = "ready", agent_written: bool = False) -> BucketFile:
    return BucketFile(
        file_id=uuid.uuid4(),
        name=name,
        status=status,
        is_agent_written=agent_written,
    )


# ─────────────────────────────────────────────────────── event capture helper ──

@dataclass
class EventCapture:
    events: list[dict[str, Any]] = field(default_factory=list)

    async def __call__(self, payload: dict[str, Any]) -> None:
        self.events.append(payload)

    def of_kind(self, kind: str) -> list[dict[str, Any]]:
        return [e for e in self.events if e.get("kind") == kind]

    def step_labels(self) -> list[str]:
        return [
            (e.get("event") or {}).get("label", "")
            for e in self.events if e.get("kind") == "step"
        ]

    def step_types(self) -> list[str]:
        return [
            (e.get("event") or {}).get("type", "")
            for e in self.events if e.get("kind") == "step"
        ]

    def plan_snapshots(self) -> list[list[dict[str, Any]]]:
        return [e.get("plan") or [] for e in self.of_kind("plan_update")]

    def token_text(self) -> str:
        return "".join(e.get("text", "") for e in self.of_kind("token"))


@pytest.fixture
def event_capture() -> EventCapture:
    return EventCapture()


@pytest.fixture
def dummy_db() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def make_turn_fixture():
    """Expose `make_turn` as a fixture for tests that want to inject it."""
    return make_turn
