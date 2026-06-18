import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.database import get_db
from app.models.bucket import Bucket
from app.models.conversation import Conversation, Message
from app.models.platform import TeamBucketAccess, TeamMember
from app.models.user import Profile, User
from app.schemas.team import (
    BucketAccessGrant,
    BucketAccessListResponse,
    BucketAccessMemberInfo,
    BucketAccessResponse,
    BucketAccessSummary,
    BucketAccessUpdate,
    BucketPermissionToggles,
    InviteAcceptRequest,
    InviteAcceptResponse,
    InviteValidateResponse,
    TeamActivityItem,
    TeamActivityResponse,
    TeamMemberInviteRequest,
    TeamMemberListResponse,
    TeamMemberResponse,
    TeamMemberUpdateRequest,
)
from app.services.team import service as team_service
from app.services.team.permissions import require_owner, resolve_user_context
from app.services.quota import enforce_seat_quota


ONLINE_WINDOW_MIN = 15
ACTIVITY_LIMIT = 40
ACTIVITY_LOOKBACK_DAYS = 30


router = APIRouter(prefix="/team", tags=["team"])


def _bucket_perms(access: TeamBucketAccess) -> BucketPermissionToggles:
    return BucketPermissionToggles(
        history_scope=access.history_scope,
        can_see_other_members=access.can_see_other_members,
        can_upload_files=access.can_upload_files,
        can_download_files=access.can_download_files,
        can_delete_files=access.can_delete_files,
        can_use_mcp=access.can_use_mcp,
    )


async def _serialize_member(
    db: AsyncSession, member: TeamMember
) -> TeamMemberResponse:
    access_q = await db.execute(
        select(TeamBucketAccess, Bucket)
        .join(Bucket, TeamBucketAccess.bucket_id == Bucket.id)
        .where(TeamBucketAccess.team_member_id == member.id)
    )
    buckets = [
        BucketAccessSummary(
            bucket_id=bucket.id,
            bucket_name=bucket.name,
            permissions=_bucket_perms(access),
        )
        for access, bucket in access_q.all()
    ]

    avatar_url = None
    last_login_at = None
    last_seen_at = None
    if member.member_user_id:
        user_q = await db.execute(
            select(Profile.avatar_url, User.last_login_at, User.last_seen_at)
            .select_from(User)
            .outerjoin(Profile, Profile.user_id == User.id)
            .where(User.id == member.member_user_id)
        )
        row = user_q.first()
        if row:
            avatar_url, last_login_at, last_seen_at = row

    last_msg_at = None
    if member.id:
        last_msg = await db.execute(
            select(func.max(Message.created_at)).where(
                Message.sender_team_member_id == member.id
            )
        )
        last_msg_at = last_msg.scalar_one_or_none()

    # Last activity = the most recent signal we have: a heartbeat (any app use),
    # a chat message, or — failing both — when they accepted the invite.
    candidates = [t for t in (last_seen_at, last_msg_at, member.accepted_at) if t]
    last_active_at = max(candidates) if candidates else None

    online_cutoff = datetime.now(timezone.utc) - timedelta(minutes=ONLINE_WINDOW_MIN)
    is_online = bool(last_seen_at and last_seen_at >= online_cutoff)

    return TeamMemberResponse(
        id=member.id,
        owner_user_id=member.owner_user_id,
        member_user_id=member.member_user_id,
        invited_by_user_id=member.invited_by_user_id,
        display_name=member.display_name,
        display_color=member.display_color,
        invite_email=member.invite_email,
        avatar_url=avatar_url,
        status=member.status,
        accepted_at=member.accepted_at,
        last_active_at=last_active_at,
        last_login_at=last_login_at,
        is_online=is_online,
        created_at=member.created_at,
        buckets=buckets,
    )


async def _ensure_owner(
    db: AsyncSession, current_user: dict
) -> User:
    # Team management always acts on the user's OWN workspace, so resolve in
    # self/owner mode regardless of which workspace they're currently viewing.
    user_id = uuid.UUID(current_user["user_id"])
    ctx = await resolve_user_context(db, user_id, active_owner_id=user_id)
    require_owner(ctx)
    user_q = await db.execute(select(User).where(User.id == ctx.user_id))
    user = user_q.scalar_one()
    return user


# ---------- Team management (owner-only) ----------


