"""
Turn contract — pure dataclasses, no logic.

A turn = (history + state + tools) → (answer + sources + state).
Input/output shapes are explicit so the harness is replaceable.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Awaitable, Callable, Literal


@dataclass(slots=True)
class BucketFile:
    """Minimal file record passed into the turn — just what the brain needs."""
    file_id: uuid.UUID
    name: str
    status: str  # uploading | processing | ready | failed
    is_agent_written: bool = False


@dataclass(slots=True)
class TurnInput:
    """Everything a single turn of the brain needs to think."""
    user_message: str
    conversation_history: list[dict[str, str]]  # [{role: user|assistant, content: str, sender_name?: str}, ...]
    active_file: uuid.UUID | None
    bucket_files: list[BucketFile]
    web_mode: str                                # smart | bucket_only | always_search
    web_override: bool | None                    # per-turn override (None = use mode)
    model: str                                   # provider id (claude/gemini/openai/...)
    now: datetime
    bucket_id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    scope_file_ids: list[uuid.UUID] | None = None  # thread file scope (None = full bucket, [] = no files, [...] = subset)
    current_speaker: str | None = None             # display name of the team member sending this turn (None = workspace owner)


@dataclass(slots=True)
class SourceCitation:
    """One row in the Sources block under the assistant message."""
    kind: Literal["document", "web", "memory", "general"]
    label: str
    file_id: str | None = None
    chunk_id: str | None = None
    page: int | None = None
    url: str | None = None
    title: str | None = None
    score: float | None = None

    def to_payload(self) -> dict[str, object]:
        out: dict[str, object] = {"kind": self.kind, "label": self.label}
        if self.file_id:
            out["file_id"] = self.file_id
        if self.chunk_id:
            out["chunk_id"] = self.chunk_id
        if self.page is not None:
            out["page"] = self.page
        if self.url:
            out["url"] = self.url
        if self.title:
            out["title"] = self.title
        if self.score is not None:
            out["score"] = round(float(self.score), 4)
        return out


@dataclass(slots=True)
class TurnOutput:
    """What the harness returns to the endpoint."""
    assistant_message: str
    sources: list[dict[str, object]]
    steps: list[dict[str, str]]
    plan: list[dict[str, object]] | None
    active_file: uuid.UUID | None
    used_web: bool
    action_required: bool = False
    action_type: str | None = None
    action_options: list[str] | None = None
    chunks_used: list[dict[str, object]] = field(default_factory=list)


# Event callback used to stream step/plan/token events to the SSE endpoint.
# `kind` is one of: "step" | "plan_update" | "token" | "done"
EventCallback = Callable[[dict[str, object]], Awaitable[None]]
