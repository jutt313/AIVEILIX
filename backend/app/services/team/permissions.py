"""Helpers for resolving owner context and enforcing team-member permissions.

A user is either an OWNER (their own workspace) or a MEMBER (belongs to one
owner's workspace). Members are scoped to specific buckets via TeamBucketAccess
with granular boolean flags.

`UserContext` is the resolved identity used throughout endpoints to know which
owner's data to query and which permission set applies.
"""

import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform import TeamBucketAccess, TeamMember
from app.models.user import Profile, User


PERMISSION_FIELDS = (
    "can_see_other_members",
    "can_upload_files",
    "can_download_files",
    "can_delete_files",
    "can_use_mcp",
)


@dataclass
class UserContext:
    user_id: uuid.UUID
    email: str
    is_member: bool
    owner_user_id: uuid.UUID
    team_member_id: uuid.UUID | None
    display_name: str | None = None
    display_color: str | None = None


def parse_active_workspace(x_workspace: str | None, user_id: uuid.UUID) -> uuid.UUID | None:
    """Turn the raw X-Workspace header into an owner id to activate.

    'self'/'own'/'me' -> the user's own workspace; a uuid string -> that owner's
    workspace; anything else (missing/garbage) -> None (let the resolver default).
    """
    if not x_workspace:
        return None
    val = x_workspace.strip().lower()
    if val in {"self", "own", "me"}:
        return user_id
    try:
        return uuid.UUID(x_workspace.strip())
    except (ValueError, AttributeError):
        return None


async def resolve_user_context(
    db: AsyncSession,
    user_id: uuid.UUID,
    active_owner_id: uuid.UUID | None = None,
) -> UserContext:
    user_q = await db.execute(select(User).where(User.id == user_id))
    user = user_q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    # A single email can be a member of several workspaces while also owning its
    # own — fetch them all (the old scalar_one_or_none would crash on 2+).
    members_q = await db.execute(
        select(TeamMember).where(
            TeamMember.member_user_id == user_id,
            TeamMember.status == "accepted",
        )
    )
    memberships = list(members_q.scalars().all())

    # Decide which workspace is active for this request.
    selected: TeamMember | None = None
    if active_owner_id is not None and active_owner_id != user_id:
        # Explicit team selection; fall back to a default membership if the id is
        # stale/invalid rather than erroring.
        selected = next((m for m in memberships if m.owner_user_id == active_owner_id), None)
        if selected is None and memberships:
            selected = memberships[0]
    elif active_owner_id is None and memberships:
        # No explicit selection — default to the first membership so users who are
        # only ever team members behave exactly as before.
        selected = memberships[0]
    # active_owner_id == user_id -> explicit self/owner mode (selected stays None)

    if selected is not None:
        return UserContext(
            user_id=user.id,
            email=user.email,
            is_member=True,
            owner_user_id=selected.owner_user_id,
            team_member_id=selected.id,
            display_name=selected.display_name,
            display_color=selected.display_color,
        )

    return UserContext(
        user_id=user.id,
        email=user.email,
        is_member=False,
        owner_user_id=user.id,
        team_member_id=None,
    )


async def list_user_workspaces(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    """Workspaces this user can act in: their own ('self') plus every workspace
    they're an accepted member of. Drives the dashboard workspace switcher."""
    own_name = (
        await db.execute(select(Profile.full_name).where(Profile.user_id == user_id))
    ).scalar_one_or_none()
    workspaces: list[dict] = [{
        "id": "self",
        "type": "owner",
        "owner_user_id": str(user_id),
        "label": own_name or "My workspace",
        "color": None,
    }]

    members_q = await db.execute(
        select(TeamMember).where(
            TeamMember.member_user_id == user_id,
            TeamMember.status == "accepted",
        )
    )
    memberships = list(members_q.scalars().all())
    if not memberships:
        return workspaces

    owner_ids = [m.owner_user_id for m in memberships]
    owners = {
        o.id: o for o in (
            await db.execute(select(User).where(User.id.in_(owner_ids)))
        ).scalars().all()
    }
    names = {
        row[0]: row[1] for row in (
            await db.execute(
                select(Profile.user_id, Profile.full_name).where(Profile.user_id.in_(owner_ids))
            )
        ).all()
    }
    for m in memberships:
        owner = owners.get(m.owner_user_id)
        label = names.get(m.owner_user_id) or (owner.email if owner else "Workspace")
        workspaces.append({
            "id": str(m.owner_user_id),
            "type": "member",
            "owner_user_id": str(m.owner_user_id),
            "label": label,
            "color": m.display_color,
        })
    return workspaces


async def get_bucket_access(
    db: AsyncSession, team_member_id: uuid.UUID, bucket_id: uuid.UUID
) -> TeamBucketAccess | None:
    result = await db.execute(
        select(TeamBucketAccess).where(
            TeamBucketAccess.team_member_id == team_member_id,
            TeamBucketAccess.bucket_id == bucket_id,
        )
    )
    return result.scalar_one_or_none()


async def get_accessible_bucket_ids(
    db: AsyncSession, team_member_id: uuid.UUID
) -> list[uuid.UUID]:
    result = await db.execute(
        select(TeamBucketAccess.bucket_id).where(
            TeamBucketAccess.team_member_id == team_member_id
        )
    )
    return [row[0] for row in result.all()]


async def check_bucket_permission(
    db: AsyncSession,
    ctx: UserContext,
    bucket_id: uuid.UUID,
    permission: str,
) -> TeamBucketAccess | None:
    """Raise 403 if member lacks `permission` on bucket. Owner is always allowed."""
    if not ctx.is_member:
        return None

    if permission not in PERMISSION_FIELDS:
        raise ValueError(f"Unknown permission: {permission}")

    access = await get_bucket_access(db, ctx.team_member_id, bucket_id)
    if not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this bucket.",
        )

    if not getattr(access, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission: {permission}.",
        )
    return access


async def get_visible_team_member_ids(
    db: AsyncSession, ctx: UserContext, bucket_id: uuid.UUID
) -> set[uuid.UUID]:
    """Return team_member ids whose identity (name + color) the caller can see
    on chat bubbles in this bucket.

    Owner sees everyone. Members see themselves always; others only if
    can_see_other_members is true for this bucket.
    """
    if not ctx.is_member:
        member_q = await db.execute(
            select(TeamMember.id).where(TeamMember.owner_user_id == ctx.user_id)
        )
        return {row[0] for row in member_q.all()}

    visible: set[uuid.UUID] = {ctx.team_member_id} if ctx.team_member_id else set()
    access = await get_bucket_access(db, ctx.team_member_id, bucket_id)
    if access and access.can_see_other_members:
        member_q = await db.execute(
            select(TeamMember.id).where(TeamMember.owner_user_id == ctx.owner_user_id)
        )
        visible |= {row[0] for row in member_q.all()}
    return visible


def require_owner(ctx: UserContext) -> None:
    if ctx.is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is restricted to account owners.",
        )