@router.post("/invite", response_model=TeamMemberResponse)
async def invite_member(
    body: TeamMemberInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    await enforce_seat_quota(db, owner.id)
    member = await team_service.invite_member(db, owner, body)
    return await _serialize_member(db, member)


@router.get("/members", response_model=TeamMemberListResponse)
async def list_members(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    members = await team_service.list_members(db, owner.id)
    serialized = [await _serialize_member(db, m) for m in members]
    return TeamMemberListResponse(members=serialized, total=len(serialized))


@router.get("/members/{member_id}", response_model=TeamMemberResponse)
async def get_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    member = await team_service.get_member(db, owner.id, member_id)
    return await _serialize_member(db, member)


@router.patch("/members/{member_id}", response_model=TeamMemberResponse)
async def update_member(
    member_id: uuid.UUID,
    body: TeamMemberUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    member = await team_service.update_member(db, owner.id, member_id, body)
    return await _serialize_member(db, member)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    await team_service.remove_member(db, owner.id, member_id)


@router.post("/members/{member_id}/resend-invite", response_model=TeamMemberResponse)
async def resend_invite(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    member = await team_service.resend_invite(db, owner, member_id)
    return await _serialize_member(db, member)


# ---------- Bucket access (owner-only) ----------


@router.get(
    "/buckets/{bucket_id}/access",
    response_model=BucketAccessListResponse,
)
async def list_bucket_access(
    bucket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    rows = await team_service.list_bucket_access(db, owner.id, bucket_id)
    members = [
        BucketAccessMemberInfo(
            team_member_id=member.id,
            display_name=member.display_name,
            display_color=member.display_color,
            invite_email=member.invite_email,
            status=member.status,
            permissions=_bucket_perms(access),
            granted_at=access.granted_at,
        )
        for access, member in rows
    ]
    return BucketAccessListResponse(bucket_id=bucket_id, members=members)


@router.post(
    "/buckets/{bucket_id}/access",
    response_model=BucketAccessResponse,
)
async def grant_bucket_access(
    bucket_id: uuid.UUID,
    body: BucketAccessGrant,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    access = await team_service.grant_bucket_access(
        db, owner, bucket_id, body.team_member_id, body.permissions
    )
    return BucketAccessResponse.model_validate(access)


@router.patch(
    "/buckets/{bucket_id}/access/{team_member_id}",
    response_model=BucketAccessResponse,
)
async def update_bucket_access(
    bucket_id: uuid.UUID,
    team_member_id: uuid.UUID,
    body: BucketAccessUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    access = await team_service.update_bucket_access(
        db, owner.id, bucket_id, team_member_id, body.permissions
    )
    return BucketAccessResponse.model_validate(access)


@router.delete(
    "/buckets/{bucket_id}/access/{team_member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_bucket_access(
    bucket_id: uuid.UUID,
    team_member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    await team_service.revoke_bucket_access(
        db, owner.id, bucket_id, team_member_id
    )


# ---------- Workspace activity feed (owner-only) ----------


@router.get("/activity", response_model=TeamActivityResponse)
async def get_team_activity(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    owner = await _ensure_owner(db, current_user)
    cutoff = datetime.now(timezone.utc) - timedelta(days=ACTIVITY_LOOKBACK_DAYS)

    member_q = await db.execute(
        select(TeamMember).where(TeamMember.owner_user_id == owner.id)
    )
    members = list(member_q.scalars().all())
    member_by_id = {m.id: m for m in members}

    avatars: dict[uuid.UUID, str | None] = {}
    user_ids = [m.member_user_id for m in members if m.member_user_id]
    if user_ids:
        prof_q = await db.execute(
            select(Profile.user_id, Profile.avatar_url).where(
                Profile.user_id.in_(user_ids)
            )
        )
        avatar_by_user = {row[0]: row[1] for row in prof_q.all()}
        for m in members:
            if m.member_user_id:
                avatars[m.id] = avatar_by_user.get(m.member_user_id)

    items: list[TeamActivityItem] = []

    for m in members:
        if m.status == "accepted" and m.accepted_at and m.accepted_at >= cutoff:
            items.append(
                TeamActivityItem(
                    id=f"joined:{m.id}",
                    kind="joined",
                    team_member_id=m.id,
                    display_name=m.display_name,
                    display_color=m.display_color,
                    avatar_url=avatars.get(m.id),
                    created_at=m.accepted_at,
                )
            )
        elif m.status == "pending" and m.created_at >= cutoff:
            items.append(
                TeamActivityItem(
                    id=f"invited:{m.id}",
                    kind="invited",
                    team_member_id=m.id,
                    display_name=m.display_name,
                    display_color=m.display_color,
                    avatar_url=avatars.get(m.id),
                    created_at=m.created_at,
                )
            )

    conv_q = await db.execute(
        select(Conversation, Bucket)
        .join(Bucket, Conversation.bucket_id == Bucket.id)
        .where(
            Conversation.created_by_team_member_id.in_([m.id for m in members]) if members else False,
            Conversation.created_at >= cutoff,
        )
        .order_by(desc(Conversation.created_at))
        .limit(ACTIVITY_LIMIT)
    )
    for conv, bucket in conv_q.all():
        m = member_by_id.get(conv.created_by_team_member_id)
        if not m:
            continue
        items.append(
            TeamActivityItem(
                id=f"thread:{conv.id}",
                kind="created_thread",
                team_member_id=m.id,
                display_name=m.display_name,
                display_color=m.display_color,
                avatar_url=avatars.get(m.id),
                bucket_id=bucket.id,
                bucket_name=bucket.name,
                conversation_id=conv.id,
                conversation_title=conv.title,
                created_at=conv.created_at,
            )
        )

    msg_q = await db.execute(
        select(Message, Conversation, Bucket)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .join(Bucket, Conversation.bucket_id == Bucket.id)
        .where(
            Message.sender_team_member_id.in_([m.id for m in members]) if members else False,
            Message.created_at >= cutoff,
        )
        .order_by(desc(Message.created_at))
        .limit(ACTIVITY_LIMIT)
    )
    for msg, conv, bucket in msg_q.all():
        m = member_by_id.get(msg.sender_team_member_id)
        if not m:
            continue
        snippet = (msg.content or "").strip().replace("\n", " ")
        if len(snippet) > 140:
            snippet = snippet[:137] + "..."
        items.append(
            TeamActivityItem(
                id=f"msg:{msg.id}",
                kind="sent_message",
                team_member_id=m.id,
                display_name=m.display_name,
                display_color=m.display_color,
                avatar_url=avatars.get(m.id),
                bucket_id=bucket.id,
                bucket_name=bucket.name,
                conversation_id=conv.id,
                conversation_title=conv.title,
                snippet=snippet,
                created_at=msg.created_at,
            )
        )

    items.sort(key=lambda it: it.created_at, reverse=True)
    items = items[:ACTIVITY_LIMIT]

    # Online = the member's user account had any authenticated activity (heartbeat)
    # within the window — not merely "sent a chat message", which missed anyone who
    # was logged in and browsing without chatting.
    online_cutoff = datetime.now(timezone.utc) - timedelta(minutes=ONLINE_WINDOW_MIN)
    online_ids: list[uuid.UUID] = []
    member_user_ids = [m.member_user_id for m in members if m.member_user_id]
    if member_user_ids:
        online_q = await db.execute(
            select(User.id).where(
                User.id.in_(member_user_ids),
                User.last_seen_at.is_not(None),
                User.last_seen_at >= online_cutoff,
            )
        )
        online_user_ids = {row[0] for row in online_q.all()}
        online_ids = [
            m.id for m in members
            if m.member_user_id and m.member_user_id in online_user_ids
        ]

    return TeamActivityResponse(items=items, online_member_ids=online_ids)


# ---------- Public invite accept ----------


@router.get("/invite/{token}", response_model=InviteValidateResponse)
async def validate_invite(token: str, db: AsyncSession = Depends(get_db)):
    info = await team_service.validate_invite(db, token)
    if not info.get("member"):
        return InviteValidateResponse(valid=False)

    member: TeamMember = info["member"]
    owner = info.get("owner")
    owner_name: str | None = None
    owner_email: str | None = None
    if owner:
        owner_email = owner.email
        prof_q = await db.execute(
            select(Profile).where(Profile.user_id == owner.id)
        )
        prof = prof_q.scalar_one_or_none()
        owner_name = prof.full_name if prof and prof.full_name else owner.email

    return InviteValidateResponse(
        valid=info["valid"],
        expired=info.get("expired", False),
        already_accepted=info.get("already_accepted", False),
        workspace_owner_name=owner_name,
        workspace_owner_email=owner_email,
        invite_email=member.invite_email,
        display_name=member.display_name,
        display_color=member.display_color,
        expires_at=member.invite_token_expires_at,
    )


@router.post("/invite/{token}/accept", response_model=InviteAcceptResponse)
async def accept_invite(
    token: str,
    body: InviteAcceptRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await team_service.accept_invite(db, token, body.password)
    return InviteAcceptResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user_id=result["user_id"],
        team_member_id=result["team_member_id"],
        workspace_owner_id=result["workspace_owner_id"],
    )
