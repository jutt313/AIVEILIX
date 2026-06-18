"""
Plan-limit enforcement for create actions.

Limits always apply to the *owner's* plan — team members share the owner's
quota. Counts are read live (cheap COUNT / SUM) so they can never drift from
reality. A blocked action raises HTTP 402 (Payment Required) with a message
the frontend can show directly.

Wired into:
  - bucket create  -> enforce_bucket_quota
  - file upload     -> enforce_upload_quota (documents + storage)
  - pipeline render -> page_quota_status (pages; non-raising, orchestrator decides)
  - in-app chat     -> enforce_chat_quota (messages this calendar month)
  - team invite     -> enforce_seat_quota (seats)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bucket import Bucket
from app.models.conversation import Conversation, Message
from app.models.file import File
from app.models.platform import Subscription, TeamMember
from app.services.plans import EffectivePlan, resolve_effective_plan


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def owner_effective_plan(db: AsyncSession, owner_user_id: uuid.UUID) -> EffectivePlan:
    """Load the owner's subscription and resolve the limits that apply right now."""
    sub = (
        await db.execute(select(Subscription).where(Subscription.user_id == owner_user_id))
    ).scalar_one_or_none()
    return resolve_effective_plan(sub)


def _deny(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)


async def enforce_bucket_quota(db: AsyncSession, owner_user_id: uuid.UUID) -> EffectivePlan:
    ep = await owner_effective_plan(db, owner_user_id)
    if ep.locked:
        _deny("Your free trial has ended. Choose a plan to keep creating buckets.")
    count = await db.scalar(
        select(func.count()).select_from(Bucket).where(Bucket.user_id == owner_user_id)
    ) or 0
    if count >= ep.limits.max_buckets:
        _deny(
            f"Your {ep.limits.name} plan includes {ep.limits.max_buckets} buckets "
            f"({count} used). Upgrade to add more."
        )
    return ep


async def enforce_upload_quota(
    db: AsyncSession,
    owner_user_id: uuid.UUID,
    *,
    incoming_files: int,
    incoming_bytes: int,
) -> EffectivePlan:
    ep = await owner_effective_plan(db, owner_user_id)
    if ep.locked:
        _deny("Your free trial has ended. Choose a plan to keep uploading.")
    lim = ep.limits

    doc_count = await db.scalar(
        select(func.count()).select_from(File).where(File.user_id == owner_user_id)
    ) or 0
    if doc_count + incoming_files > lim.max_documents:
        remaining = max(0, lim.max_documents - doc_count)
        _deny(
            f"Your {lim.name} plan includes {lim.max_documents} documents "
            f"({doc_count} used, {remaining} left). Delete some or upgrade to add {incoming_files}."
        )

    used_bytes = await db.scalar(
        select(func.coalesce(func.sum(File.size), 0)).where(File.user_id == owner_user_id)
    ) or 0
    if used_bytes + incoming_bytes > lim.max_storage_bytes:
        gb = lim.max_storage_bytes / (1024 ** 3)
        _deny(
            f"This upload would exceed your {lim.name} plan storage limit of {gb:.0f} GB. "
            "Free up space or upgrade."
        )
    return ep


async def enforce_chat_quota(db: AsyncSession, owner_user_id: uuid.UUID) -> EffectivePlan:
    ep = await owner_effective_plan(db, owner_user_id)
    if ep.locked:
        _deny("Your free trial has ended. Choose a plan to keep chatting.")
    used = await db.scalar(
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
    if used >= ep.limits.max_chat_messages:
        _deny(
            f"You've used all {ep.limits.max_chat_messages} AI chats in your "
            f"{ep.limits.name} plan this month. Upgrade for more."
        )
    return ep


async def enforce_seat_quota(db: AsyncSession, owner_user_id: uuid.UUID) -> EffectivePlan:
    ep = await owner_effective_plan(db, owner_user_id)
    if ep.locked:
        _deny("Your free trial has ended. Choose a plan to add team members.")
    members = await db.scalar(
        select(func.count())
        .select_from(TeamMember)
        .where(TeamMember.owner_user_id == owner_user_id, TeamMember.status != "rejected")
    ) or 0
    allowed_members = ep.limits.max_users - 1  # the owner occupies one seat
    if members >= allowed_members:
        _deny(
            f"Your {ep.limits.name} plan includes {ep.limits.max_users} seats. "
            "Upgrade to add more team members."
        )
    return ep


async def page_quota_status(
    db: AsyncSession,
    owner_user_id: uuid.UUID,
    *,
    adding_pages: int,
    exclude_file_id: uuid.UUID | None = None,
) -> tuple[bool, int, int, str]:
    """
    Non-raising page check for the pipeline (pages are only known after render).
    Returns (within_limit, used_pages, max_pages, plan_name).
    """
    ep = await owner_effective_plan(db, owner_user_id)
    q = select(func.coalesce(func.sum(File.page_count), 0)).where(File.user_id == owner_user_id)
    if exclude_file_id is not None:
        q = q.where(File.id != exclude_file_id)
    used = await db.scalar(q) or 0
    within = (not ep.locked) and (used + adding_pages <= ep.limits.max_pages)
    return within, int(used), ep.limits.max_pages, ep.limits.name


async def image_quota_status(
    db: AsyncSession,
    owner_user_id: uuid.UUID,
    *,
    adding_images: int,
    exclude_file_id: uuid.UUID | None = None,
) -> tuple[bool, int, int, str]:
    """
    Non-raising visual/image check for the pipeline (images known after extraction).
    Returns (within_limit, used_images, max_images, plan_name).
    """
    ep = await owner_effective_plan(db, owner_user_id)
    q = select(func.coalesce(func.sum(File.image_count), 0)).where(File.user_id == owner_user_id)
    if exclude_file_id is not None:
        q = q.where(File.id != exclude_file_id)
    used = await db.scalar(q) or 0
    within = (not ep.locked) and (used + adding_images <= ep.limits.max_images)
    return within, int(used), ep.limits.max_images, ep.limits.name
