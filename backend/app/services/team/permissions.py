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
from app.models.user import User


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


async def resolve_user_context(db: AsyncSession, user_id: uuid.UUID) -> UserContext:
    user_q = await db.execute(select(User).where(User.id == user_id))
    user = user_q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    member_q = await db.execute(
        select(TeamMember).where(
            TeamMember.member_user_id == user_id,
            TeamMember.status == "accepted",
        )
    )
    member = member_q.scalar_one_or_none()

    if member:
        return UserContext(
            user_id=user.id,
            email=user.email,
            is_member=True,
            owner_user_id=member.owner_user_id,
            team_member_id=member.id,
            display_name=member.display_name,
            display_color=member.display_color,
        )

    return UserContext(
        user_id=user.id,
        email=user.email,
        is_member=False,
        owner_user_id=user.id,
        team_member_id=None,
    )


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
