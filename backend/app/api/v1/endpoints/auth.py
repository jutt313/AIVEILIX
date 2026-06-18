from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    VerifyEmailRequest, VerifyEmailResponse,
    LoginRequest, LoginResponse, LoginRequires2FAResponse,
    Verify2FARequest,
    Enable2FAResponse,
    Confirm2FARequest, Confirm2FAResponse,
    Disable2FARequest, Disable2FAResponse,
    RefreshRequest, RefreshResponse,
    LogoutResponse,
    ResendVerificationRequest, ResendVerificationResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    OAuthRequest, OAuthResponse,
)
from app.services import auth as auth_service
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, body.full_name, body.email, body.password)


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(body: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.verify_email(db, body.token)


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.login(db, body.email, body.password)
    if result.get("requires_2fa"):
        return LoginRequires2FAResponse(**result)
    return LoginResponse(**result)


@router.post("/2fa/verify", response_model=LoginResponse)
async def verify_2fa(body: Verify2FARequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.verify_2fa(db, body.temp_token, body.code)


@router.post("/2fa/enable", response_model=Enable2FAResponse)
async def enable_2fa(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await auth_service.enable_2fa(db, str(current_user["user_id"]))


@router.post("/2fa/confirm", response_model=Confirm2FAResponse)
async def confirm_2fa(body: Confirm2FARequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await auth_service.confirm_2fa(db, str(current_user["user_id"]), body.code)


@router.post("/2fa/disable", response_model=Disable2FAResponse)
async def disable_2fa(body: Disable2FARequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await auth_service.disable_2fa(db, str(current_user["user_id"]), body.code)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(body: RefreshRequest):
    return await auth_service.refresh_token(body.refresh_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(body: RefreshRequest, current_user=Depends(get_current_user)):
    return await auth_service.logout(
        jti=current_user["jti"],
        exp=current_user["exp"],
        refresh=body.refresh_token,
    )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.resend_verification(db, body.email)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.forgot_password(db, body.email)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.reset_password(db, body.token, body.new_password)


@router.get("/{provider}/authorize-url")
async def get_oauth_authorize_url(provider: str, redirect_uri: str, mode: str = "login"):
    return auth_service.get_oauth_authorize_url(provider, redirect_uri, mode)


@router.post("/google", response_model=OAuthResponse)
async def google_oauth(body: OAuthRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.google_oauth(db, body.code, body.redirect_uri)


@router.post("/github", response_model=OAuthResponse)
async def github_oauth(body: OAuthRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.github_oauth(db, body.code, body.redirect_uri)
