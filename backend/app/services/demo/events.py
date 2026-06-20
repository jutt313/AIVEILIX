"""Demo activity event logging — one tiny helper used across the demo layer."""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demo import DemoEvent

# Canonical event types (kept in sync with the model docstring + admin timeline).
EVENT_TYPES = {
    "login",
    "message_sent",
    "file_uploaded",
    "team_invited",
    "mcp_opened",
    "tour_completed",
    "popup_shown",
    "popup_snoozed",
    "survey_submitted",
    "meeting_requested",
    "limit_hit",
}


async def log_event(
    db: AsyncSession,
    *,
    demo_link_id: uuid.UUID,
    demo_lead_id: uuid.UUID,
    event_type: str,
    payload: dict | None = None,
    commit: bool = False,
) -> DemoEvent:
    event = DemoEvent(
        demo_link_id=demo_link_id,
        demo_lead_id=demo_lead_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    if commit:
        await db.commit()
    return event
