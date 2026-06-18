import secrets
import uuid
from datetime import date
from fastapi import HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Profile
from app.models.bucket import Bucket
from app.models.file import File
from app.models.conversation import Conversation, Message
from app.models.notification import Notification
from app.models.mcp_token import McpAccessLog
from app.services.notifications import create_notification


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _shift_month(value: date, delta: int) -> date:
    month_index = (value.year * 12) + (value.month - 1) + delta
    year = month_index // 12
    month = (month_index % 12) + 1
    return date(year, month, 1)


def _iter_months(start_month: date, end_month: date) -> list[date]:
    months: list[date] = []
    current = start_month
    while current <= end_month:
        months.append(current)
        current = _shift_month(current, 1)
    return months


# ---------- Profile ----------

async def get_profile(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(select(Profile).where(Profile.user_id == uuid.UUID(user_id)))
    profile = result.scalar_one_or_none()
    if not profile:
        return {"full_name": "User", "avatar_url": None}
    return {"full_name": profile.full_name or "User", "avatar_url": profile.avatar_url}


# ---------- Stats ----------

async def get_stats(db: AsyncSession, user_id: str) -> dict:
    uid = uuid.UUID(user_id)
    today = date.today()
    month_start = today.replace(day=1)

    snapshot = await _get_live_dashboard_snapshot(db, uid, month_start)

    return {
        "storage_gb": round(snapshot["storage_bytes"] / (1024 ** 3), 2),
        "storage_bytes": snapshot["storage_bytes"],
        "bucket_count": snapshot["bucket_count"],
        "files_count": snapshot["files_count"],
        "chat_messages": snapshot["chat_messages"],
        "mcp_calls": snapshot["mcp_calls"],
    }


async def _get_live_dashboard_snapshot(db: AsyncSession, uid: uuid.UUID, month_start: date) -> dict:
    # Storage & file count from the current files table.
    # `buckets.storage_used` is not kept in sync in the upload/delete/replace flow,
    # so the dashboard must compute these totals live.
    storage_and_files_result = await db.execute(
        select(
            func.coalesce(func.sum(File.size), 0),
            func.count(File.id),
        )
        .join(Bucket, File.bucket_id == Bucket.id)
        .where(Bucket.user_id == uid)
    )
    storage_bytes, files_count = storage_and_files_result.one()
    storage_bytes = int(storage_bytes or 0)
    files_count = int(files_count or 0)

    bucket_result = await db.execute(select(func.count()).where(Bucket.user_id == uid))
    bucket_count = bucket_result.scalar() or 0

    chat_messages_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.user_id == uid,
            Message.created_at >= month_start,
        )
    )
    chat_messages = int(chat_messages_result.scalar() or 0)

    # MCP calls this month, counted live from the access log.
    # `usage_tracking.mcp_calls_count` is never incremented anywhere, so it
    # would always read 0 — `mcp_access_logs` is the real source of truth.
    mcp_calls_result = await db.execute(
        select(func.count(McpAccessLog.id))
        .join(Bucket, McpAccessLog.bucket_id == Bucket.id)
        .where(
            Bucket.user_id == uid,
            McpAccessLog.created_at >= month_start,
        )
    )
    mcp_calls = int(mcp_calls_result.scalar() or 0)

    return {
        "storage_bytes": storage_bytes,
        "bucket_count": bucket_count,
        "files_count": files_count,
        "chat_messages": chat_messages,
        "mcp_calls": mcp_calls,
    }


async def _get_bucket_stats_map(
    db: AsyncSession,
    bucket_ids: list[uuid.UUID],
) -> dict[uuid.UUID, dict[str, int]]:
    if not bucket_ids:
        return {}

    result = await db.execute(
        select(
            File.bucket_id,
            func.count(File.id),
            func.coalesce(func.sum(File.size), 0),
        )
        .where(File.bucket_id.in_(bucket_ids))
        .group_by(File.bucket_id)
    )

    stats_map = {
        bucket_id: {
            "file_count": int(file_count or 0),
            "storage_used": int(storage_used or 0),
        }
        for bucket_id, file_count, storage_used in result.all()
    }

    for bucket_id in bucket_ids:
        stats_map.setdefault(bucket_id, {"file_count": 0, "storage_used": 0})

    return stats_map


