"""
Narration utilities — emit live step events to the SSE callback.

Lines come from the MODEL (text the LLM emits between tool calls). The
harness also has a few mechanical fallbacks (we ran a search, no results,
etc.) so the UI never goes silent while the model is thinking.
"""
from __future__ import annotations

import logging

from app.services.agent.harness.contract import EventCallback
from app.services.agent.harness.state import AgentState, StepEvent

logger = logging.getLogger(__name__)


# Tool name → step category (used by the frontend to pick an icon).
TOOL_STEP_CATEGORY: dict[str, str] = {
    "search_documents": "retrieving_files",
    "list_files": "retrieving_files",
    "get_file_summary": "retrieving_files",
    "read_file": "retrieving_files",
    "get_file_stats": "retrieving_files",
    "get_page": "retrieving_files",
    "get_visual": "retrieving_files",
    "list_visuals": "retrieving_files",
    "get_section": "retrieving_files",
    "search_web": "searching_web",
    "fetch_url": "searching_web",
    "recall_memory": "reading_memory",
    "ask_user": "thinking",
}


def step_category_for(tool_name: str) -> str:
    return TOOL_STEP_CATEGORY.get(tool_name, "thinking")


async def emit_step(
    state: AgentState,
    on_event: EventCallback | None,
    *,
    type_: str,
    label: str,
    tool: str | None = None,
) -> StepEvent:
    """Record a narration line and stream it to the SSE channel."""
    ev = state.add_step(type_, label, tool=tool)
    if on_event is not None:
        try:
            await on_event({"kind": "step", "event": ev.to_payload()})
        except Exception:
            logger.debug("on_event step callback failed", exc_info=True)
    return ev


async def emit_plan_update(
    state: AgentState,
    on_event: EventCallback | None,
) -> None:
    """Stream the current plan to the UI so the checklist updates live."""
    if on_event is None:
        return
    try:
        await on_event({"kind": "plan_update", "plan": state.plan_payload()})
    except Exception:
        logger.debug("on_event plan_update callback failed", exc_info=True)


async def emit_token(
    on_event: EventCallback | None,
    token: str,
) -> None:
    """Stream a single token chunk of the final answer to the UI."""
    if on_event is None or not token:
        return
    try:
        await on_event({"kind": "token", "text": token})
    except Exception:
        logger.debug("on_event token callback failed", exc_info=True)
