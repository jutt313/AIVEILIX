"""
Public Demo Bucket API.

Unauthenticated **except** for a signed demo session token (see
app.services.demo.tokens) issued on code+identity entry or invite-accept. Every
endpoint is scoped to one ``is_demo`` bucket via the token and can never reach
another bucket or any real user/billing data.

Prefix: ``/demo`` (mounted under ``/v1``).
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File as FastAPIFile,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.demo import DemoLink
from app.services.demo import service as demo_service
from app.services.demo.caps import check_cap
from app.services.demo.events import log_event
from app.services.demo.session import DemoSession, get_demo_session
from app.services.email import send_demo_meeting_admin_email, send_demo_team_invite_email
from app.services.pipeline.upload import intake_upload
from app.valkey import get_valkey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["demo"])

# ── verify-code abuse limits (4 digits = 10k combos) ──────────────────────────
_VERIFY_ATTEMPT_LIMIT = 20          # attempts per IP+slug per window
_VERIFY_WINDOW_SECONDS = 300        # 5-minute sliding window
_VERIFY_FAIL_LOCK = 10              # wrong-code lock threshold per IP+slug
_VERIFY_FAIL_WINDOW = 600           # 10-minute lock window


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _rate_limit_verify(slug: str, ip: str) -> None:
    """Bound verify/enter attempts per IP+slug and lock after repeated failures.
    Fails open if Valkey is down so an outage can't lock out real visitors."""
    try:
        v = get_valkey()
        locked = await v.get(f"demo:lock:{slug}:{ip}")
        if locked:
            raise HTTPException(status_code=429, detail="Too many attempts. Please try again later.")
        key = f"demo:try:{slug}:{ip}"
        count = await v.incr(key)
        if count == 1:
            await v.expire(key, _VERIFY_WINDOW_SECONDS)
        if count > _VERIFY_ATTEMPT_LIMIT:
            raise HTTPException(status_code=429, detail="Too many attempts. Please try again later.")
    except HTTPException:
        raise
    except Exception:
        return


async def _record_code_failure(slug: str, ip: str) -> None:
    try:
        v = get_valkey()
        key = f"demo:fail:{slug}:{ip}"
        fails = await v.incr(key)
        if fails == 1:
            await v.expire(key, _VERIFY_FAIL_WINDOW)
        if fails >= _VERIFY_FAIL_LOCK:
            await v.setex(f"demo:lock:{slug}:{ip}", _VERIFY_FAIL_WINDOW, "1")
    except Exception:
        return


async def _clear_code_failures(slug: str, ip: str) -> None:
    try:
        v = get_valkey()
        await v.delete(f"demo:fail:{slug}:{ip}")
    except Exception:
        return


# ── request/response models ───────────────────────────────────────────────────

class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=8)


class EnterRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=8)
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=3, max_length=320)
    role: str | None = Field(default=None, max_length=200)


class CreateThreadRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)


class ChatRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)
    web_search: bool | None = None


class ScopeRequest(BaseModel):
    file_ids: list[str] = Field(default_factory=list)
    scoped: bool | None = None


class TeamInviteRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=3, max_length=320)
    color: str | None = Field(default=None, max_length=16)


class SurveyRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    experience: dict | None = None
    product_answers: dict | None = None
    notes: str | None = Field(default=None, max_length=4000)
    wants_to_talk: bool | None = None
    talk_reason: str | None = Field(default=None, max_length=2000)


class MeetingRequest(BaseModel):
    preferred_time: datetime | None = None
    timezone: str | None = Field(default=None, max_length=80)


class EventRequest(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=60)
    payload: dict | None = None


# ── serializers ────────────────────────────────────────────────────────────────

def _serialize_message(msg) -> dict:
    return {
        "id": str(msg.id),
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "sources": msg.chunks_used or [],
        "agent_plan": msg.agent_plan or [],
        "agent_steps": msg.agent_steps or [],
    }


def _serialize_conversation(conv) -> dict:
    return {
        "id": str(conv.id),
        "title": conv.title,
        "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
        "created_at": conv.created_at.isoformat() if conv.created_at else None,
    }


# ── entry: verify-code / enter / invite ───────────────────────────────────────

