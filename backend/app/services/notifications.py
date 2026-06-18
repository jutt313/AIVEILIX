import uuid

from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

DEFAULT_NOTIFICATION_LIMIT = 20
MAX_NOTIFICATION_LIMIT = 100


def serialize_notification(notification: Notification) -> dict:
    return {
        "id": str(notification.id),
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
    }


async def create_notification(
    db: AsyncSession,
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    *,
    commit: bool = False,
) -> Notification:
    notification = Notification(
        user_id=uuid.UUID(user_id),
        type=notification_type,
        title=title[:255],
        message=message,
        is_read=False,
    )
    db.add(notification)
    await db.flush()
    if commit:
        await db.commit()
        await db.refresh(notification)
    return notification


async def list_notifications(
    db: AsyncSession,
    user_id: str,
    *,
    unread_only: bool = False,
    notification_type: str | None = None,
    limit: int = DEFAULT_NOTIFICATION_LIMIT,
) -> list[dict]:
    uid = uuid.UUID(user_id)
    safe_limit = max(1, min(limit, MAX_NOTIFICATION_LIMIT))

    stmt = select(Notification).where(Notification.user_id == uid)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    if notification_type:
        stmt = stmt.where(Notification.type == notification_type)

    result = await db.execute(
        stmt.order_by(desc(Notification.created_at)).limit(safe_limit)
    )
    return [serialize_notification(row) for row in result.scalars().all()]


async def get_unread_notification_count(db: AsyncSession, user_id: str) -> int:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == uid,
            Notification.is_read.is_(False),
        )
    )
    return int(result.scalar() or 0)


async def mark_notification_read(
    db: AsyncSession,
    user_id: str,
    notification_id: str,
    *,
    is_read: bool,
) -> dict:
    uid = uuid.UUID(user_id)
    nid = uuid.UUID(notification_id)
    result = await db.execute(
        select(Notification).where(Notification.id == nid, Notification.user_id == uid)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found.")

    notification.is_read = is_read
    await db.commit()
    await db.refresh(notification)
    return serialize_notification(notification)


async def mark_all_notifications_read(db: AsyncSession, user_id: str) -> dict:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Notification).where(Notification.user_id == uid, Notification.is_read.is_(False))
    )
    notifications = result.scalars().all()
    for notification in notifications:
        notification.is_read = True
    await db.commit()
    return {"updated_count": len(notifications)}


async def mark_notifications_read_bulk(
    db: AsyncSession,
    user_id: str,
    notification_ids: list[str],
) -> dict:
    uid = uuid.UUID(user_id)
    parsed_ids = [uuid.UUID(notification_id) for notification_id in notification_ids]
    if not parsed_ids:
        return {"updated_count": 0}

    result = await db.execute(
        select(Notification).where(
            Notification.user_id == uid,
            Notification.id.in_(parsed_ids),
        )
    )
    notifications = result.scalars().all()
    for notification in notifications:
        notification.is_read = True
    await db.commit()
    return {"updated_count": len(notifications)}


async def delete_notification(db: AsyncSession, user_id: str, notification_id: str) -> dict:
    uid = uuid.UUID(user_id)
    nid = uuid.UUID(notification_id)
    result = await db.execute(
        select(Notification).where(Notification.id == nid, Notification.user_id == uid)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found.")

    await db.delete(notification)
    await db.commit()
    return {"message": "Notification deleted.", "id": notification_id}


async def clear_read_notifications(db: AsyncSession, user_id: str) -> dict:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Notification).where(Notification.user_id == uid, Notification.is_read.is_(True))
    )
    notifications = result.scalars().all()
    deleted_count = len(notifications)
    for notification in notifications:
        await db.delete(notification)
    await db.commit()
    return {"message": "Read notifications cleared.", "deleted_count": deleted_count}


async def clear_all_notifications(db: AsyncSession, user_id: str) -> dict:
    uid = uuid.UUID(user_id)
    result = await db.execute(
        select(Notification).where(Notification.user_id == uid)
    )
    notifications = result.scalars().all()
    deleted_count = len(notifications)
    for notification in notifications:
        await db.delete(notification)
    await db.commit()
    return {"message": "All notifications cleared.", "deleted_count": deleted_count}
