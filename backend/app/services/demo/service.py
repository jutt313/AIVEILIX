"""
Demo layer service — entry, invites, threads, chat, survey, meeting, MCP.

Everything here reuses the existing document + chat + MCP machinery and is scoped
to a single ``is_demo`` bucket via a :class:`DemoSession`. Demo visitors never
become ``users``; their chat threads run as the bucket owner (the admin) but are
tagged with ``demo_lead_id`` so they can be attributed and capped.
"""
from __future__ import annotations

import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.bucket import Bucket
from app.models.conversation import Conversation, Message
from app.models.demo import DemoLead, DemoLink, DemoMeetingRequest, DemoSurvey
from app.models.file import File
from app.models.mcp_token import BucketMcpToken
from app.services.agent.service import run_conversation_turn
from app.services.demo.caps import check_cap, usage_counts
from app.services.demo.events import log_event
from app.services.demo.session import DemoSession
from app.services.demo.tokens import create_demo_token

INVITE_TTL_DAYS = 7
DEFAULT_TEAM_COLORS = [
    "#6366F1", "#EC4899", "#F59E0B", "#10B981", "#3B82F6",
    "#8B5CF6", "#EF4444", "#14B8A6", "#F97316", "#06B6D4",
]


# ── identity / entry ──────────────────────────────────────────────────────────

def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def code_matches(link: DemoLink, code: str) -> bool:
    """Constant-time 4-digit code comparison."""
    return hmac.compare_digest((link.access_code or "").strip(), (code or "").strip())


async def get_active_link_by_slug(db: AsyncSession, slug: str) -> DemoLink:
    link = await db.scalar(select(DemoLink).where(DemoLink.slug == slug))
    if link is None:
        raise HTTPException(status_code=404, detail="This demo link was not found.")
    if not link.is_active or _link_expired(link):
        raise HTTPException(status_code=403, detail="This demo is no longer available.")
    return link


def _link_expired(link: DemoLink) -> bool:
    if link.expires_at is None:
        return False
    exp = link.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp <= datetime.now(timezone.utc)


