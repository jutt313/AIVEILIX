"""
Team management router - add/remove members, assign bucket permissions, view activity.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional, List
from app.models.team import (
    AddTeamMemberRequest,
    UpdateTeamMemberRequest,
    AssignBucketsRequest,
    TeamMemberResponse,
    TeamBucketAccessResponse,
    TeamActivityLogEntry,
    TeamInfoResponse,
)
from app.services.supabase import get_supabase
from app.services.team_service import (
    get_team_member_context,
    create_team_member_auth_account,
    delete_team_member_auth_account,
    log_team_activity,
)
from app.services.notifications import create_notification
from app.routers.buckets import get_current_user_id
from app.utils.error_logger import log_error, get_correlation_id
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _require_owner(user_id: str):
    """Raise 403 if the user is a team member (not an owner)."""
    ctx = get_team_member_context(user_id)
    if ctx:
        raise HTTPException(status_code=403, detail="Only workspace owners can manage teams")


# ==================== Member CRUD ====================

@router.post("/members", response_model=TeamMemberResponse)
async def add_team_member(
    request: AddTeamMemberRequest,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Add a new team member (owner only)."""
    correlation_id = get_correlation_id(http_request)
    _require_owner(user_id)

    try:
        supabase = get_supabase()

        # Check if real_email already exists as a team member for this owner
        existing = supabase.table("team_members").select("id").eq(
            "owner_id", user_id
        ).eq("real_email", request.real_email).eq("is_active", True).execute()
        if existing.data:
            raise HTTPException(status_code=409, detail="A team member with this email already exists")

        # Create auth account
        auth_result = create_team_member_auth_account(request.name, request.password)
        member_user_id = auth_result["user_id"]
        aiveilix_email = auth_result["aiveilix_email"]

        # Insert team_members record
        team_member_id = str(uuid.uuid4())
        member_data = {
            "id": team_member_id,
            "owner_id": user_id,
            "member_id": member_user_id,
            "name": request.name,
            "real_email": request.real_email,
            "aiveilix_email": aiveilix_email,
            "color": request.color,
            "show_name": True,
            "is_active": True,
        }
        supabase.table("team_members").insert(member_data).execute()

        # Update profile to mark as team member
        supabase.table("profiles").update({
            "is_team_member": True,
            "team_owner_id": user_id,
        }).eq("id", member_user_id).execute()

        # Notify owner
        create_notification(
            user_id=user_id,
            notification_type="team_member_added",
            title="Team Member Added",
            message=f"{request.name} has been added to your team.",
            icon="users",
            metadata={"team_member_id": team_member_id, "member_color": request.color},
        )

        # Notify the member
        create_notification(
            user_id=member_user_id,
            notification_type="team_invite",
            title="Welcome to the team!",
            message=f"You've been invited to a workspace. Log in with {aiveilix_email}.",
            icon="users",
        )

        logger.info(f"Team member added: {request.name} ({aiveilix_email}) by owner {user_id}")

        return TeamMemberResponse(
            id=team_member_id,
            owner_id=user_id,
            member_id=member_user_id,
            name=request.name,
            real_email=request.real_email,
            aiveilix_email=aiveilix_email,
            color=request.color,
            show_name=True,
            is_active=True,
            created_at=member_data.get("created_at", ""),
            updated_at=member_data.get("updated_at", ""),
            bucket_count=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(status_code=500, detail=f"Failed to add team member: {str(e)}")


@router.get("/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """List all team members (owner only)."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()
        members = supabase.table("team_members").select("*").eq(
            "owner_id", user_id
        ).order("created_at", desc=True).execute()

        result = []
        for m in (members.data or []):
            # Count bucket access
            access_count = supabase.table("team_bucket_access").select(
                "id", count="exact"
            ).eq("team_member_id", m["id"]).execute()

            result.append(TeamMemberResponse(
                id=str(m["id"]),
                owner_id=str(m["owner_id"]),
                member_id=str(m["member_id"]) if m.get("member_id") else None,
                name=m["name"],
                real_email=m["real_email"],
                aiveilix_email=m["aiveilix_email"],
                color=m["color"],
                show_name=m["show_name"],
                is_active=m["is_active"],
                removed_at=m.get("removed_at"),
                created_at=m["created_at"],
                updated_at=m["updated_at"],
                bucket_count=access_count.count if access_count.count else 0,
            ))

        return result

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to list team members: {str(e)}")


@router.get("/members/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(
    member_id: str,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Get a specific team member's details."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()
        m = supabase.table("team_members").select("*").eq(
            "id", member_id
        ).eq("owner_id", user_id).single().execute()

        if not m.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        access_count = supabase.table("team_bucket_access").select(
            "id", count="exact"
        ).eq("team_member_id", member_id).execute()

        return TeamMemberResponse(
            id=str(m.data["id"]),
            owner_id=str(m.data["owner_id"]),
            member_id=str(m.data["member_id"]) if m.data.get("member_id") else None,
            name=m.data["name"],
            real_email=m.data["real_email"],
            aiveilix_email=m.data["aiveilix_email"],
            color=m.data["color"],
            show_name=m.data["show_name"],
            is_active=m.data["is_active"],
            removed_at=m.data.get("removed_at"),
            created_at=m.data["created_at"],
            updated_at=m.data["updated_at"],
            bucket_count=access_count.count if access_count.count else 0,
        )

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get team member: {str(e)}")


@router.patch("/members/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: str,
    request: UpdateTeamMemberRequest,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Update a team member's color, show_name, or active status."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()

        # Verify member belongs to this owner
        existing = supabase.table("team_members").select("id").eq(
            "id", member_id
        ).eq("owner_id", user_id).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        update_data = {}
        if request.color is not None:
            update_data["color"] = request.color
        if request.show_name is not None:
            update_data["show_name"] = request.show_name
        if request.is_active is not None:
            update_data["is_active"] = request.is_active

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        supabase.table("team_members").update(update_data).eq("id", member_id).execute()

        # Fetch updated record
        return await get_team_member(member_id, http_request, user_id)

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to update team member: {str(e)}")


@router.delete("/members/{member_id}")
async def remove_team_member(
    member_id: str,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Soft-delete a team member. Deactivates and deletes their auth account."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()

        m = supabase.table("team_members").select("id, member_id, name").eq(
            "id", member_id
        ).eq("owner_id", user_id).single().execute()
        if not m.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        # Soft delete
        supabase.table("team_members").update({
            "is_active": False,
            "removed_at": "now()",
        }).eq("id", member_id).execute()

        # Update profile
        member_user_id = m.data.get("member_id")
        if member_user_id:
            supabase.table("profiles").update({
                "is_team_member": False,
                "team_owner_id": None,
            }).eq("id", member_user_id).execute()

            # Delete the auth account
            delete_team_member_auth_account(member_user_id)

        # Notify owner
        create_notification(
            user_id=user_id,
            notification_type="team_member_removed",
            title="Team Member Removed",
            message=f"{m.data['name']} has been removed from your team.",
            icon="users",
        )

        logger.info(f"Team member removed: {m.data['name']} (id={member_id}) by owner {user_id}")

        return {"success": True, "message": f"Team member {m.data['name']} removed"}

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to remove team member: {str(e)}")


# ==================== Bucket Access ====================

@router.post("/members/{member_id}/buckets")
async def assign_bucket_permissions(
    member_id: str,
    request: AssignBucketsRequest,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Assign or update bucket permissions for a team member."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()

        # Verify member belongs to this owner
        existing = supabase.table("team_members").select("id").eq(
            "id", member_id
        ).eq("owner_id", user_id).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        for perm in request.permissions:
            # Verify bucket belongs to owner
            bucket_check = supabase.table("buckets").select("id").eq(
                "id", perm.bucket_id
            ).eq("user_id", user_id).single().execute()
            if not bucket_check.data:
                raise HTTPException(status_code=404, detail=f"Bucket {perm.bucket_id} not found")

            # Upsert access record
            access_data = {
                "team_member_id": member_id,
                "bucket_id": perm.bucket_id,
                "can_view": perm.can_view,
                "can_chat": perm.can_chat,
                "can_upload": perm.can_upload,
                "can_delete": perm.can_delete,
            }

            # Check if exists
            existing_access = supabase.table("team_bucket_access").select("id").eq(
                "team_member_id", member_id
            ).eq("bucket_id", perm.bucket_id).execute()

            if existing_access.data:
                supabase.table("team_bucket_access").update(access_data).eq(
                    "id", existing_access.data[0]["id"]
                ).execute()
            else:
                access_data["id"] = str(uuid.uuid4())
                supabase.table("team_bucket_access").insert(access_data).execute()

        return {"success": True, "message": f"Updated permissions for {len(request.permissions)} bucket(s)"}

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to assign permissions: {str(e)}")


@router.get("/members/{member_id}/buckets", response_model=List[TeamBucketAccessResponse])
async def get_member_buckets(
    member_id: str,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Get a team member's bucket access list."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()

        # Verify member belongs to this owner
        existing = supabase.table("team_members").select("id").eq(
            "id", member_id
        ).eq("owner_id", user_id).single().execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Team member not found")

        access_list = supabase.table("team_bucket_access").select("*").eq(
            "team_member_id", member_id
        ).execute()

        result = []
        for a in (access_list.data or []):
            # Get bucket name
            bucket = supabase.table("buckets").select("name").eq("id", a["bucket_id"]).single().execute()
            bucket_name = bucket.data["name"] if bucket.data else "Unknown"

            result.append(TeamBucketAccessResponse(
                id=str(a["id"]),
                team_member_id=str(a["team_member_id"]),
                bucket_id=str(a["bucket_id"]),
                bucket_name=bucket_name,
                can_view=a["can_view"],
                can_chat=a["can_chat"],
                can_upload=a["can_upload"],
                can_delete=a["can_delete"],
                created_at=a["created_at"],
            ))

        return result

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get bucket access: {str(e)}")


@router.delete("/members/{member_id}/buckets/{bucket_id}")
async def remove_bucket_access(
    member_id: str,
    bucket_id: str,
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """Remove a team member's access to a specific bucket."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()

        supabase.table("team_bucket_access").delete().eq(
            "team_member_id", member_id
        ).eq("bucket_id", bucket_id).execute()

        return {"success": True, "message": "Bucket access removed"}

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to remove bucket access: {str(e)}")


# ==================== Activity Log ====================

@router.get("/activity", response_model=List[TeamActivityLogEntry])
async def get_team_activity(
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
    member_id: Optional[str] = Query(None),
    bucket_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """Get team activity log (owner only). Filterable by member or bucket."""
    _require_owner(user_id)
    try:
        supabase = get_supabase()

        query = supabase.table("team_activity_log").select("*").eq("owner_id", user_id)

        if member_id:
            query = query.eq("team_member_id", member_id)
        if bucket_id:
            query = query.eq("bucket_id", bucket_id)

        result = query.order("created_at", desc=True).limit(limit).execute()

        return [
            TeamActivityLogEntry(
                id=str(a["id"]),
                owner_id=str(a["owner_id"]),
                member_id=str(a["member_id"]) if a.get("member_id") else None,
                team_member_id=str(a["team_member_id"]) if a.get("team_member_id") else None,
                bucket_id=str(a["bucket_id"]) if a.get("bucket_id") else None,
                action_type=a["action_type"],
                resource_id=a.get("resource_id"),
                resource_name=a.get("resource_name"),
                member_color=a.get("member_color"),
                member_name=a.get("member_name"),
                metadata=a.get("metadata"),
                created_at=a["created_at"],
            )
            for a in (result.data or [])
        ]

    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get activity log: {str(e)}")


# ==================== Team Info ====================

@router.get("/me", response_model=TeamInfoResponse)
async def get_my_team_info(
    user_id: str = Depends(get_current_user_id),
):
    """Get current user's team membership info."""
    ctx = get_team_member_context(user_id)
    if ctx:
        return TeamInfoResponse(
            is_team_member=True,
            owner_id=ctx["owner_id"],
            team_member_id=ctx["team_member_id"],
            color=ctx["color"],
            name=ctx["name"],
            show_name=ctx["show_name"],
        )
    return TeamInfoResponse(is_team_member=False)
