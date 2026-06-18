import logging
import uuid
from datetime import date, datetime, timezone

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.bucket import Bucket
from app.models.conversation import Conversation, Message
from app.models.file import File
from app.models.platform import LimitIncreaseRequest, Subscription, TeamMember, UsageTracking
from app.models.user import Profile, User
from app.services import stripe_billing
from app.services.notifications import create_notification
from app.services.plans import _OVERRIDABLE, resolve_effective_plan
from app.services.team.permissions import parse_active_workspace, resolve_user_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: str


class LimitIncreaseRequestBody(BaseModel):
    requested_limits: dict[str, int] = Field(default_factory=dict)
    note: str | None = Field(default=None, max_length=1000)
    trigger_message: str | None = Field(default=None, max_length=1000)


def _usage_month() -> date:
    return date.today().replace(day=1)


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _limit_payload(ep) -> dict[str, int]:
    return {
        "max_users": ep.limits.max_users,
        "max_buckets": ep.limits.max_buckets,
        "max_documents": ep.limits.max_documents,
        "max_pages": ep.limits.max_pages,
        "max_storage_bytes": ep.limits.max_storage_bytes,
        "max_chat_messages": ep.limits.max_chat_messages,
        "mcp_rate_per_min": ep.limits.mcp_rate_per_min,
        "max_images": ep.limits.max_images,
        "max_file_size_bytes": ep.limits.max_file_size_bytes,
    }


def _clean_requested_limits(raw: dict[str, int]) -> dict[str, int]:
    clean: dict[str, int] = {}
    for key, value in (raw or {}).items():
        if key not in _OVERRIDABLE:
            raise HTTPException(status_code=400, detail=f"Unknown limit field: '{key}'.")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise HTTPException(status_code=400, detail=f"'{key}' must be a non-negative integer.")
        clean[key] = value
    if not clean:
        raise HTTPException(status_code=400, detail="Choose at least one limit to request.")
    return clean


async def _usage_snapshot(db: AsyncSession, owner_user_id: uuid.UUID) -> dict[str, int]:
    docs = await db.scalar(select(func.count()).select_from(File).where(File.user_id == owner_user_id)) or 0
    images = await db.scalar(select(func.coalesce(func.sum(File.image_count), 0)).where(File.user_id == owner_user_id)) or 0
    pages = await db.scalar(select(func.coalesce(func.sum(File.page_count), 0)).where(File.user_id == owner_user_id)) or 0
    storage = await db.scalar(select(func.coalesce(func.sum(File.size), 0)).where(File.user_id == owner_user_id)) or 0
    buckets = await db.scalar(select(func.count()).select_from(Bucket).where(Bucket.user_id == owner_user_id)) or 0
    members = await db.scalar(
        select(func.count())
        .select_from(TeamMember)
        .where(TeamMember.owner_user_id == owner_user_id, TeamMember.status != "rejected")
    ) or 0
    chats = await db.scalar(
        select(func.count())
        .select_from(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .join(Bucket, Conversation.bucket_id == Bucket.id)
        .where(
            Bucket.user_id == owner_user_id,
            Message.role == "user",
            Message.created_at >= _month_start(),
        )
    ) or 0
    usage = (
        await db.execute(
            select(UsageTracking).where(
                UsageTracking.user_id == owner_user_id,
                UsageTracking.month == _usage_month(),
            )
        )
    ).scalar_one_or_none()

    return {
        "max_users": int(members) + 1,
        "max_buckets": int(buckets),
        "max_documents": int(docs),
        "max_pages": int(pages),
        "max_storage_bytes": int(storage),
        "max_chat_messages": int(chats),
        "mcp_rate_per_min": int(usage.mcp_calls_count if usage else 0),
        "max_images": int(images),
    }


def _percent_used(usage: dict[str, int], limits: dict[str, int]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, limit in limits.items():
        used = usage.get(key, 0)
        out[key] = round((used / limit) * 100, 1) if limit else 0
    return out


async def _plan_payload(db: AsyncSession, owner_user_id: uuid.UUID) -> dict:
    sub = (
        await db.execute(select(Subscription).where(Subscription.user_id == owner_user_id))
    ).scalar_one_or_none()
    ep = resolve_effective_plan(sub)
    limits = _limit_payload(ep)
    usage = await _usage_snapshot(db, owner_user_id)
    return {
        "plan": ep.plan,
        "name": ep.limits.name,
        "status": "locked" if ep.locked else "active",
        "locked": ep.locked,
        "is_trial": ep.is_trial,
        "trial_ends_at": ep.trial_ends_at.isoformat() if ep.trial_ends_at else None,
        "limits": limits,
        "usage": usage,
        "percent_used": _percent_used(usage, limits),
        "overridable_fields": sorted(_OVERRIDABLE),
    }


async def _admin_users(db: AsyncSession) -> list[User]:
    emails = {e.strip().lower() for e in (settings.admin_emails or "").split(",") if e.strip()}
    conditions = [User.is_admin.is_(True)]
    if emails:
        conditions.append(func.lower(User.email).in_(emails))
    result = await db.execute(select(User).where(or_(*conditions)))
    return list(result.scalars().all())


async def _user_label(db: AsyncSession, user_id: uuid.UUID) -> str:
    user = await db.get(User, user_id)
    if not user:
        return str(user_id)
    full_name = (
        await db.execute(select(Profile.full_name).where(Profile.user_id == user.id))
    ).scalar_one_or_none()
    return full_name or user.email


@router.get("/plan")
async def get_plan(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    x_workspace: str | None = Header(default=None, alias="X-Workspace"),
):
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, parse_active_workspace(x_workspace, user_id))
    payload = await _plan_payload(db, ctx.owner_user_id)
    payload["user_id"] = str(ctx.user_id)
    payload["owner_user_id"] = str(ctx.owner_user_id)
    payload["is_member"] = ctx.is_member
    return payload


@router.post("/limit-increase-requests")
async def request_limit_increase(
    body: LimitIncreaseRequestBody,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    x_workspace: str | None = Header(default=None, alias="X-Workspace"),
):
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, parse_active_workspace(x_workspace, user_id))
    requested_limits = _clean_requested_limits(body.requested_limits)
    plan = await _plan_payload(db, ctx.owner_user_id)
    if plan["plan"] != "business":
        raise HTTPException(
            status_code=400,
            detail="Custom limit requests are only available on Enterprise. Upgrade your plan first.",
        )

    req = LimitIncreaseRequest(
        owner_user_id=ctx.owner_user_id,
        requester_user_id=ctx.user_id,
        requester_email=ctx.email,
        current_plan=plan["plan"],
        requested_limits=requested_limits,
        current_usage=plan["usage"],
        trigger_message=body.trigger_message,
        user_note=body.note,
    )
    db.add(req)
    await db.flush()

    requested_text = ", ".join(f"{key}={value}" for key, value in requested_limits.items())
    requester_label = await _user_label(db, ctx.user_id)
    owner_label = await _user_label(db, ctx.owner_user_id)

    await create_notification(
        db,
        str(ctx.user_id),
        "success",
        "Limit increase request sent",
        "Your request was sent to the admin team. We'll review it and update your account if approved.",
    )
    for admin in await _admin_users(db):
        await create_notification(
            db,
            str(admin.id),
            "warning",
            "Limit increase requested",
            f"{requester_label} requested higher limits for {owner_label}: {requested_text}.",
        )

    await db.commit()
    await db.refresh(req)
    return {
        "message": "Limit increase request sent.",
        "request_id": str(req.id),
        "status": req.status,
    }


