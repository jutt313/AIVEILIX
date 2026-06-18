"""
Admin-only provisioning endpoints (Enterprise / custom limits).

Security:
  1. Caller must be an authenticated admin user (users.is_admin or ADMIN_EMAILS).
  2. Caller must prove the env admin key before a one-time email code is sent.
  3. Sensitive actions require the short-lived admin session from that code.
Every change is written to admin_audit_log. All queries use SQLAlchemy ORM
parameter binding; no raw SQL is built from input.
"""

import asyncio
import hmac
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import require_admin, require_admin_session
from app.config import settings
from app.database import get_db
from app.models.bucket import Bucket
from app.models.file import File
from app.models.platform import AdminAuditLog, EnterpriseInquiry, LimitIncreaseRequest, Subscription
from app.models.user import Profile, User
from app.services.email import send_admin_login_code
from app.services.notifications import create_notification
from app.services.plans import PLAN_LIMITS, _OVERRIDABLE, normalize_plan_key, resolve_effective_plan
from app.valkey import get_valkey

router = APIRouter(prefix="/admin", tags=["admin"])

_ALLOWED_PLANS = {"individual", "team", "business"}
_ALLOWED_SUBSCRIPTION_STATUSES = {"active", "cancelled", "past_due"}
_CODE_TTL_SECONDS = 60
_SESSION_TTL_SECONDS = 1800
_MAX_CODE_SENDS = 3
_CODE_SEND_WINDOW_SECONDS = 600
_MAX_ADMIN_KEY_FAILURES = 5
_ADMIN_KEY_FAILURE_WINDOW_SECONDS = 3600
_MAX_CODE_FAILURES = 5


class LookupRequest(BaseModel):
    email: EmailStr


class SetPlanRequest(BaseModel):
    email: EmailStr
    plan: str = Field(..., description="individual | team | business")
    status: str = Field(default="active", description="active | cancelled | past_due")
    limits_override: dict[str, int] | None = None


class ApplyLimitRequest(BaseModel):
    plan: str = Field(default="business", description="individual | team | business")
    limits_override: dict[str, int]
    admin_note: str | None = Field(default=None, max_length=1000)


class RejectLimitRequest(BaseModel):
    admin_note: str | None = Field(default=None, max_length=1000)


class RequestCodeRequest(BaseModel):
    email: EmailStr
    admin_key: str


class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


def _norm_email(email: str | EmailStr) -> str:
    return str(email or "").strip().lower()


async def _bump_limited(key: str, *, limit: int, ttl: int, detail: str) -> int:
    v = get_valkey()
    count = await v.incr(key)
    if count == 1:
        await v.expire(key, ttl)
    if count > limit:
        raise HTTPException(status_code=429, detail=detail)
    return int(count)


def _mask_email(email: str) -> str:
    name, _, domain = (email or "").partition("@")
    head = name[:2] if len(name) > 2 else name[:1]
    return f"{head}{'*' * max(2, len(name) - len(head))}@{domain}" if domain else email


def _limits_payload(limits) -> dict[str, int]:
    return {
        "max_users": limits.max_users,
        "max_buckets": limits.max_buckets,
        "max_documents": limits.max_documents,
        "max_pages": limits.max_pages,
        "max_storage_bytes": limits.max_storage_bytes,
        "max_chat_messages": limits.max_chat_messages,
        "mcp_rate_per_min": limits.mcp_rate_per_min,
        "max_images": limits.max_images,
        "max_file_size_bytes": limits.max_file_size_bytes,
    }


