"""
Team service for managing team members, permissions, and activity tracking.
"""
from app.services.supabase import get_supabase, get_supabase_auth
from typing import Optional, Dict, List
import logging
import re

logger = logging.getLogger(__name__)


def get_team_member_context(user_id: str) -> Optional[Dict]:
    """
    Check if user_id belongs to a team member.
    Returns {owner_id, team_member_id, color, name, show_name} or None if not a team member.
    """
    try:
        supabase = get_supabase()
        profile = supabase.table("profiles").select(
            "is_team_member, team_owner_id"
        ).eq("id", user_id).single().execute()

        if not profile.data or not profile.data.get("is_team_member"):
            return None

        owner_id = profile.data.get("team_owner_id")
        if not owner_id:
            return None

        # Get the team_members record
        member = supabase.table("team_members").select(
            "id, color, name, show_name, is_active"
        ).eq("member_id", user_id).eq("owner_id", owner_id).eq("is_active", True).single().execute()

        if not member.data:
            return None

        return {
            "owner_id": str(owner_id),
            "team_member_id": str(member.data["id"]),
            "color": member.data["color"],
            "name": member.data["name"],
            "show_name": member.data["show_name"],
        }
    except Exception as e:
        logger.error(f"Error getting team member context: {e}")
        return None


def get_effective_user_id(user_id: str) -> str:
    """
    Returns the owner_id for team members, or the user_id itself for owners.
    All data queries should use this to access the owner's data.
    """
    ctx = get_team_member_context(user_id)
    if ctx:
        return ctx["owner_id"]
    return user_id


def check_bucket_permission(user_id: str, bucket_id: str, permission: str) -> bool:
    """
    Check if a team member has a specific permission on a bucket.
    Returns True for non-team-members (owners).
    permission: 'can_view', 'can_chat', 'can_upload', 'can_delete'
    """
    ctx = get_team_member_context(user_id)
    if not ctx:
        return True  # Not a team member = owner, has all permissions

    try:
        supabase = get_supabase()
        access = supabase.table("team_bucket_access").select(
            permission
        ).eq("team_member_id", ctx["team_member_id"]).eq("bucket_id", bucket_id).single().execute()

        if not access.data:
            return False

        return access.data.get(permission, False)
    except Exception as e:
        logger.error(f"Error checking bucket permission: {e}")
        return False


def get_member_accessible_buckets(user_id: str) -> Optional[List[str]]:
    """
    Get list of bucket IDs a team member can access (with can_view=true).
    Returns None for non-team-members (owners see all).
    """
    ctx = get_team_member_context(user_id)
    if not ctx:
        return None  # Owner sees all

    try:
        supabase = get_supabase()
        access = supabase.table("team_bucket_access").select(
            "bucket_id"
        ).eq("team_member_id", ctx["team_member_id"]).eq("can_view", True).execute()

        return [a["bucket_id"] for a in (access.data or [])]
    except Exception as e:
        logger.error(f"Error getting accessible buckets: {e}")
        return []


def log_team_activity(
    owner_id: str,
    member_id: Optional[str],
    team_member_id: Optional[str],
    bucket_id: Optional[str],
    action_type: str,
    resource_id: Optional[str] = None,
    resource_name: Optional[str] = None,
    member_color: Optional[str] = None,
    member_name: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """Insert a row into team_activity_log."""
    try:
        supabase = get_supabase()
        supabase.table("team_activity_log").insert({
            "owner_id": owner_id,
            "member_id": member_id,
            "team_member_id": team_member_id,
            "bucket_id": bucket_id,
            "action_type": action_type,
            "resource_id": resource_id,
            "resource_name": resource_name,
            "member_color": member_color,
            "member_name": member_name,
            "metadata": metadata or {},
        }).execute()
    except Exception as e:
        logger.error(f"Error logging team activity: {e}")


def _sanitize_username(name: str) -> str:
    """Convert a display name to a valid email username part."""
    username = name.lower().strip()
    username = re.sub(r'[^a-z0-9]', '', username)
    if not username:
        username = "member"
    return username


def create_team_member_auth_account(name: str, password: str) -> Dict:
    """
    Create a Supabase Auth user with name@aiveilix.com email.
    Returns {"user_id": str, "aiveilix_email": str}.
    """
    supabase = get_supabase()
    username = _sanitize_username(name)
    aiveilix_email = f"{username}@aiveilix.com"

    # Check uniqueness and append number if needed
    existing = supabase.table("team_members").select("id").eq("aiveilix_email", aiveilix_email).execute()
    if existing.data:
        counter = 1
        while True:
            candidate = f"{username}{counter}@aiveilix.com"
            check = supabase.table("team_members").select("id").eq("aiveilix_email", candidate).execute()
            if not check.data:
                aiveilix_email = candidate
                break
            counter += 1

    # Create the auth user
    response = supabase.auth.admin.create_user({
        "email": aiveilix_email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {
            "full_name": name,
            "is_team_member": True,
        }
    })

    if not response.user:
        raise Exception("Failed to create team member auth account")

    return {
        "user_id": str(response.user.id),
        "aiveilix_email": aiveilix_email,
    }


def delete_team_member_auth_account(member_user_id: str):
    """Delete a team member's Supabase Auth account."""
    try:
        supabase = get_supabase()
        supabase.auth.admin.delete_user(member_user_id)
        logger.info(f"Deleted auth account for team member: {member_user_id}")
    except Exception as e:
        logger.error(f"Error deleting team member auth account: {e}")