async def enter_demo(
    db: AsyncSession,
    link: DemoLink,
    *,
    name: str,
    email: str,
    role: str | None,
) -> tuple[DemoLead, str]:
    """Upsert the primary lead by email, enforce the comeback cap, count the
    visit, log ``login``, and issue a demo session token."""
    email_norm = _norm_email(email)
    name = (name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Please enter your name.")
    if "@" not in email_norm:
        raise HTTPException(status_code=400, detail="Please enter a valid email.")

    lead = await db.scalar(
        select(DemoLead).where(
            DemoLead.demo_link_id == link.id,
            func.lower(DemoLead.email) == email_norm,
        )
    )
    if lead is None:
        lead = DemoLead(
            demo_link_id=link.id,
            name=name,
            email=email_norm,
            role=(role or "").strip() or None,
            is_team_member=False,
            comeback_count=0,
        )
        db.add(lead)
        await db.flush()
    else:
        # Returning visitor — enforce the per-lead comeback cap before counting.
        await check_cap(db, link, "comebacks", lead=lead)
        lead.name = name or lead.name
        if role is not None:
            lead.role = (role or "").strip() or None

    lead.comeback_count += 1
    lead.last_seen_at = datetime.now(timezone.utc)
    await log_event(
        db,
        demo_link_id=link.id,
        demo_lead_id=lead.id,
        event_type="login",
        payload={"visit": lead.comeback_count, "is_team_member": lead.is_team_member},
    )
    await db.commit()
    await db.refresh(lead)
    token = create_demo_token(str(link.id), str(lead.id))
    return lead, token


async def get_invite_info(db: AsyncSession, token: str) -> dict:
    """Validate an invite token without issuing a session (for the entry screen)."""
    lead = await db.scalar(select(DemoLead).where(DemoLead.invite_token == token))
    if lead is None or not lead.is_team_member:
        return {"valid": False}
    link = await db.get(DemoLink, lead.demo_link_id)
    if link is None or not link.is_active or _link_expired(link):
        return {"valid": False, "expired": True}
    expired = bool(
        lead.invite_token_expires_at
        and _aware(lead.invite_token_expires_at) <= datetime.now(timezone.utc)
    )
    # Resolve who invited them so the page can say "Alex invited you …" instead
    # of a generic message.
    inviter_name: str | None = None
    if lead.invited_by_lead_id is not None:
        inviter_name = await db.scalar(
            select(DemoLead.name).where(DemoLead.id == lead.invited_by_lead_id)
        )
    return {
        "valid": not expired,
        "expired": expired,
        "company_name": link.company_name,
        "name": lead.name,
        "email": lead.email,
        "color": lead.color,
        "inviter_name": inviter_name,
    }


async def accept_invite(db: AsyncSession, token: str) -> tuple[DemoLink, DemoLead, str]:
    """Resolve a team invite → confirm the lead, count the visit, issue a token."""
    lead = await db.scalar(select(DemoLead).where(DemoLead.invite_token == token))
    if lead is None or not lead.is_team_member:
        raise HTTPException(status_code=404, detail="This invite was not found.")
    link = await db.get(DemoLink, lead.demo_link_id)
    if link is None or not link.is_active or _link_expired(link):
        raise HTTPException(status_code=403, detail="This demo is no longer available.")
    if lead.invite_token_expires_at and _aware(lead.invite_token_expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="This invite has expired. Ask for a new one.")

    lead.comeback_count += 1
    lead.last_seen_at = datetime.now(timezone.utc)
    await log_event(
        db,
        demo_link_id=link.id,
        demo_lead_id=lead.id,
        event_type="login",
        payload={"visit": lead.comeback_count, "is_team_member": True},
    )
    await db.commit()
    await db.refresh(lead)
    demo_token = create_demo_token(str(link.id), str(lead.id))
    return link, lead, demo_token


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# ── bucket owner / helpers ─────────────────────────────────────────────────────

async def bucket_owner_id(db: AsyncSession, link: DemoLink) -> uuid.UUID:
    owner_id = await db.scalar(select(Bucket.user_id).where(Bucket.id == link.bucket_id))
    if owner_id is None:
        raise HTTPException(status_code=404, detail="Demo bucket not found.")
    return owner_id


# ── threads + chat ─────────────────────────────────────────────────────────────

async def list_threads(db: AsyncSession, session: DemoSession) -> list[Conversation]:
    """A lead sees only their own threads."""
    rows = await db.execute(
        select(Conversation)
        .where(
            Conversation.bucket_id == session.bucket_id,
            Conversation.demo_lead_id == session.lead_id,
        )
        .order_by(Conversation.updated_at.desc())
    )
    return list(rows.scalars().all())


async def create_thread(db: AsyncSession, session: DemoSession, *, title: str | None) -> Conversation:
    await check_cap(db, session.demo_link, "threads")
    owner_id = await bucket_owner_id(db, session.demo_link)
    conversation = Conversation(
        user_id=owner_id,
        bucket_id=session.bucket_id,
        title=(title or "New chat").strip() or "New chat",
        web_search_mode="smart",
        follow_up_mode="all_at_once",
        demo_lead_id=session.lead_id,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_demo_conversation(db: AsyncSession, session: DemoSession, conversation_id: str) -> Conversation:
    try:
        cid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    conversation = await db.scalar(
        select(Conversation).where(
            Conversation.id == cid,
            Conversation.bucket_id == session.bucket_id,
            Conversation.demo_lead_id == session.lead_id,
        )
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


async def list_messages(db: AsyncSession, session: DemoSession, conversation_id: str) -> list[Message]:
    await get_demo_conversation(db, session, conversation_id)
    rows = await db.execute(
        select(Message)
        .where(Message.conversation_id == uuid.UUID(conversation_id))
        .order_by(Message.created_at.asc())
    )
    return list(rows.scalars().all())


# ── per-thread file scope (reuses conversation_file_scope; read by the harness) ──

async def get_thread_scope(db: AsyncSession, session: DemoSession, conversation_id: str) -> dict:
    conversation = await get_demo_conversation(db, session, conversation_id)
    active = await db.scalar(
        text("SELECT file_scope_active FROM conversations WHERE id = :cid"),
        {"cid": conversation.id},
    )
    rows = await db.execute(
        text("SELECT file_id FROM conversation_file_scope WHERE conversation_id = :cid"),
        {"cid": conversation.id},
    )
    return {"file_ids": [str(r[0]) for r in rows.fetchall()], "scoped": bool(active)}


async def set_thread_scope(
    db: AsyncSession,
    session: DemoSession,
    conversation_id: str,
    file_ids: list[str],
    scoped: bool | None,
) -> dict:
    conversation = await get_demo_conversation(db, session, conversation_id)
    # scoped=None -> infer from file_ids (non-empty means filtered).
    active = scoped if scoped is not None else (len(file_ids) > 0)
    await db.execute(
        text("DELETE FROM conversation_file_scope WHERE conversation_id = :cid"),
        {"cid": conversation.id},
    )
    saved: list[str] = []
    if active:
        for fid in file_ids:
            try:
                fid_uuid = uuid.UUID(fid)
            except ValueError:
                continue
            res = await db.execute(
                text(
                    "INSERT INTO conversation_file_scope (conversation_id, file_id) "
                    "SELECT :cid, :fid WHERE EXISTS ("
                    "  SELECT 1 FROM files WHERE id = :fid AND bucket_id = :bid"
                    ") ON CONFLICT DO NOTHING RETURNING file_id"
                ),
                {"cid": conversation.id, "fid": fid_uuid, "bid": session.bucket_id},
            )
            if res.fetchone() is not None:
                saved.append(fid)
    await db.execute(
        text("UPDATE conversations SET file_scope_active = :a WHERE id = :cid"),
        {"a": active, "cid": conversation.id},
    )
    await db.commit()
    return {"file_ids": saved, "scoped": active}


async def run_demo_turn(
    db: AsyncSession,
    session: DemoSession,
    *,
    conversation_id: str,
    content: str,
    web_search: bool | None = None,
    on_step=None,
):
    """Enforce the message cap, run the existing harness turn as the bucket owner,
    tag the demo lead, and log ``message_sent``."""
    conversation = await get_demo_conversation(db, session, conversation_id)
    await check_cap(db, session.demo_link, "messages")
    owner_id = await bucket_owner_id(db, session.demo_link)

    result = await run_conversation_turn(
        db,
        user_id=str(owner_id),
        bucket_id=str(session.bucket_id),
        conversation_id=str(conversation.id),
        content=content,
        web_search_override=web_search,
        on_step=on_step,
    )
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type="message_sent",
        payload={"conversation_id": str(conversation.id)},
        commit=True,
    )
    return result


# ── files (prebuild docs the visitor explores) ─────────────────────────────────

async def list_demo_files(db: AsyncSession, session: DemoSession) -> list[File]:
    rows = await db.execute(
        select(File)
        .where(File.bucket_id == session.bucket_id)
        .order_by(File.created_at.asc())
    )
    return list(rows.scalars().all())


# ── team invite (from inside the demo) ─────────────────────────────────────────

async def invite_team_member(
    db: AsyncSession,
    session: DemoSession,
    *,
    name: str,
    email: str,
    color: str | None,
) -> DemoLead:
    """Create an invited team-member lead (cap-checked) with a fresh invite token."""
    name = (name or "").strip()
    email_norm = _norm_email(email)
    if not name:
        raise HTTPException(status_code=400, detail="Enter the teammate's name.")
    if "@" not in email_norm:
        raise HTTPException(status_code=400, detail="Enter a valid teammate email.")

    existing = await db.scalar(
        select(DemoLead).where(
            DemoLead.demo_link_id == session.link_id,
            func.lower(DemoLead.email) == email_norm,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="That person has already been added to this demo.")

    await check_cap(db, session.demo_link, "team_members")

    used_colors = {
        c for (c,) in (
            await db.execute(
                select(DemoLead.color).where(DemoLead.demo_link_id == session.link_id)
            )
        ).all()
        if c
    }
    chosen_color = (color or "").strip() or next(
        (c for c in DEFAULT_TEAM_COLORS if c not in used_colors), DEFAULT_TEAM_COLORS[0]
    )

    member = DemoLead(
        demo_link_id=session.link_id,
        name=name,
        email=email_norm,
        is_team_member=True,
        invited_by_lead_id=session.lead_id,
        invite_token=secrets.token_urlsafe(32),
        invite_token_expires_at=datetime.now(timezone.utc) + timedelta(days=INVITE_TTL_DAYS),
        color=chosen_color,
        comeback_count=0,
    )
    db.add(member)
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type="team_invited",
        payload={"invited_email": email_norm, "invited_name": name},
    )
    await db.commit()
    await db.refresh(member)
    return member


async def list_team(db: AsyncSession, session: DemoSession) -> list[DemoLead]:
    rows = await db.execute(
        select(DemoLead)
        .where(DemoLead.demo_link_id == session.link_id, DemoLead.is_team_member.is_(True))
        .order_by(DemoLead.first_seen_at.asc())
    )
    return list(rows.scalars().all())


# ── survey + meeting ───────────────────────────────────────────────────────────

async def submit_survey(
    db: AsyncSession,
    session: DemoSession,
    *,
    rating: int | None,
    experience: dict | None,
    product_answers: dict | None,
    notes: str | None,
    wants_to_talk: bool | None,
    talk_reason: str | None,
) -> DemoSurvey:
    survey = DemoSurvey(
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        rating=rating,
        experience=experience,
        product_answers=product_answers,
        notes=(notes or "").strip() or None,
        wants_to_talk=wants_to_talk,
        talk_reason=(talk_reason or "").strip() or None,
    )
    db.add(survey)
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type="survey_submitted",
        payload={"rating": rating, "wants_to_talk": wants_to_talk},
    )
    await db.commit()
    await db.refresh(survey)
    return survey


async def request_meeting(
    db: AsyncSession,
    session: DemoSession,
    *,
    preferred_time: datetime | None,
    timezone_name: str | None,
) -> DemoMeetingRequest:
    meeting = DemoMeetingRequest(
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        preferred_time=preferred_time,
        timezone=(timezone_name or "").strip() or None,
        status="pending",
    )
    db.add(meeting)
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type="meeting_requested",
        payload={"preferred_time": preferred_time.isoformat() if preferred_time else None},
    )
    await db.commit()
    await db.refresh(meeting)
    return meeting