async def _account_snapshot(db: AsyncSession, user: User) -> dict:
    sub = (await db.execute(select(Subscription).where(Subscription.user_id == user.id))).scalar_one_or_none()
    ep = resolve_effective_plan(sub)
    prof = (await db.execute(select(Profile).where(Profile.user_id == user.id))).scalar_one_or_none()

    docs = await db.scalar(select(func.count()).select_from(File).where(File.user_id == user.id)) or 0
    images = await db.scalar(select(func.coalesce(func.sum(File.image_count), 0)).where(File.user_id == user.id)) or 0
    pages = await db.scalar(select(func.coalesce(func.sum(File.page_count), 0)).where(File.user_id == user.id)) or 0
    storage = await db.scalar(select(func.coalesce(func.sum(File.size), 0)).where(File.user_id == user.id)) or 0
    buckets = await db.scalar(select(func.count()).select_from(Bucket).where(Bucket.user_id == user.id)) or 0

    return {
        "user_id": str(user.id),
        "email": user.email,
        "name": prof.full_name if prof else None,
        "is_admin": user.is_admin,
        "plan": normalize_plan_key(sub.plan) if sub else None,
        "subscription_status": sub.status if sub else None,
        "effective_plan": ep.plan,
        "is_trial": ep.is_trial,
        "trial_ends_at": ep.trial_ends_at.isoformat() if ep.trial_ends_at else None,
        "locked": ep.locked,
        "limits_override": (sub.limits_override if sub else None) or {},
        "effective_limits": _limits_payload(ep.limits),
        "base_plan_limits": {key: _limits_payload(limits) for key, limits in PLAN_LIMITS.items()},
        "usage": {
            "documents": int(docs),
            "images": int(images),
            "pages": int(pages),
            "storage_bytes": int(storage),
            "buckets": int(buckets),
        },
        "overridable_fields": sorted(_OVERRIDABLE),
    }


def _clean_limits_override(raw: dict[str, int] | None) -> dict[str, int]:
    clean: dict[str, int] = {}
    for key, value in (raw or {}).items():
        if key not in _OVERRIDABLE:
            raise HTTPException(status_code=400, detail=f"Unknown limit field: '{key}'.")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise HTTPException(status_code=400, detail=f"'{key}' must be a non-negative integer.")
        clean[key] = value
    return clean


async def _user_summary(db: AsyncSession, user_id) -> dict | None:
    if not user_id:
        return None
    user = await db.get(User, user_id)
    if not user:
        return None
    full_name = (
        await db.execute(select(Profile.full_name).where(Profile.user_id == user.id))
    ).scalar_one_or_none()
    return {
        "user_id": str(user.id),
        "email": user.email,
        "name": full_name,
    }


async def _serialize_limit_request(db: AsyncSession, req: LimitIncreaseRequest) -> dict:
    return {
        "id": str(req.id),
        "status": req.status,
        "current_plan": req.current_plan,
        "requested_limits": req.requested_limits or {},
        "current_usage": req.current_usage or {},
        "trigger_message": req.trigger_message,
        "user_note": req.user_note,
        "admin_note": req.admin_note,
        "applied_limits": req.applied_limits or {},
        "requester_email": req.requester_email,
        "owner": await _user_summary(db, req.owner_user_id),
        "requester": await _user_summary(db, req.requester_user_id),
        "admin": await _user_summary(db, req.admin_user_id),
        "created_at": req.created_at.isoformat() if req.created_at else None,
        "updated_at": req.updated_at.isoformat() if req.updated_at else None,
        "resolved_at": req.resolved_at.isoformat() if req.resolved_at else None,
    }


async def _serialize_enterprise_inquiry(db: AsyncSession, inquiry: EnterpriseInquiry) -> dict:
    user = await _user_summary(db, inquiry.user_id)
    return {
        "id": str(inquiry.id),
        "status": inquiry.status,
        "requester": user,
        "requester_email": user["email"] if user else None,
        "company": inquiry.company,
        "role": inquiry.role,
        "team_size": inquiry.team_size,
        "doc_volume": inquiry.doc_volume,
        "use_case": inquiry.use_case,
        "meeting_url": inquiry.meeting_url,
        "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None,
    }


async def _apply_plan_to_user(
    *,
    db: AsyncSession,
    admin: User,
    user: User,
    plan: str,
    status: str = "active",
    limits_override: dict[str, int],
    audit_action: str,
    request_id: str | None = None,
) -> dict:
    plan = normalize_plan_key(plan)
    if plan not in _ALLOWED_PLANS:
        raise HTTPException(status_code=400, detail=f"plan must be one of {sorted(_ALLOWED_PLANS)}.")
    if status not in _ALLOWED_SUBSCRIPTION_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(_ALLOWED_SUBSCRIPTION_STATUSES)}.")

    sub = (await db.execute(select(Subscription).where(Subscription.user_id == user.id))).scalar_one_or_none()
    if sub is None:
        sub = Subscription(user_id=user.id, plan=plan, status=status)
        db.add(sub)
    applied_override = limits_override if plan == "business" else {}

    sub.plan = plan
    sub.status = status
    sub.limits_override = applied_override or None
    # Manual admin status changes take effect immediately. Cancelled/past_due
    # accounts resolve to locked because resolve_effective_plan requires active.
    sub.current_period_end = None

    details = {"plan": plan, "status": status, "limits_override": applied_override}
    if request_id:
        details["limit_request_id"] = request_id
    db.add(AdminAuditLog(
        admin_user_id=admin.id,
        action=audit_action,
        target_user_id=user.id,
        target_email=user.email,
        details=details,
    ))

    fresh = await db.get(User, user.id)
    return await _account_snapshot(db, fresh)


