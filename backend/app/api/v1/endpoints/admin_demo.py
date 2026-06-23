"""
Admin API for the public Demo Bucket layer.

Founder/admin only — gated by the same verified ``require_admin_session`` used for
the rest of the sensitive admin actions. Lets the founder create per-company demo
buckets, load the prebuild docs, watch activity (logins / messages / feedback),
and work the "let's talk" meeting queue.

Prefix: ``/admin`` (mounted under ``/v1``).
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File as FastAPIFile,
    HTTPException,
    Query,
    UploadFile,
)
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_admin_session
from app.database import get_db
from app.models.bucket import Bucket
from app.models.conversation import Conversation, Message
from app.models.demo import DemoEvent, DemoLead, DemoLink, DemoMeetingRequest, DemoSurvey
from app.models.file import File
from app.models.user import User
from app.services.pipeline.upload import intake_upload

router = APIRouter(prefix="/admin", tags=["admin-demo"])

_SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,60}[a-z0-9])?$")
_CODE_RE = re.compile(r"^\d{4}$")
_CAP_FIELDS = {
    "cap_team_members",
    "cap_threads",
    "cap_messages",
    "cap_files",
    "cap_file_size_mb",
    "cap_comebacks",
}


# ── request models ─────────────────────────────────────────────────────────────

class CapsModel(BaseModel):
    cap_team_members: int = Field(default=3, ge=0, le=1000)
    cap_threads: int = Field(default=10, ge=0, le=10000)
    cap_messages: int = Field(default=100, ge=0, le=100000)
    cap_files: int = Field(default=1, ge=0, le=1000)
    cap_file_size_mb: int = Field(default=50, ge=1, le=1024)
    cap_comebacks: int = Field(default=3, ge=1, le=1000)


class CreateDemoBucketRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=2, max_length=62)
    access_code: str = Field(..., min_length=4, max_length=4)
    caps: CapsModel = Field(default_factory=CapsModel)
    expires_at: datetime | None = None


class UpdateDemoBucketRequest(BaseModel):
    company_name: str | None = Field(default=None, max_length=200)
    access_code: str | None = Field(default=None, min_length=4, max_length=4)
    is_active: bool | None = None
    expires_at: datetime | None = None
    caps: dict[str, int] | None = None


class UpdateMeetingRequest(BaseModel):
    status: str | None = Field(default=None, pattern="^(pending|scheduled|done|declined)$")
    zoom_link: str | None = Field(default=None, max_length=2000)
    admin_notes: str | None = Field(default=None, max_length=4000)
    scheduled_at: datetime | None = None


# ── helpers ────────────────────────────────────────────────────────────────────

def _validate_slug(slug: str) -> str:
    slug = (slug or "").strip().lower()
    if not _SLUG_RE.match(slug):
        raise HTTPException(
            status_code=400,
            detail="Slug must be 2–62 chars: lowercase letters, numbers, hyphens (not at the ends).",
        )
    return slug


def _validate_code(code: str) -> str:
    code = (code or "").strip()
    if not _CODE_RE.match(code):
        raise HTTPException(status_code=400, detail="Access code must be exactly 4 digits.")
    return code


async def _file_rollup(db: AsyncSession, bucket_id: uuid.UUID) -> dict:
    rows = (
        await db.execute(
            select(File.status, func.count()).where(File.bucket_id == bucket_id).group_by(File.status)
        )
    ).all()
    by_status = {status: int(count) for status, count in rows}
    total = sum(by_status.values())
    ready = by_status.get("ready", 0)
    processing = by_status.get("processing", 0) + by_status.get("uploading", 0)
    failed = by_status.get("failed", 0)
    if total == 0:
        state = "empty"
    elif processing > 0:
        state = "processing"
    elif ready == total:
        state = "ready"
    else:
        state = "partial"
    return {"total": total, "ready": ready, "processing": processing, "failed": failed, "state": state}


async def _link_summary(db: AsyncSession, link: DemoLink) -> dict:
    files = await _file_rollup(db, link.bucket_id)
    leads = int(
        await db.scalar(select(func.count()).select_from(DemoLead).where(DemoLead.demo_link_id == link.id)) or 0
    )
    messages = int(
        await db.scalar(
            select(func.count())
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(DemoLead, Conversation.demo_lead_id == DemoLead.id)
            .where(DemoLead.demo_link_id == link.id, Message.role == "user")
        )
        or 0
    )
    feedback = int(
        await db.scalar(select(func.count()).select_from(DemoSurvey).where(DemoSurvey.demo_link_id == link.id)) or 0
    )
    pending_calls = int(
        await db.scalar(
            select(func.count())
            .select_from(DemoMeetingRequest)
            .where(DemoMeetingRequest.demo_link_id == link.id, DemoMeetingRequest.status == "pending")
        )
        or 0
    )
    return {
        "id": str(link.id),
        "bucket_id": str(link.bucket_id),
        "company_name": link.company_name,
        "slug": link.slug,
        "access_code": link.access_code,
        "is_active": link.is_active,
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "created_at": link.created_at.isoformat() if link.created_at else None,
        "caps": {f: getattr(link, f) for f in _CAP_FIELDS},
        "files": files,
        "counts": {
            "leads": leads,
            "messages": messages,
            "feedback": feedback,
            "pending_calls": pending_calls,
        },
    }


async def _get_link(db: AsyncSession, link_id: str) -> DemoLink:
    try:
        lid = uuid.UUID(link_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid demo bucket id.")
    link = await db.get(DemoLink, lid)
    if link is None:
        raise HTTPException(status_code=404, detail="Demo bucket not found.")
    return link


# ── create / list / detail / edit ──────────────────────────────────────────────

@router.post("/demo-buckets")
async def create_demo_bucket(
    body: CreateDemoBucketRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    slug = _validate_slug(body.slug)
    code = _validate_code(body.access_code)

    existing = await db.scalar(select(DemoLink).where(DemoLink.slug == slug))
    if existing is not None:
        raise HTTPException(status_code=409, detail="That slug is already taken. Pick another.")

    bucket = Bucket(
        user_id=admin.id,
        name=f"{body.company_name.strip()} — Demo",
        description=f"Public demo bucket for {body.company_name.strip()}.",
        is_demo=True,
        icon="sparkles",
        color="#6366F1",
    )
    db.add(bucket)
    await db.flush()

    # The owner (primary lead) is created by the FIRST visitor who enters the
    # code and fills name/email/role — not here. See enter_demo().
    link = DemoLink(
        bucket_id=bucket.id,
        company_name=body.company_name.strip(),
        slug=slug,
        access_code=code,
        created_by=admin.id,
        expires_at=body.expires_at,
        **body.caps.model_dump(),
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return await _link_summary(db, link)


@router.get("/demo-buckets")
async def list_demo_buckets(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    rows = (
        await db.execute(select(DemoLink).order_by(desc(DemoLink.created_at)).limit(200))
    ).scalars().all()
    return {"items": [await _link_summary(db, link) for link in rows]}


@router.get("/demo-buckets/{link_id}")
async def get_demo_bucket(
    link_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    link = await _get_link(db, link_id)
    summary = await _link_summary(db, link)

    file_rows = (
        await db.execute(
            select(File).where(File.bucket_id == link.bucket_id).order_by(File.created_at.asc())
        )
    ).scalars().all()
    lead_rows = (
        await db.execute(
            select(DemoLead).where(DemoLead.demo_link_id == link.id).order_by(DemoLead.first_seen_at.asc())
        )
    ).scalars().all()

    summary["file_list"] = [
        {
            "id": str(f.id),
            "name": f.name,
            "type": f.type,
            "status": f.status,
            "page_count": f.page_count,
            "image_count": f.image_count,
            "size": f.size,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in file_rows
    ]
    summary["leads"] = [
        {
            "id": str(l.id),
            "name": l.name,
            "email": l.email,
            "role": l.role,
            "is_team_member": l.is_team_member,
            "comeback_count": l.comeback_count,
            "color": l.color,
            "first_seen_at": l.first_seen_at.isoformat() if l.first_seen_at else None,
            "last_seen_at": l.last_seen_at.isoformat() if l.last_seen_at else None,
        }
        for l in lead_rows
    ]
    return summary


@router.patch("/demo-buckets/{link_id}")
async def update_demo_bucket(
    link_id: str,
    body: UpdateDemoBucketRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    link = await _get_link(db, link_id)
    if body.company_name is not None:
        link.company_name = body.company_name.strip() or link.company_name
    if body.access_code is not None:
        link.access_code = _validate_code(body.access_code)
    if body.is_active is not None:
        link.is_active = body.is_active
    if body.expires_at is not None:
        link.expires_at = body.expires_at
    if body.caps:
        for key, value in body.caps.items():
            if key not in _CAP_FIELDS:
                raise HTTPException(status_code=400, detail=f"Unknown cap field: {key}.")
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise HTTPException(status_code=400, detail=f"'{key}' must be a non-negative integer.")
            setattr(link, key, value)

    await db.commit()
    await db.refresh(link)
    return await _link_summary(db, link)


# ── prebuild files ─────────────────────────────────────────────────────────────

@router.post("/demo-buckets/{link_id}/files")
async def upload_demo_files(
    link_id: str,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    """Load the prebuild docs the visitor will explore. Reuses the normal pipeline.
    Not subject to the founder's plan quota (the bucket is ``is_demo``)."""
    from app.services.processing_v3.orchestrator import process_file

    link = await _get_link(db, link_id)
    out = []
    for upload in files:
        file_row, trace_run_id = await intake_upload(
            db=db, bucket_id=link.bucket_id, user_id=admin.id, upload=upload
        )
        background_tasks.add_task(process_file, str(file_row.id), trace_run_id, "upload")
        out.append({"id": str(file_row.id), "name": file_row.name, "status": file_row.status})
    return {"files": out}


