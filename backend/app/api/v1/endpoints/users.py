from datetime import datetime, date

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.api.v1.deps import get_current_user, get_user_context
from app.services.team.permissions import UserContext, list_user_workspaces
from app.services.profile import (
    change_password as change_password_service,
    connect_auth_provider as connect_auth_provider_service,
    delete_account as delete_account_service,
    disconnect_auth_provider as disconnect_auth_provider_service,
    get_auth_provider_connect_url as get_auth_provider_connect_url_service,
    get_profile,
    save_onboarding,
    update_profile as update_profile_service,
    upload_avatar,
)
from app.services.dashboard import get_stats, get_monthly_stats

router = APIRouter(prefix="/user", tags=["user"])


def _parse_month(value: str | None, field_name: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m").date().replace(day=1)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}. Use YYYY-MM.") from exc


class OnboardingRequest(BaseModel):
    use_case: str
    need: str
    referral_source: str


class OnboardingResponse(BaseModel):
    message: str


class UpdateProfileRequest(BaseModel):
    full_name: str
    bio: str | None = None
    theme: str = "dark"
    language: str = "en"
    timezone: str = "UTC"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    password: str


class OAuthConnectRequest(BaseModel):
    code: str
    redirect_uri: str


@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(
    body: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await save_onboarding(db, str(current_user["user_id"]), body.use_case, body.need, body.referral_source)
    return {"message": "Onboarding saved."}


@router.get("/profile")
async def get_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_profile(db, str(current_user["user_id"]))


@router.get("/me")
async def get_me(
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from sqlalchemy import select
    from app.models.user import Profile, User

    workspace_owner_name: str | None = None
    workspace_owner_email: str | None = None
    if ctx.is_member and ctx.owner_user_id != ctx.user_id:
        owner_q = await db.execute(select(User).where(User.id == ctx.owner_user_id))
        owner = owner_q.scalar_one_or_none()
        if owner:
            workspace_owner_email = owner.email
            prof_q = await db.execute(
                select(Profile.full_name).where(Profile.user_id == owner.id)
            )
            full_name = prof_q.scalar_one_or_none()
            workspace_owner_name = full_name or owner.email

    # All workspaces this user can switch between (own + memberships), plus which
    # one is currently active — drives the dashboard workspace switcher.
    workspaces = await list_user_workspaces(db, ctx.user_id)
    active_workspace = "self" if not ctx.is_member else str(ctx.owner_user_id)

    return {
        "user_id": str(ctx.user_id),
        "email": ctx.email,
        "is_member": ctx.is_member,
        "owner_user_id": str(ctx.owner_user_id),
        "team_member_id": str(ctx.team_member_id) if ctx.team_member_id else None,
        "display_name": ctx.display_name,
        "display_color": ctx.display_color,
        "role": "member" if ctx.is_member else "owner",
        "workspace_owner_name": workspace_owner_name,
        "workspace_owner_email": workspace_owner_email,
        "workspaces": workspaces,
        "active_workspace": active_workspace,
    }


@router.get("/stats")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_stats(db, str(current_user["user_id"]))


@router.get("/stats/monthly")
async def get_user_monthly_stats(
    start_month: str | None = None,
    end_month: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_monthly_stats(
        db,
        str(current_user["user_id"]),
        start_month=_parse_month(start_month, "start_month"),
        end_month=_parse_month(end_month, "end_month"),
    )


@router.put("/profile")
async def update_profile(
    body: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_profile_service(
        db,
        str(current_user["user_id"]),
        body.full_name,
        body.bio,
        body.theme,
        body.language,
        body.timezone,
    )


@router.put("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await upload_avatar(db, str(current_user["user_id"]), file)


@router.put("/password")
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await change_password_service(db, str(current_user["user_id"]), body.current_password, body.new_password)


@router.get("/auth-provider/{provider}/connect-url")
async def get_auth_provider_connect_url(
    provider: str,
    redirect_uri: str,
    current_user=Depends(get_current_user),
):
    return await get_auth_provider_connect_url_service(provider, redirect_uri)


@router.post("/auth-provider/{provider}")
async def connect_auth_provider(
    provider: str,
    body: OAuthConnectRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await connect_auth_provider_service(db, str(current_user["user_id"]), provider, body.code, body.redirect_uri)


@router.delete("/auth-provider/{provider}")
async def disconnect_auth_provider_by_name(
    provider: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await disconnect_auth_provider_service(db, str(current_user["user_id"]), provider)


@router.delete("/auth-provider")
async def disconnect_auth_provider(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await disconnect_auth_provider_service(db, str(current_user["user_id"]))


@router.delete("/account")
async def delete_account(
    body: DeleteAccountRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await delete_account_service(db, str(current_user["user_id"]), body.password)
