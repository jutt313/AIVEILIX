import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.bucket import Bucket
from app.models.platform import TeamBucketAccess, TeamMember
from app.models.user import Profile, User
from app.schemas.team import (
    BucketAccessGrantRequest,
    BucketPermissionToggles,
    TeamMemberInviteRequest,
    TeamMemberUpdateRequest,
)
from app.services.email import send_team_invite_email


INVITE_TOKEN_TTL_DAYS = 7


def _generate_invite_token() -> str:
    return secrets.token_urlsafe(48)


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _ensure_buckets_owned(db: AsyncSession, owner_id: uuid.UUID, bucket_ids: list[uuid.UUID]) -> dict[uuid.UUID, Bucket]:
    if not bucket_ids:
        return {}
    result = await db.execute(
        select(Bucket).where(Bucket.id.in_(bucket_ids), Bucket.user_id == owner_id)
    )
    buckets = {b.id: b for b in result.scalars().all()}
    missing = [bid for bid in bucket_ids if bid not in buckets]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not own bucket(s): {missing}",
        )
    return buckets


def _apply_permissions(access: TeamBucketAccess, perms: BucketPermissionToggles) -> None:
    access.history_scope = perms.history_scope
    access.can_see_other_members = perms.can_see_other_members
    access.can_upload_files = perms.can_upload_files
    access.can_download_files = perms.can_download_files
    access.can_delete_files = perms.can_delete_files
    access.can_use_mcp = perms.can_use_mcp


async def invite_member(
    db: AsyncSession,
    owner: User,
    request: TeamMemberInviteRequest,
) -> TeamMember:
    bucket_map = await _ensure_buckets_owned(
        db, owner.id, [b.bucket_id for b in request.buckets]
    )

    existing_q = await db.execute(
        select(TeamMember).where(
            TeamMember.owner_user_id == owner.id,
            TeamMember.invite_email == str(request.email).lower(),
            TeamMember.status == "pending",
        )
    )
    if existing_q.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending invite already exists for this email.",
        )

    existing_user_q = await db.execute(
        select(TeamMember).join(User, TeamMember.member_user_id == User.id).where(
            TeamMember.owner_user_id == owner.id,
            User.email == str(request.email).lower(),
            TeamMember.status == "accepted",
        )
    )
    if existing_user_q.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is already a member of your team.",
        )

    member = TeamMember(
        owner_user_id=owner.id,
        member_user_id=None,
        invited_by_user_id=owner.id,
        display_name=request.display_name,
        display_color=request.display_color,
        invite_email=str(request.email).lower(),
        invite_token=_generate_invite_token(),
        invite_token_expires_at=_now() + timedelta(days=INVITE_TOKEN_TTL_DAYS),
        invite_note=request.note,
        status="pending",
    )
    db.add(member)
    await db.flush()

    for grant in request.buckets:
        access = TeamBucketAccess(
            team_member_id=member.id,
            bucket_id=grant.bucket_id,
            granted_by_user_id=owner.id,
        )
        _apply_permissions(access, grant.permissions)
        db.add(access)

    await db.commit()
    await db.refresh(member)

    owner_name = await _resolve_display_name(db, owner)
    try:
        send_team_invite_email(
            to=member.invite_email,
            display_name=member.display_name or "there",
            owner_name=owner_name,
            invite_token=member.invite_token,
            note=member.invite_note,
        )
    except Exception:
        pass

    return member


async def list_members(db: AsyncSession, owner_id: uuid.UUID) -> list[TeamMember]:
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.owner_user_id == owner_id)
        .order_by(TeamMember.created_at.desc())
    )
    return list(result.scalars().all())


async def get_member(db: AsyncSession, owner_id: uuid.UUID, member_id: uuid.UUID) -> TeamMember:
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.id == member_id, TeamMember.owner_user_id == owner_id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found.")
    return member


async def update_member(
    db: AsyncSession,
    owner_id: uuid.UUID,
    member_id: uuid.UUID,
    request: TeamMemberUpdateRequest,
) -> TeamMember:
    member = await get_member(db, owner_id, member_id)
    if request.display_name is not None:
        member.display_name = request.display_name
    if request.display_color is not None:
        member.display_color = request.display_color
    await db.commit()
    await db.refresh(member)
    return member


async def remove_member(
    db: AsyncSession, owner_id: uuid.UUID, member_id: uuid.UUID
) -> None:
    member = await get_member(db, owner_id, member_id)
    await db.delete(member)
    await db.commit()


async def resend_invite(
    db: AsyncSession, owner: User, member_id: uuid.UUID
) -> TeamMember:
    member = await get_member(db, owner.id, member_id)
    if member.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Cannot resend invite — member already accepted.",
        )
    member.invite_token = _generate_invite_token()
    member.invite_token_expires_at = _now() + timedelta(days=INVITE_TOKEN_TTL_DAYS)
    await db.commit()
    await db.refresh(member)

    owner_name = await _resolve_display_name(db, owner)
    try:
        send_team_invite_email(
            to=member.invite_email,
            display_name=member.display_name or "there",
            owner_name=owner_name,
            invite_token=member.invite_token,
            note=member.invite_note,
        )
    except Exception:
        pass
    return member