# ── activity ───────────────────────────────────────────────────────────────────

@router.get("/demo-buckets/{link_id}/activity")
async def demo_bucket_activity(
    link_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    link = await _get_link(db, link_id)

    leads = (
        await db.execute(
            select(DemoLead).where(DemoLead.demo_link_id == link.id).order_by(DemoLead.first_seen_at.asc())
        )
    ).scalars().all()
    events = (
        await db.execute(
            select(DemoEvent).where(DemoEvent.demo_link_id == link.id).order_by(desc(DemoEvent.created_at)).limit(500)
        )
    ).scalars().all()
    surveys = (
        await db.execute(
            select(DemoSurvey).where(DemoSurvey.demo_link_id == link.id).order_by(desc(DemoSurvey.created_at))
        )
    ).scalars().all()
    meetings = (
        await db.execute(
            select(DemoMeetingRequest)
            .where(DemoMeetingRequest.demo_link_id == link.id)
            .order_by(desc(DemoMeetingRequest.created_at))
        )
    ).scalars().all()

    # message counts per lead
    msg_rows = (
        await db.execute(
            select(Conversation.demo_lead_id, func.count())
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Conversation.demo_lead_id.in_([l.id for l in leads]) if leads else False, Message.role == "user")
            .group_by(Conversation.demo_lead_id)
        )
    ).all()
    msgs_by_lead = {lead_id: int(c) for lead_id, c in msg_rows}

    events_by_lead: dict[uuid.UUID, list] = {}
    for ev in events:
        events_by_lead.setdefault(ev.demo_lead_id, []).append(
            {
                "type": ev.event_type,
                "payload": ev.payload,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
            }
        )

    surveys_by_lead: dict[uuid.UUID, list] = {}
    for s in surveys:
        surveys_by_lead.setdefault(s.demo_lead_id, []).append(
            {
                "rating": s.rating,
                "experience": s.experience,
                "product_answers": s.product_answers,
                "notes": s.notes,
                "wants_to_talk": s.wants_to_talk,
                "talk_reason": s.talk_reason,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
        )

    lead_by_id = {l.id: l for l in leads}
    meetings_out = [
        {
            "id": str(m.id),
            "lead_name": lead_by_id[m.demo_lead_id].name if m.demo_lead_id in lead_by_id else None,
            "lead_email": lead_by_id[m.demo_lead_id].email if m.demo_lead_id in lead_by_id else None,
            "preferred_time": m.preferred_time.isoformat() if m.preferred_time else None,
            "timezone": m.timezone,
            "status": m.status,
            "zoom_link": m.zoom_link,
            "admin_notes": m.admin_notes,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "scheduled_at": m.scheduled_at.isoformat() if m.scheduled_at else None,
        }
        for m in meetings
    ]

    leads_out = [
        {
            "id": str(l.id),
            "name": l.name,
            "email": l.email,
            "role": l.role,
            "is_team_member": l.is_team_member,
            "comeback_count": l.comeback_count,
            "color": l.color,
            "first_seen_at": l.first_seen_at.isoformat() if l.first_seen_at else None,
            "last_seen_at": l.last_seen_at.isoformat() if l.last_seen_at else None,
            "message_count": msgs_by_lead.get(l.id, 0),
            "events": events_by_lead.get(l.id, []),
            "surveys": surveys_by_lead.get(l.id, []),
        }
        for l in leads
    ]
    return {"company_name": link.company_name, "leads": leads_out, "meetings": meetings_out}


# ── meeting queue ──────────────────────────────────────────────────────────────

@router.get("/demo-meetings")
async def list_demo_meetings(
    status: str = Query(default="pending", pattern="^(pending|scheduled|done|declined|all)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    stmt = (
        select(DemoMeetingRequest, DemoLead, DemoLink)
        .join(DemoLead, DemoMeetingRequest.demo_lead_id == DemoLead.id)
        .join(DemoLink, DemoMeetingRequest.demo_link_id == DemoLink.id)
        .order_by(desc(DemoMeetingRequest.created_at))
        .limit(200)
    )
    if status != "all":
        stmt = stmt.where(DemoMeetingRequest.status == status)
    rows = (await db.execute(stmt)).all()
    return {
        "items": [
            {
                "id": str(m.id),
                "company_name": link.company_name,
                "slug": link.slug,
                "lead_name": lead.name,
                "lead_email": lead.email,
                "lead_role": lead.role,
                "preferred_time": m.preferred_time.isoformat() if m.preferred_time else None,
                "timezone": m.timezone,
                "status": m.status,
                "zoom_link": m.zoom_link,
                "admin_notes": m.admin_notes,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "scheduled_at": m.scheduled_at.isoformat() if m.scheduled_at else None,
            }
            for m, lead, link in rows
        ]
    }


@router.patch("/demo-meetings/{meeting_id}")
async def update_demo_meeting(
    meeting_id: str,
    body: UpdateMeetingRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    try:
        mid = uuid.UUID(meeting_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid meeting id.")
    meeting = await db.get(DemoMeetingRequest, mid)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting request not found.")

    if body.status is not None:
        meeting.status = body.status
        if body.status == "scheduled" and meeting.scheduled_at is None and body.scheduled_at is None:
            meeting.scheduled_at = datetime.now(timezone.utc)
    if body.zoom_link is not None:
        meeting.zoom_link = body.zoom_link.strip() or None
    if body.admin_notes is not None:
        meeting.admin_notes = body.admin_notes.strip() or None
    if body.scheduled_at is not None:
        meeting.scheduled_at = body.scheduled_at
    await db.commit()
    await db.refresh(meeting)
    return {
        "id": str(meeting.id),
        "status": meeting.status,
        "zoom_link": meeting.zoom_link,
        "admin_notes": meeting.admin_notes,
        "scheduled_at": meeting.scheduled_at.isoformat() if meeting.scheduled_at else None,
    }
