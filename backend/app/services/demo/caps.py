"""
Server-side cap enforcement for the demo layer (the UI is convenience only).

All resource caps are **per bucket** (a shared pool across the company's leads).
Comebacks are the one exception — counted **per lead** (by email) and checked at
entry. Every count is read live so it can never drift from reality.

On exceed, ``check_cap`` raises HTTP 409 with ``{"limit": <kind>}`` so the
frontend can open the "you've reached the demo limit — let's talk" pop-up and
block the action.
"""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message
from app.models.demo import DemoEvent, DemoLead, DemoLink


async def count_threads(db: AsyncSession, link: DemoLink) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(Conversation)
            .join(DemoLead, Conversation.demo_lead_id == DemoLead.id)
            .where(DemoLead.demo_link_id == link.id)
        )
        or 0
    )


async def count_messages(db: AsyncSession, link: DemoLink) -> int:
    """Visitor-sent (user-role) messages across the whole demo bucket."""
    return int(
        await db.scalar(
            select(func.count())
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(DemoLead, Conversation.demo_lead_id == DemoLead.id)
            .where(DemoLead.demo_link_id == link.id, Message.role == "user")
        )
        or 0
    )


async def count_files(db: AsyncSession, link: DemoLink) -> int:
    """Visitor-uploaded files, tracked via ``file_uploaded`` events for this link.

    Prebuild docs are uploaded by the admin through the admin API and never log a
    demo event, so this counts only what visitors uploaded — exactly the cap's
    intent.
    """
    return int(
        await db.scalar(
            select(func.count())
            .select_from(DemoEvent)
            .where(DemoEvent.demo_link_id == link.id, DemoEvent.event_type == "file_uploaded")
        )
        or 0
    )


async def count_team_members(db: AsyncSession, link: DemoLink) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(DemoLead)
            .where(DemoLead.demo_link_id == link.id, DemoLead.is_team_member.is_(True))
        )
        or 0
    )


async def usage_counts(db: AsyncSession, link: DemoLink) -> dict[str, int]:
    """Live usage for the header + UI. Cheap COUNTs."""
    return {
        "threads": await count_threads(db, link),
        "messages": await count_messages(db, link),
        "files": await count_files(db, link),
        "team_members": await count_team_members(db, link),
    }


def _deny(kind: str) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"limit": kind})


async def check_cap(
    db: AsyncSession,
    link: DemoLink,
    kind: str,
    *,
    lead: DemoLead | None = None,
) -> None:
    """Raise HTTP 409 ``{"limit": kind}`` when the action would exceed its cap.

    ``kind`` ∈ {threads, messages, files, team_members, comebacks}. ``comebacks``
    requires ``lead`` (it's per-lead). Call this *before* performing the action.
    """
    if kind == "threads":
        if await count_threads(db, link) >= link.cap_threads:
            _deny("threads")
    elif kind == "messages":
        if await count_messages(db, link) >= link.cap_messages:
            _deny("messages")
    elif kind == "files":
        if await count_files(db, link) >= link.cap_files:
            _deny("files")
    elif kind == "team_members":
        if await count_team_members(db, link) >= link.cap_team_members:
            _deny("team_members")
    elif kind == "comebacks":
        if lead is None:
            raise ValueError("comebacks cap requires a lead")
        # comeback_count is incremented on each successful entry; block once the
        # lead has already used all their allowed returns.
        if lead.comeback_count >= link.cap_comebacks:
            _deny("comebacks")
    else:
        raise ValueError(f"unknown cap kind: {kind}")