async def validate_invite(db: AsyncSession, token: str) -> dict:
    result = await db.execute(
        select(TeamMember).where(TeamMember.invite_token == token)
    )
    member = result.scalar_one_or_none()
    if not member:
        return {"valid": False, "member": None, "owner": None}

    if member.status == "accepted":
        return {
            "valid": False,
            "already_accepted": True,
            "member": member,
            "owner": None,
        }

    if (
        member.invite_token_expires_at
        and member.invite_token_expires_at < _now()
    ):
        return {"valid": False, "expired": True, "member": member, "owner": None}

    owner_q = await db.execute(
        select(User).options(selectinload(User.profile)).where(
            User.id == member.owner_user_id
        )
    )
    owner = owner_q.scalar_one_or_none()
    return {"valid": True, "member": member, "owner": owner}


async def accept_invite(db: AsyncSession, token: str, password: str) -> dict:
    info = await validate_invite(db, token)
    if not info["valid"]:
        raise HTTPException(
            status_code=400,
            detail="Invite link is invalid, expired, or already used.",
        )

    member: TeamMember = info["member"]
    member_email = member.invite_email.lower()

    user_q = await db.execute(select(User).where(User.email == member_email))
    user = user_q.scalar_one_or_none()

    if user:
        if not user.password_hash:
            user.password_hash = hash_password(password)
    else:
        user = User(
            email=member_email,
            password_hash=hash_password(password),
            provider="email",
            is_verified=True,
        )
        db.add(user)
        await db.flush()
        profile = Profile(user_id=user.id, full_name=member.display_name or "")
        db.add(profile)

    member.member_user_id = user.id
    member.status = "accepted"
    member.accepted_at = _now()
    member.invite_token = None

    await db.commit()
    await db.refresh(member)
    await db.refresh(user)

    access_token = create_access_token(str(user.id), user.email)
    refresh = create_refresh_token()

    return {
        "access_token": access_token,
        "refresh_token": refresh,
        "user_id": user.id,
        "team_member_id": member.id,
        "workspace_owner_id": member.owner_user_id,
    }


async def list_bucket_access(
    db: AsyncSession, owner_id: uuid.UUID, bucket_id: uuid.UUID
) -> list[tuple[TeamBucketAccess, TeamMember]]:
    bucket_q = await db.execute(
        select(Bucket).where(Bucket.id == bucket_id, Bucket.user_id == owner_id)
    )
    if not bucket_q.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bucket not found.")

    result = await db.execute(
        select(TeamBucketAccess, TeamMember)
        .join(TeamMember, TeamBucketAccess.team_member_id == TeamMember.id)
        .where(
            TeamBucketAccess.bucket_id == bucket_id,
            TeamMember.owner_user_id == owner_id,
        )
        .order_by(TeamBucketAccess.granted_at.desc())
    )
    return list(result.all())


async def grant_bucket_access(
    db: AsyncSession,
    owner: User,
    bucket_id: uuid.UUID,
    team_member_id: uuid.UUID,
    permissions: BucketPermissionToggles,
) -> TeamBucketAccess:
    await _ensure_buckets_owned(db, owner.id, [bucket_id])
    member = await get_member(db, owner.id, team_member_id)

    existing_q = await db.execute(
        select(TeamBucketAccess).where(
            TeamBucketAccess.bucket_id == bucket_id,
            TeamBucketAccess.team_member_id == team_member_id,
        )
    )
    existing = existing_q.scalar_one_or_none()
    if existing:
        _apply_permissions(existing, permissions)
        existing.granted_by_user_id = owner.id
        await db.commit()
        await db.refresh(existing)
        return existing

    access = TeamBucketAccess(
        team_member_id=member.id,
        bucket_id=bucket_id,
        granted_by_user_id=owner.id,
    )
    _apply_permissions(access, permissions)
    db.add(access)
    await db.commit()
    await db.refresh(access)
    return access


async def update_bucket_access(
    db: AsyncSession,
    owner_id: uuid.UUID,
    bucket_id: uuid.UUID,
    team_member_id: uuid.UUID,
    permissions: BucketPermissionToggles,
) -> TeamBucketAccess:
    await _ensure_buckets_owned(db, owner_id, [bucket_id])
    result = await db.execute(
        select(TeamBucketAccess).where(
            TeamBucketAccess.bucket_id == bucket_id,
            TeamBucketAccess.team_member_id == team_member_id,
        )
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found.")
    _apply_permissions(access, permissions)
    await db.commit()
    await db.refresh(access)
    return access


async def revoke_bucket_access(
    db: AsyncSession,
    owner_id: uuid.UUID,
    bucket_id: uuid.UUID,
    team_member_id: uuid.UUID,
) -> None:
    await _ensure_buckets_owned(db, owner_id, [bucket_id])
    result = await db.execute(
        select(TeamBucketAccess).where(
            TeamBucketAccess.bucket_id == bucket_id,
            TeamBucketAccess.team_member_id == team_member_id,
        )
    )
    access = result.scalar_one_or_none()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found.")
    await db.delete(access)
    await db.commit()


async def _resolve_display_name(db: AsyncSession, user: User) -> str:
    result = await db.execute(select(Profile).where(Profile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile and profile.full_name:
        return profile.full_name
    return user.email


async def get_member_buckets(
    db: AsyncSession, member_id: uuid.UUID
) -> list[tuple[TeamBucketAccess, Bucket]]:
    result = await db.execute(
        select(TeamBucketAccess, Bucket)
        .join(Bucket, TeamBucketAccess.bucket_id == Bucket.id)
        .where(TeamBucketAccess.team_member_id == member_id)
    )
    return list(result.all())
