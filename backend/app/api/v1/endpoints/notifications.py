from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.database import get_db
from app.services.notifications import (
    clear_all_notifications,
    clear_read_notifications,
    delete_notification as delete_notification_service,
    get_unread_notification_count,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    mark_notifications_read_bulk,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationBulkReadRequest(BaseModel):
    ids: list[str]


@router.get("")
async def list_notifications_endpoint(
    unread_only: bool = False,
    type: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_notifications(
        db,
        str(current_user["user_id"]),
        unread_only=unread_only,
        notification_type=type,
        limit=limit,
    )


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return {"count": await get_unread_notification_count(db, str(current_user["user_id"]))}


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await mark_notification_read(db, str(current_user["user_id"]), notification_id, is_read=True)


@router.patch("/{notification_id}/unread")
async def mark_unread(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await mark_notification_read(db, str(current_user["user_id"]), notification_id, is_read=False)


@router.put("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await mark_all_notifications_read(db, str(current_user["user_id"]))
    return {"message": "All notifications marked as read.", **result}


@router.post("/read")
async def mark_bulk_read(
    body: NotificationBulkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await mark_notifications_read_bulk(db, str(current_user["user_id"]), body.ids)
    return {"message": "Selected notifications marked as read.", **result}


@router.delete("")
async def clear_read(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await clear_read_notifications(db, str(current_user["user_id"]))


@router.delete("/all")
async def clear_all(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await clear_all_notifications(db, str(current_user["user_id"]))


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await delete_notification_service(db, str(current_user["user_id"]), notification_id)