@router.post("/{slug}/verify-code")
async def verify_code(slug: str, body: VerifyCodeRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip = _client_ip(request)
    await _rate_limit_verify(slug, ip)
    link = await demo_service.get_active_link_by_slug(db, slug)
    if demo_service.code_matches(link, body.code):
        await _clear_code_failures(slug, ip)
        return {"ok": True}
    await _record_code_failure(slug, ip)
    return {"ok": False}


@router.post("/{slug}/enter")
async def enter(slug: str, body: EnterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip = _client_ip(request)
    await _rate_limit_verify(slug, ip)
    link = await demo_service.get_active_link_by_slug(db, slug)
    if not demo_service.code_matches(link, body.code):
        await _record_code_failure(slug, ip)
        raise HTTPException(status_code=403, detail="That access code isn't right. Check the code in your invite.")
    await _clear_code_failures(slug, ip)

    lead, token = await demo_service.enter_demo(
        db, link, name=body.name, email=body.email, role=body.role
    )
    session = DemoSession(demo_link=link, demo_lead=lead)
    return {"token": token, "me": await demo_service.me_payload(db, session)}


@router.get("/invite/{invite_token}")
async def invite_info(invite_token: str, db: AsyncSession = Depends(get_db)):
    return await demo_service.get_invite_info(db, invite_token)


@router.post("/invite/{invite_token}/accept")
async def invite_accept(invite_token: str, db: AsyncSession = Depends(get_db)):
    link, lead, token = await demo_service.accept_invite(db, invite_token)
    session = DemoSession(demo_link=link, demo_lead=lead)
    return {"token": token, "me": await demo_service.me_payload(db, session)}


# ── session info ───────────────────────────────────────────────────────────────

@router.get("/me")
async def me(session: DemoSession = Depends(get_demo_session), db: AsyncSession = Depends(get_db)):
    return await demo_service.me_payload(db, session)


@router.get("/files")
async def files(session: DemoSession = Depends(get_demo_session), db: AsyncSession = Depends(get_db)):
    rows = await demo_service.list_demo_files(db, session)
    return {
        "files": [
            {
                "id": str(f.id),
                "name": f.name,
                "type": f.type,
                "status": f.status,
                "page_count": f.page_count,
                "image_count": f.image_count,
            }
            for f in rows
        ]
    }


# ── threads + chat ─────────────────────────────────────────────────────────────

@router.get("/conversations")
async def list_conversations(session: DemoSession = Depends(get_demo_session), db: AsyncSession = Depends(get_db)):
    rows = await demo_service.list_threads(db, session)
    return {"conversations": [_serialize_conversation(c) for c in rows]}


@router.post("/conversations")
async def create_conversation(
    body: CreateThreadRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    conv = await demo_service.create_thread(db, session, title=body.title)
    return _serialize_conversation(conv)


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    rows = await demo_service.list_messages(db, session, conversation_id)
    return {"messages": [_serialize_message(m) for m in rows]}


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    body: ChatRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    result = await demo_service.run_demo_turn(
        db, session, conversation_id=conversation_id, content=body.content, web_search=body.web_search
    )
    return {
        "user_message": _serialize_message(result.user_message),
        "assistant_message": _serialize_message(result.assistant_message),
        "sources": result.sources,
        "used_web_search": result.used_web_search,
    }


@router.get("/conversations/{conversation_id}/scope")
async def get_scope(
    conversation_id: str,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    return await demo_service.get_thread_scope(db, session, conversation_id)


@router.put("/conversations/{conversation_id}/scope")
async def set_scope(
    conversation_id: str,
    body: ScopeRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    return await demo_service.set_thread_scope(db, session, conversation_id, body.file_ids, body.scoped)


@router.post("/conversations/{conversation_id}/messages/stream")
async def send_message_stream(
    conversation_id: str,
    body: ChatRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    """SSE: streams thinking-step + token events, then a final ``done`` payload."""
    queue: asyncio.Queue = asyncio.Queue()
    DONE = object()

    async def on_step(event: dict) -> None:
        kind = event.get("type")
        if kind == "plan_update":
            await queue.put({"kind": "plan_update", "plan": event.get("plan") or []})
        elif kind == "token":
            await queue.put({"kind": "token", "text": event.get("text") or ""})
        else:
            await queue.put({"kind": "step", "event": event})

    async def run():
        try:
            result = await demo_service.run_demo_turn(
                db, session, conversation_id=conversation_id, content=body.content,
                web_search=body.web_search, on_step=on_step,
            )
            await queue.put({
                "kind": "done",
                "result": {
                    "user_message": _serialize_message(result.user_message),
                    "assistant_message": _serialize_message(result.assistant_message),
                    "sources": result.sources,
                    "used_web_search": result.used_web_search,
                },
            })
        except HTTPException as exc:
            await db.rollback()
            # Surface caps (409) so the client opens the pop-up.
            await queue.put({"kind": "error", "status": exc.status_code, "detail": exc.detail})
        except Exception as exc:  # noqa: BLE001
            await db.rollback()
            logger.exception("demo chat failed")
            await queue.put({"kind": "error", "status": 500, "detail": str(exc)[:300]})
        finally:
            await queue.put(DONE)

    async def event_stream():
        task = asyncio.create_task(run())
        try:
            while True:
                item = await queue.get()
                if item is DONE:
                    break
                yield f"data: {json.dumps(item)}\n\n"
        finally:
            if not task.done():
                task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


# ── visitor upload ─────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = FastAPIFile(...),
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    from app.services.processing_v3.orchestrator import process_file

    # Count cap first → 409 opens the pop-up.
    await check_cap(db, session.demo_link, "files")

    max_bytes = session.demo_link.cap_file_size_mb * 1024 * 1024
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="That file is empty.")
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"That file is larger than the {session.demo_link.cap_file_size_mb} MB demo limit.",
        )
    await file.seek(0)

    owner_id = await demo_service.bucket_owner_id(db, session.demo_link)
    file_row, trace_run_id = await intake_upload(
        db=db, bucket_id=session.bucket_id, user_id=owner_id, upload=file
    )
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type="file_uploaded",
        payload={"file_id": str(file_row.id), "name": file_row.name, "size": len(data)},
        commit=True,
    )
    background_tasks.add_task(process_file, str(file_row.id), trace_run_id, "upload")
    return {"id": str(file_row.id), "name": file_row.name, "status": file_row.status}


# ── team invite ────────────────────────────────────────────────────────────────

@router.post("/team-invite")
async def team_invite(
    body: TeamInviteRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    member = await demo_service.invite_team_member(
        db, session, name=body.name, email=body.email, color=body.color
    )
    # Best-effort email — never fail the request on a delivery hiccup.
    try:
        await asyncio.to_thread(
            send_demo_team_invite_email,
            member.email,
            member.name,
            session.demo_lead.name,
            session.demo_link.company_name,
            member.invite_token,
        )
    except Exception:
        logger.warning("demo team invite email failed for %s", member.email)
    return {
        "id": str(member.id),
        "name": member.name,
        "email": member.email,
        "color": member.color,
    }


@router.get("/team")
async def team(session: DemoSession = Depends(get_demo_session), db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timedelta, timezone
    rows = await demo_service.list_team(db, session)
    now = datetime.now(timezone.utc)
    online_cutoff = now - timedelta(minutes=15)

    def _aware(dt):
        return dt if (dt and dt.tzinfo) else (dt.replace(tzinfo=timezone.utc) if dt else None)

    return {
        "members": [
            {
                "id": str(m.id),
                "name": m.name,
                "email": m.email,
                "color": m.color,
                "role": m.role,
                "joined": m.comeback_count > 0,
                "comeback_count": m.comeback_count,
                "is_online": bool(m.last_seen_at and _aware(m.last_seen_at) >= online_cutoff),
                "first_seen_at": m.first_seen_at.isoformat() if m.first_seen_at else None,
                "last_seen_at": m.last_seen_at.isoformat() if m.last_seen_at else None,
            }
            for m in rows
        ]
    }


# ── survey + meeting ───────────────────────────────────────────────────────────

@router.post("/survey")
async def survey(
    body: SurveyRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    row = await demo_service.submit_survey(
        db,
        session,
        rating=body.rating,
        experience=body.experience,
        product_answers=body.product_answers,
        notes=body.notes,
        wants_to_talk=body.wants_to_talk,
        talk_reason=body.talk_reason,
    )
    return {"ok": True, "id": str(row.id)}


@router.post("/meeting")
async def meeting(
    body: MeetingRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    row = await demo_service.request_meeting(
        db, session, preferred_time=body.preferred_time, timezone_name=body.timezone
    )
    # Notify the founder inbox so they can create + email a Zoom link.
    try:
        recipients = [e.strip() for e in (settings.admin_emails or "").split(",") if e.strip()]
        if not recipients and settings.smtp_from_email:
            recipients = [settings.smtp_from_email.strip()]
        payload = {
            "company": session.demo_link.company_name,
            "visitor_name": session.demo_lead.name,
            "visitor_email": session.demo_lead.email,
            "visitor_role": session.demo_lead.role,
            "preferred_time": body.preferred_time.isoformat() if body.preferred_time else None,
            "timezone": body.timezone,
            "request_id": str(row.id),
        }
        for to in recipients:
            await asyncio.to_thread(send_demo_meeting_admin_email, to, payload)
    except Exception:
        logger.warning("demo meeting admin email failed")
    return {"ok": True, "id": str(row.id), "status": row.status}


# ── generic event logging ──────────────────────────────────────────────────────

@router.post("/event")
async def event(
    body: EventRequest,
    session: DemoSession = Depends(get_demo_session),
    db: AsyncSession = Depends(get_db),
):
    await log_event(
        db,
        demo_link_id=session.link_id,
        demo_lead_id=session.lead_id,
        event_type=body.event_type,
        payload=body.payload,
        commit=True,
    )
    return {"ok": True}


# ── MCP panel ──────────────────────────────────────────────────────────────────

@router.get("/mcp")
async def mcp(session: DemoSession = Depends(get_demo_session), db: AsyncSession = Depends(get_db)):
    from app.services.mcp.account_tools import bucket_mcp_url

    token = await demo_service.get_or_create_demo_mcp_token(db, session)
    return {
        "token": token.token,
        "mcp_url": bucket_mcp_url(token.token),
        "allowed_tools": token.allowed_tools,
    }
