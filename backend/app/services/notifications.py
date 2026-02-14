"""
Notification service for creating user notifications
"""
from app.services.supabase import get_supabase
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    icon: Optional[str] = None,
    metadata: Optional[Dict] = None,
    action_url: Optional[str] = None
):
    """
    Create a notification for a user
    
    Args:
        user_id: User ID
        notification_type: Type of notification (login, mcp_run, file_uploaded, etc.)
        title: Notification title
        message: Notification message
        icon: Optional icon name
        metadata: Optional metadata dict (e.g., {"bucket_id": "...", "file_id": "..."})
        action_url: Optional URL to navigate when clicked
    """
    try:
        supabase = get_supabase()
        
        notification_data = {
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "icon": icon,
            "metadata": metadata or {},
            "action_url": action_url
        }
        
        result = supabase.table("notifications").insert(notification_data).execute()
        
        if result.data:
            logger.info(f"✅ Notification created for user {user_id}: {title}")
            return result.data[0]
        else:
            logger.warning(f"⚠️ Failed to create notification for user {user_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error creating notification: {str(e)}")
        return None


def create_login_notification(user_id: str):
    """Create a notification when user logs in"""
    return create_notification(
        user_id=user_id,
        notification_type="login",
        title="Welcome back!",
        message="You have successfully logged in to AIveilix.",
        icon="check"
    )


def create_mcp_run_notification(user_id: str, bucket_id: Optional[str] = None, details: Optional[str] = None):
    """Create a notification when MCP is run"""
    action_url = f"/buckets/{bucket_id}" if bucket_id else None
    return create_notification(
        user_id=user_id,
        notification_type="mcp_run",
        title="MCP Command Executed",
        message=f"MCP command has been executed successfully.{' ' + details if details else ''}",
        icon="terminal",
        metadata={"bucket_id": bucket_id} if bucket_id else None,
        action_url=action_url
    )


def create_file_uploaded_notification(user_id: str, file_name: str, bucket_id: str, file_id: str):
    """Create a notification when a file is uploaded"""
    return create_notification(
        user_id=user_id,
        notification_type="file_uploaded",
        title="File Uploaded",
        message=f"File '{file_name}' has been uploaded successfully.",
        icon="file",
        metadata={"bucket_id": bucket_id, "file_id": file_id},
        action_url=f"/buckets/{bucket_id}"
    )


def create_file_processed_notification(user_id: str, file_name: str, bucket_id: str, file_id: str):
    """Create a notification when a file is processed"""
    return create_notification(
        user_id=user_id,
        notification_type="file_processed",
        title="File Processed",
        message=f"File '{file_name}' has been processed and is ready to use.",
        icon="check",
        metadata={"bucket_id": bucket_id, "file_id": file_id},
        action_url=f"/buckets/{bucket_id}"
    )


def create_bucket_created_notification(user_id: str, bucket_name: str, bucket_id: str):
    """Create a notification when a bucket is created"""
    return create_notification(
        user_id=user_id,
        notification_type="bucket_created",
        title="Bucket Created",
        message=f"Bucket '{bucket_name}' has been created successfully.",
        icon="folder",
        metadata={"bucket_id": bucket_id},
        action_url=f"/buckets/{bucket_id}"
    )


def create_api_key_created_notification(user_id: str, key_name: str, key_id: str):
    """Create a notification when an API key is created"""
    return create_notification(
        user_id=user_id,
        notification_type="api_key_created",
        title="API Key Created",
        message=f"API key '{key_name}' has been created successfully.",
        icon="key",
        metadata={"api_key_id": key_id},
        action_url="/dashboard"
    )


def create_team_member_added_notification(owner_id: str, member_name: str, member_color: str):
    """Create a notification when a team member is added"""
    return create_notification(
        user_id=owner_id,
        notification_type="team_member_added",
        title="Team Member Added",
        message=f"{member_name} has been added to your team.",
        icon="users",
        metadata={"member_name": member_name, "member_color": member_color}
    )


def create_team_member_removed_notification(owner_id: str, member_name: str):
    """Create a notification when a team member is removed"""
    return create_notification(
        user_id=owner_id,
        notification_type="team_member_removed",
        title="Team Member Removed",
        message=f"{member_name} has been removed from your team.",
        icon="users",
        metadata={"member_name": member_name}
    )


def create_team_invite_notification(member_user_id: str, owner_name: str):
    """Create a notification for the invited team member"""
    return create_notification(
        user_id=member_user_id,
        notification_type="team_invite",
        title="Team Invitation",
        message=f"You've been invited to {owner_name}'s workspace on AIveilix.",
        icon="users",
    )


def create_conversation_created_notification(user_id: str, bucket_id: str, conversation_id: str):
    """Create a notification when a conversation is created"""
    return create_notification(
        user_id=user_id,
        notification_type="conversation_created",
        title="New Conversation",
        message="A new conversation has been started.",
        icon="message",
        metadata={"bucket_id": bucket_id, "conversation_id": conversation_id},
        action_url=f"/buckets/{bucket_id}"
    )