@router.post("/request-code")
async def admin_request_code(
    body: RequestCodeRequest,
    admin: User = Depends(require_admin),
):
    """Step 1: verify the admin email + key, then email a 60-second 6-digit code."""
    admin_email = _norm_email(admin.email)
    if _norm_email(body.email) != admin_email:
        raise HTTPException(status_code=403, detail="Email does not match your account.")
    expected = settings.admin_api_key or ""
    if not expected or not hmac.compare_digest((body.admin_key or "").strip(), expected):
        await _bump_limited(
            f"admin:key_fail:{admin.id}",
            limit=_MAX_ADMIN_KEY_FAILURES,
            ttl=_ADMIN_KEY_FAILURE_WINDOW_SECONDS,
            detail="Too many invalid admin key attempts. Try again later.",
        )
        raise HTTPException(status_code=403, detail="Invalid admin key.")

    v = get_valkey()
    await v.delete(f"admin:key_fail:{admin.id}")
    await _bump_limited(
        f"admin:code_send:{admin.id}",
        limit=_MAX_CODE_SENDS,
        ttl=_CODE_SEND_WINDOW_SECONDS,
        detail="Too many admin codes requested. Try again in a few minutes.",
    )

    code = f"{secrets.randbelow(1_000_000):06d}"
    await v.setex(f"admin:code:{admin.id}", _CODE_TTL_SECONDS, code)
    await v.delete(f"admin:code_fail:{admin.id}")
    try:
        await asyncio.to_thread(send_admin_login_code, admin.email, code)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not send the code: {exc}")
    return {"sent": True, "channel": "email", "sent_to": _mask_email(admin.email), "expires_in": _CODE_TTL_SECONDS}


@router.post("/verify-code")
async def admin_verify_code(
    body: VerifyCodeRequest,
    admin: User = Depends(require_admin),
):
    """Step 2: verify the 6-digit code (60s window), issue a short-lived admin session."""
    v = get_valkey()
    key = f"admin:code:{admin.id}"
    stored = await v.get(key)
    if not stored:
        raise HTTPException(status_code=400, detail="Code expired. Request a new one.")
    if not hmac.compare_digest(stored, (body.code or "").strip()):
        attempts = await _bump_limited(
            f"admin:code_fail:{admin.id}",
            limit=_MAX_CODE_FAILURES,
            ttl=_CODE_TTL_SECONDS,
            detail="Too many invalid codes. Request a new one.",
        )
        if attempts >= _MAX_CODE_FAILURES:
            await v.delete(key)
            await v.delete(f"admin:code_fail:{admin.id}")
            raise HTTPException(status_code=429, detail="Too many invalid codes. Request a new one.")
        raise HTTPException(status_code=400, detail="Invalid code.")
    await v.delete(key)
    await v.delete(f"admin:code_fail:{admin.id}")
    session = secrets.token_urlsafe(32)
    await v.setex(f"admin:session:{session}", _SESSION_TTL_SECONDS, str(admin.id))
    return {"admin_session": session, "expires_in": _SESSION_TTL_SECONDS}


