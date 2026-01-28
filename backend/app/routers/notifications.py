from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from app.services.supabase import get_supabase_auth, get_supabase
from app.routers.buckets import get_current_user_id
from postgrest.exceptions import APIError as PostgrestAPIError
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Models
class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    icon: Optional[str] = None
    metadata: Optional[dict] = None
    action_url: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    icon: Optional[str]
    metadata: Optional[dict]
    action_url: Optional[str]
    is_read: bool
    read_at: Optional[str]
    created_at: str
    updated_at: str


@router.get("", response_model=dict)
async def get_notifications(
    user_id: str = Depends(get_current_user_id),
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False
):
    """Get all notifications for the current user"""
    try:
        supabase = get_supabase_auth()
        
        query = supabase.table("notifications").select("*").eq("user_id", user_id)
        
        if unread_only:
            query = query.eq("is_read", False)
        
        query = query.order("created_at", desc=True).limit(limit).offset(offset)
        
        result = query.execute()
        
        # Get unread count
        unread_result = supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
        unread_count = unread_result.count if hasattr(unread_result, 'count') else 0
        
        return {
            "notifications": result.data or [],
            "unread_count": unread_count,
            "total": len(result.data) if result.data else 0
        }
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error getting notifications: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/unread-count")
async def get_unread_count(
    user_id: str = Depends(get_current_user_id)
):
    """Get count of unread notifications"""
    try:
        supabase = get_supabase_auth()
        
        result = supabase.table("notifications").select("id", count="exact").eq("user_id", user_id).eq("is_read", False).execute()
        unread_count = result.count if hasattr(result, 'count') else 0
        
        return {"unread_count": unread_count}
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error getting unread count: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("", response_model=dict)
async def create_notification(
    notification: NotificationCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new notification"""
    try:
        supabase = get_supabase()
        
        notification_data = {
            "user_id": user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "icon": notification.icon,
            "metadata": notification.metadata,
            "action_url": notification.action_url
        }
        
        result = supabase.table("notifications").insert(notification_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create notification")
        
        return {"notification": result.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error creating notification: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Mark a notification as read"""
    try:
        supabase = get_supabase()
        
        # Verify notification belongs to user
        check_res = supabase.table("notifications").select("id").eq("id", notification_id).eq("user_id", user_id).single().execute()
        if not check_res.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Update to read
        result = supabase.table("notifications").update({"is_read": True}).eq("id", notification_id).execute()
        
        return {"message": "Notification marked as read", "notification": result.data[0] if result.data else None}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error marking notification as read: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.patch("/mark-all-read")
async def mark_all_as_read(
    user_id: str = Depends(get_current_user_id)
):
    """Mark all notifications as read"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("notifications").update({"is_read": True}).eq("user_id", user_id).eq("is_read", False).execute()
        
        return {"message": "All notifications marked as read", "count": len(result.data) if result.data else 0}
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error marking all notifications as read: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a notification"""
    try:
        supabase = get_supabase()
        
        # Verify notification belongs to user
        check_res = supabase.table("notifications").select("id").eq("id", notification_id).eq("user_id", user_id).single().execute()
        if not check_res.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Delete notification
        supabase.table("notifications").delete().eq("id", notification_id).execute()
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error deleting notification: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/delete-all-read")
async def delete_all_read(
    user_id: str = Depends(get_current_user_id)
):
    """Delete all read notifications"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("notifications").delete().eq("user_id", user_id).eq("is_read", True).execute()
        
        return {"message": "All read notifications deleted", "count": len(result.data) if result.data else 0}
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Error deleting read notifications: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