@router.post("/upgrade")
async def upgrade_plan(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    x_workspace: str | None = Header(default=None, alias="X-Workspace"),
):
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, parse_active_workspace(x_workspace, user_id))
    plan = await _plan_payload(db, ctx.owner_user_id)
    requested = {
        key: max(int(plan["limits"].get(key, 0)), int(plan["usage"].get(key, 0))) * 2
        for key in ("max_documents", "max_pages", "max_storage_bytes", "max_chat_messages")
    }
    body = LimitIncreaseRequestBody(
        requested_limits=requested,
        note="General upgrade request.",
        trigger_message="Upgrade requested from billing.",
    )
    return await request_limit_increase(body, db, current_user, x_workspace)


@router.post("/checkout")
async def create_checkout(
    body: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    x_workspace: str | None = Header(default=None, alias="X-Workspace"),
):
    """Start a Stripe Checkout session for a self-serve plan; returns the URL to redirect to."""
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, parse_active_workspace(x_workspace, user_id))
    owner = await db.get(User, ctx.owner_user_id)
    email = owner.email if owner else ctx.email
    try:
        url = await stripe_billing.create_checkout_session(db, ctx.owner_user_id, email, body.plan)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"url": url}


@router.post("/portal")
async def create_portal(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    x_workspace: str | None = Header(default=None, alias="X-Workspace"),
):
    """Stripe Customer Portal — manage card, downgrade, or cancel."""
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, parse_active_workspace(x_workspace, user_id))
    try:
        url = await stripe_billing.create_portal_session(db, ctx.owner_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"url": url}


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    x_workspace: str | None = Header(default=None, alias="X-Workspace"),
):
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, parse_active_workspace(x_workspace, user_id))
    try:
        await stripe_billing.cancel_subscription(db, ctx.owner_user_id, at_period_end=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    await create_notification(
        db,
        str(current_user["user_id"]),
        "warning",
        "Subscription cancellation scheduled",
        "Your subscription will end at the close of the current billing period.",
        commit=True,
    )
    return {"message": "Your subscription will be cancelled at the end of the current period."}


@router.get("/history")
async def billing_history(current_user=Depends(get_current_user)):
    return {
        "items": [],
        "total": 0,
        "message": f'No billing history is available yet for user {current_user["user_id"]}.',
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify and process Stripe webhook events (signature-checked)."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe_billing.construct_event(payload, sig)
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload.")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    try:
        await stripe_billing.handle_event(db, event)
    except Exception:
        logger.exception("stripe webhook handler failed for %s", event["type"])
        raise HTTPException(status_code=500, detail="Webhook handler error.")
    return {"received": True}