@router.post("/lookup")
async def admin_lookup(
    body: LookupRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    email = _norm_email(body.email)
    user = (await db.execute(select(User).where(func.lower(User.email) == email))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f"No account found for {email}.")
    return await _account_snapshot(db, user)


@router.post("/set-plan")
async def admin_set_plan(
    body: SetPlanRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    email = _norm_email(body.email)
    user = (await db.execute(select(User).where(func.lower(User.email) == email))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f"No account found for {email}.")

    snapshot = await _apply_plan_to_user(
        db=db,
        admin=admin,
        user=user,
        plan=body.plan,
        status=body.status,
        limits_override=_clean_limits_override(body.limits_override),
        audit_action="set_plan",
    )
    await db.commit()
    return snapshot


@router.get("/limit-requests")
async def admin_list_limit_requests(
    status: str = Query(default="pending", pattern="^(pending|approved|rejected|all)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    stmt = select(LimitIncreaseRequest).order_by(desc(LimitIncreaseRequest.created_at))
    if status != "all":
        stmt = stmt.where(LimitIncreaseRequest.status == status)
    rows = (await db.execute(stmt.limit(100))).scalars().all()
    return {"items": [await _serialize_limit_request(db, row) for row in rows]}


@router.get("/enterprise-inquiries")
async def admin_list_enterprise_inquiries(
    status: str = Query(default="new", pattern="^(new|all)$"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    stmt = select(EnterpriseInquiry).order_by(desc(EnterpriseInquiry.created_at))
    if status != "all":
        stmt = stmt.where(EnterpriseInquiry.status == status)
    rows = (await db.execute(stmt.limit(100))).scalars().all()
    return {"items": [await _serialize_enterprise_inquiry(db, row) for row in rows]}


@router.post("/limit-requests/{request_id}/apply")
async def admin_apply_limit_request(
    request_id: str,
    body: ApplyLimitRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    try:
        rid = uuid.UUID(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid request id.") from exc
    req = await db.get(LimitIncreaseRequest, rid)
    if req is None:
        raise HTTPException(status_code=404, detail="Limit request not found.")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been resolved.")

    user = await db.get(User, req.owner_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Request owner account not found.")

    clean_override = _clean_limits_override(body.limits_override)
    applied_override = clean_override if body.plan == "business" else {}
    snapshot = await _apply_plan_to_user(
        db=db,
        admin=admin,
        user=user,
        plan=body.plan,
        status="active",
        limits_override=applied_override,
        audit_action="apply_limit_request",
        request_id=str(req.id),
    )
    req.status = "approved"
    req.admin_user_id = admin.id
    req.admin_note = body.admin_note
    req.applied_limits = applied_override
    req.resolved_at = datetime.now(timezone.utc)

    notify_user_id = req.requester_user_id or req.owner_user_id
    await create_notification(
        db,
        str(notify_user_id),
        "success",
        "Limit increase approved",
        body.admin_note or "Your requested limit increase was approved and applied.",
    )
    if req.requester_user_id and req.requester_user_id != req.owner_user_id:
        await create_notification(
            db,
            str(req.owner_user_id),
            "success",
            "Workspace limits updated",
            body.admin_note or "An admin approved a limit increase for your workspace.",
        )

    db.add(AdminAuditLog(
        admin_user_id=admin.id,
        action="resolve_limit_request",
        target_user_id=req.owner_user_id,
        target_email=user.email,
        details={"limit_request_id": str(req.id), "status": "approved", "admin_note": body.admin_note},
    ))
    await db.commit()
    await db.refresh(req)
    return {
        "request": await _serialize_limit_request(db, req),
        "account": snapshot,
    }


@router.post("/limit-requests/{request_id}/reject")
async def admin_reject_limit_request(
    request_id: str,
    body: RejectLimitRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_session),
):
    try:
        rid = uuid.UUID(request_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid request id.") from exc
    req = await db.get(LimitIncreaseRequest, rid)
    if req is None:
        raise HTTPException(status_code=404, detail="Limit request not found.")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been resolved.")

    req.status = "rejected"
    req.admin_user_id = admin.id
    req.admin_note = body.admin_note
    req.resolved_at = datetime.now(timezone.utc)

    notify_user_id = req.requester_user_id or req.owner_user_id
    await create_notification(
        db,
        str(notify_user_id),
        "info",
        "Limit increase reviewed",
        body.admin_note or "Your requested limit increase was reviewed. No changes were applied.",
    )
    db.add(AdminAuditLog(
        admin_user_id=admin.id,
        action="resolve_limit_request",
        target_user_id=req.owner_user_id,
        target_email=req.requester_email,
        details={"limit_request_id": str(req.id), "status": "rejected", "admin_note": body.admin_note},
    ))
    await db.commit()
    await db.refresh(req)
    return {"request": await _serialize_limit_request(db, req)}