# ── MCP token to show the visitor ──────────────────────────────────────────────

async def get_or_create_demo_mcp_token(db: AsyncSession, session: DemoSession) -> BucketMcpToken:
    """Return a stable, read-only MCP token for the demo bucket so the visitor can
    try the MCP feature in ChatGPT/Claude. Created lazily, owned by the bucket
    owner, restricted to the safe read tools."""
    token = await db.scalar(
        select(BucketMcpToken)
        .where(BucketMcpToken.bucket_id == session.bucket_id, BucketMcpToken.is_active.is_(True))
        .order_by(BucketMcpToken.created_at.asc())
    )
    if token is not None:
        return token

    owner_id = await bucket_owner_id(db, session.demo_link)
    token = BucketMcpToken(
        bucket_id=session.bucket_id,
        user_id=owner_id,
        name="Demo MCP",
        allowed_tools=["search", "query", "list_files", "get_file", "get_layout", "get_bucket_info"],
        allowed_origins=[],
    )
    db.add(token)
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type="mcp_opened",
    )
    await db.commit()
    await db.refresh(token)
    return token


# ── /demo/me payload ───────────────────────────────────────────────────────────

async def me_payload(db: AsyncSession, session: DemoSession) -> dict:
    link = session.demo_link
    lead = session.demo_lead
    usage = await usage_counts(db, link)
    caps = {
        "team_members": link.cap_team_members,
        "threads": link.cap_threads,
        "messages": link.cap_messages,
        "files": link.cap_files,
        "file_size_mb": link.cap_file_size_mb,
        "comebacks": link.cap_comebacks,
    }
    file_count = await db.scalar(
        select(func.count()).select_from(File).where(
            File.bucket_id == link.bucket_id, File.status == "ready"
        )
    ) or 0
    return {
        "company_name": link.company_name,
        "slug": link.slug,
        "lead": {
            "id": str(lead.id),
            "name": lead.name,
            "email": lead.email,
            "role": lead.role,
            "color": lead.color,
            "is_team_member": lead.is_team_member,
            "comeback_count": lead.comeback_count,
        },
        "caps": caps,
        "usage": usage,
        "ready_files": int(file_count),
        "comebacks_remaining": max(0, link.cap_comebacks - lead.comeback_count),
    }