async def get_monthly_stats(
    db: AsyncSession,
    user_id: str,
    start_month: date | None = None,
    end_month: date | None = None,
) -> list:
    uid = uuid.UUID(user_id)
    current_month = _month_start(date.today())
    end_month = _month_start(end_month or current_month)
    start_month = _month_start(start_month or _shift_month(end_month, -5))
    end_month_exclusive = _shift_month(end_month, 1)

    if start_month > end_month:
        raise HTTPException(status_code=400, detail="start_month cannot be after end_month.")

    bucket_baseline_result = await db.execute(
        select(func.count(Bucket.id))
        .where(
            Bucket.user_id == uid,
            Bucket.created_at < start_month,
        )
    )
    bucket_total = int(bucket_baseline_result.scalar() or 0)

    file_baseline_result = await db.execute(
        select(
            func.count(File.id),
            func.coalesce(func.sum(File.size), 0),
        )
        .join(Bucket, File.bucket_id == Bucket.id)
        .where(
            Bucket.user_id == uid,
            File.created_at < start_month,
        )
    )
    file_total, storage_total = file_baseline_result.one()
    file_total = int(file_total or 0)
    storage_total = int(storage_total or 0)

    bucket_month_expr = func.date_trunc("month", Bucket.created_at).label("bucket_month")
    bucket_rows = await db.execute(
        select(bucket_month_expr, func.count(Bucket.id))
        .where(
            Bucket.user_id == uid,
            Bucket.created_at >= start_month,
            Bucket.created_at < end_month_exclusive,
        )
        .group_by(bucket_month_expr)
        .order_by(bucket_month_expr.asc())
    )
    bucket_increments = {
        bucket_month.date().replace(day=1): int(bucket_count or 0)
        for bucket_month, bucket_count in bucket_rows.all()
    }

    file_month_expr = func.date_trunc("month", File.created_at).label("file_month")
    file_rows = await db.execute(
        select(
            file_month_expr,
            func.count(File.id),
            func.coalesce(func.sum(File.size), 0),
        )
        .join(Bucket, File.bucket_id == Bucket.id)
        .where(
            Bucket.user_id == uid,
            File.created_at >= start_month,
            File.created_at < end_month_exclusive,
        )
        .group_by(file_month_expr)
        .order_by(file_month_expr.asc())
    )
    file_increments: dict[date, dict[str, int]] = {}
    for file_month, file_count, storage_used in file_rows.all():
        file_increments[file_month.date().replace(day=1)] = {
            "files": int(file_count or 0),
            "storage": int(storage_used or 0),
        }

    message_month_expr = func.date_trunc("month", Message.created_at).label("message_month")
    message_rows = await db.execute(
        select(message_month_expr, func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.user_id == uid,
            Message.created_at >= start_month,
            Message.created_at < end_month_exclusive,
        )
        .group_by(message_month_expr)
        .order_by(message_month_expr.asc())
    )
    message_counts = {
        message_month.date().replace(day=1): int(message_count or 0)
        for message_month, message_count in message_rows.all()
    }

    mcp_month_expr = func.date_trunc("month", McpAccessLog.created_at).label("mcp_month")
    mcp_rows = await db.execute(
        select(mcp_month_expr, func.count(McpAccessLog.id))
        .join(Bucket, McpAccessLog.bucket_id == Bucket.id)
        .where(
            Bucket.user_id == uid,
            McpAccessLog.created_at >= start_month,
            McpAccessLog.created_at < end_month_exclusive,
        )
        .group_by(mcp_month_expr)
        .order_by(mcp_month_expr.asc())
    )
    mcp_calls_by_month = {
        mcp_month.date().replace(day=1): int(mcp_calls or 0)
        for mcp_month, mcp_calls in mcp_rows.all()
    }

    series: list[dict[str, object]] = []
    for month in _iter_months(start_month, end_month):
        bucket_total += bucket_increments.get(month, 0)
        file_total += file_increments.get(month, {}).get("files", 0)
        storage_total += file_increments.get(month, {}).get("storage", 0)
        series.append({
            "month": str(month),
            "storage_gb": round(storage_total / (1024 ** 3), 4),
            "files": file_total,
            "buckets": bucket_total,
            "messages": message_counts.get(month, 0),
            "mcp_calls": mcp_calls_by_month.get(month, 0),
        })

    return series


# ---------- Buckets ----------

async def get_bucket(db: AsyncSession, user_id: str, bucket_id: str) -> dict:
    uid = uuid.UUID(user_id)
    bid = uuid.UUID(bucket_id)
    result = await db.execute(
        select(Bucket).where(Bucket.id == bid, Bucket.user_id == uid)
    )
    bucket = result.scalar_one_or_none()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found.")
    bucket_stats = await _get_bucket_stats_map(db, [bid])
    file_count = bucket_stats[bid]["file_count"]
    storage_used = bucket_stats[bid]["storage_used"]
    return {
        "id": str(bucket.id),
        "name": bucket.name,
        "description": bucket.description,
        "color": bucket.color,
        "icon": bucket.icon,
        "storage_used": storage_used,
        "storage_gb": round(storage_used / (1024 ** 3), 2),
        "file_count": file_count,
        "updated_at": bucket.updated_at.isoformat(),
        "created_at": bucket.created_at.isoformat(),
    }


