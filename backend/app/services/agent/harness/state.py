"""
Agent state carried across the turn.

active_file — what we're focused on right now (e.g. user said "summarize the
              tax return" then "what about deductions" → second turn keeps file).
plan        — the TODO. Empty for trivial turns. Built ONLY after scouting,
              when 2+ actions remain.
steps       — model-written narration lines for the UI.
call_hashes — fingerprint guard. Don't re-run the same tool with the same args.
stall_count — two consecutive no-new-info calls = stop.
sources     — mechanical citation collection: what tools actually returned.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Literal


PlanStatus = Literal["pending", "in_progress", "done", "blocked"]
_STATUS_GLYPH: dict[str, str] = {
    "pending": "◻",
    "in_progress": "▶",
    "done": "✓",
    "blocked": "✗",
}


@dataclass(slots=True)
class PlanItem:
    id: int
    task: str
    status: PlanStatus = "pending"

    def to_payload(self) -> dict[str, object]:
        return {"id": self.id, "task": self.task, "status": self.status}


@dataclass(slots=True)
class StepEvent:
    """Narration line shown live in the UI under the in-progress message."""
    type: str   # "thinking" | "reading_memory" | "searching_web" | "retrieving_files" | "tool" | "answer"
    label: str
    tool: str | None = None

    def to_payload(self) -> dict[str, str]:
        out: dict[str, str] = {"type": self.type, "label": self.label}
        if self.tool:
            out["tool"] = self.tool
        return out


@dataclass(slots=True)
class ToolCallRecord:
    """Internal record of a tool call we ran this turn."""
    name: str
    args: dict[str, object]
    result_summary: str
    sources_added: int = 0
    success: bool = True


@dataclass
class AgentState:
    """Mutable working state for ONE turn of the brain."""
    active_file: uuid.UUID | None = None
    plan: list[PlanItem] = field(default_factory=list)
    steps: list[StepEvent] = field(default_factory=list)
    call_hashes: set[str] = field(default_factory=set)
    call_records: list[ToolCallRecord] = field(default_factory=list)

    stall_count: int = 0
    total_steps: int = 0
    last_results_signature: str | None = None

    used_web: bool = False
    # Document / web sources actually returned and used to write the final answer.
    # Collected mechanically by the harness, not from a USED: marker.
    pending_doc_sources: list[dict[str, object]] = field(default_factory=list)
    pending_web_sources: list[dict[str, object]] = field(default_factory=list)
    used_doc_sources: list[dict[str, object]] = field(default_factory=list)
    used_web_sources: list[dict[str, object]] = field(default_factory=list)
    used_memory: bool = False

    # Loop budget
    started_at: float = field(default_factory=time.monotonic)

    # Optional: the agent asked the user to clarify something.
    action_required: bool = False
    action_type: str | None = None
    action_options: list[str] | None = None
    clarifying_question: str | None = None

    # ------------------------------------------------------------------ helpers

    def fingerprint(self, name: str, args: dict[str, object]) -> str:
        """Stable hash of a tool call. Used to detect repeat calls."""
        normalized = json.dumps(args, sort_keys=True, default=str)
        return hashlib.sha1(f"{name}|{normalized}".encode("utf-8")).hexdigest()

    def elapsed_seconds(self) -> float:
        return time.monotonic() - self.started_at

    # --------------------------------------------------------------------- plan

    def set_plan(self, items: list[str]) -> None:
        """Replace the plan with new tasks. Status defaults to pending."""
        self.plan = [
            PlanItem(id=i, task=task) for i, task in enumerate(items, start=1)
        ]

    def update_plan_item(self, item_id: int, status: PlanStatus) -> None:
        for item in self.plan:
            if item.id == item_id:
                item.status = status
                return

    def next_pending(self) -> PlanItem | None:
        for item in self.plan:
            if item.status == "pending":
                return item
        return None

    def all_done(self) -> bool:
        return all(item.status in ("done", "blocked") for item in self.plan)

    def plan_payload(self) -> list[dict[str, object]]:
        return [item.to_payload() for item in self.plan]

    def compact_plan_view(self) -> str:
        if not self.plan:
            return ""
        return " ".join(
            f"{item.id}.{_STATUS_GLYPH.get(item.status, '?')} {item.task}"
            for item in self.plan
        )

    # -------------------------------------------------------------------- steps

    def add_step(self, type_: str, label: str, *, tool: str | None = None) -> StepEvent:
        ev = StepEvent(type=type_, label=label, tool=tool)
        self.steps.append(ev)
        return ev

    def steps_payload(self) -> list[dict[str, str]]:
        return [s.to_payload() for s in self.steps]

    # --------------------------------------------------- mechanical source pool

    def commit_pending_sources(self) -> None:
        """Promote any pending source (added by a tool that was used) to the
        final-used list. Called after the model writes its final answer."""
        for src in self.pending_doc_sources:
            if src not in self.used_doc_sources:
                self.used_doc_sources.append(src)
        for src in self.pending_web_sources:
            if src not in self.used_web_sources:
                self.used_web_sources.append(src)

    def reset_pending_sources(self) -> None:
        self.pending_doc_sources = []
        self.pending_web_sources = []


# ─── budget caps (from the design doc §9) ────────────────────────────────────

MAX_TOOL_CALLS = 30  # raised from 15 — multi-question turns decompose into one search per question
SOFT_TIMEOUT_SECONDS = 7 * 60
HARD_TIMEOUT_SECONDS = 10 * 60
MAX_STALL = 2
MAX_RETRIES_PER_GOAL = 3