async def list_buckets(db: AsyncSession, user_id: str) -> list:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Bucket).where(Bucket.user_id == uid).order_by(desc(Bucket.updated_at))
    )
    buckets = result.scalars().all()

    stats_map = await _get_bucket_stats_map(db, [b.id for b in buckets])

    out = []
    for b in buckets:
        bucket_stats = stats_map.get(b.id, {"file_count": 0, "storage_used": 0})
        file_count = bucket_stats["file_count"]
        storage_used = bucket_stats["storage_used"]
        out.append({
            "id": str(b.id),
            "name": b.name,
            "description": b.description,
            "color": b.color,
            "icon": b.icon,
            "storage_used": storage_used,
            "storage_gb": round(storage_used / (1024 ** 3), 2),
            "file_count": file_count,
            "updated_at": b.updated_at.isoformat(),
            "created_at": b.created_at.isoformat(),
        })
    return out


async def create_bucket(db: AsyncSession, user_id: str, name: str, description: str | None, color: str, icon: str) -> dict:
    uid = uuid.UUID(user_id)
    mcp_token = secrets.token_urlsafe(32)
    bucket = Bucket(
        user_id=uid,
        name=name,
        description=description,
        color=color,
        icon=icon,
        mcp_token=mcp_token,
    )
    db.add(bucket)
    try:
        await db.flush()
        await create_notification(
            db,
            user_id,
            "success",
            "Bucket created",
            f'Bucket "{name}" was created successfully.',
        )
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        if "buckets_name_per_user_unique" in str(exc.orig):
            raise HTTPException(status_code=409, detail="A bucket with this name already exists.") from exc
        raise
    await db.refresh(bucket)
    return {
        "id": str(bucket.id),
        "name": bucket.name,
        "description": bucket.description,
        "color": bucket.color,
        "icon": bucket.icon,
        "storage_gb": 0,
        "file_count": 0,
        "updated_at": bucket.updated_at.isoformat(),
        "created_at": bucket.created_at.isoformat(),
    }


async def update_bucket(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    name: str | None,
    description: str | None,
    color: str | None,
    icon: str | None,
) -> dict:
    uid = uuid.UUID(user_id)
    bid = uuid.UUID(bucket_id)
    result = await db.execute(
        select(Bucket).where(Bucket.id == bid, Bucket.user_id == uid)
    )
    bucket = result.scalar_one_or_none()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found.")
    if name is not None:
        bucket.name = name
    if description is not None:
        bucket.description = description
    if color is not None:
        bucket.color = color
    if icon is not None:
        bucket.icon = icon
    await create_notification(
        db,
        user_id,
        "info",
        "Bucket updated",
        f'Bucket "{bucket.name}" was updated successfully.',
    )
    await db.commit()
    await db.refresh(bucket)
    bucket_stats = await _get_bucket_stats_map(db, [bid])
    file_count = bucket_stats[bid]["file_count"]
    storage_used = bucket_stats[bid]["storage_used"]
    return {
        "id": str(bucket.id),
        "name": bucket.name,
        "description": bucket.description,
        "color": bucket.color,
        "icon": bucket.icon,
        "storage_used": storage_used,
        "storage_gb": round(storage_used / (1024 ** 3), 2),
        "file_count": file_count,
        "updated_at": bucket.updated_at.isoformat(),
        "created_at": bucket.created_at.isoformat(),
    }


async def delete_all_buckets(db: AsyncSession, user_id: str) -> dict:
    uid = uuid.UUID(user_id)
    result = await db.execute(select(Bucket).where(Bucket.user_id == uid))
    buckets = result.scalars().all()
    deleted_count = len(buckets)
    for bucket in buckets:
        await db.delete(bucket)
    await create_notification(
        db,
        user_id,
        "warning",
        "All buckets deleted",
        f"{deleted_count} bucket(s) were deleted from your account.",
    )
    await db.commit()
    return {"message": "All buckets deleted successfully.", "deleted_count": deleted_count}


async def delete_bucket(db: AsyncSession, user_id: str, bucket_id: str) -> dict:
    uid = uuid.UUID(user_id)
    bid = uuid.UUID(bucket_id)
    result = await db.execute(
        select(Bucket).where(Bucket.id == bid, Bucket.user_id == uid)
    )
    bucket = result.scalar_one_or_none()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found.")

    bucket_name = bucket.name
    await db.delete(bucket)
    await create_notification(
        db,
        user_id,
        "warning",
        "Bucket deleted",
        f'Bucket "{bucket_name}" was deleted successfully.',
    )
    await db.commit()
    return {"message": "Bucket deleted successfully.", "id": bucket_id}


# ---------- Notifications ----------

async def list_notifications(db: AsyncSession, user_id: str) -> list:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == uid)
        .order_by(desc(Notification.created_at))
        .limit(20)
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(n.id),
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in rows
    ]


async def mark_all_notifications_read(db: AsyncSession, user_id: str):
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Notification).where(Notification.user_id == uid, Notification.is_read == False)
    )
    notifications = result.scalars().all()
    for n in notifications:
        n.is_read = True
    await db.commit()
