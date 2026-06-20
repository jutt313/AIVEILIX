import uuid
import random
import httpx
from datetime import timedelta, timezone, datetime
from urllib.parse import urlencode
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func

from app.config import settings
from app.models.user import User, Profile, OAuthToken
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, create_temp_token,
    decode_token_safe,
    generate_totp_secret, get_totp_uri, verify_totp,
    generate_backup_codes,
)
from app.valkey import get_valkey
from app.services.email import send_verification_email, send_password_reset_email
from app.services.notifications import create_notification

REFRESH_TTL = settings.refresh_token_expire_days * 86400
RESET_TTL = 3600       # 1 hour
VERIFY_TTL = 86400     # 24 hours
RATE_LIMIT_TTL = 3600  # 1 hour
MAX_FAILED = 5


# ---------- helpers ----------

async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()


def _stamp_login(user: User) -> None:
    """Record a successful sign-in. Persisted by the caller's commit."""
    user.last_login_at = func.now()
    user.last_seen_at = func.now()


async def _check_rate_limit(email: str):
    v = get_valkey()
    key = f"failed_login:{email}"
    attempts = await v.get(key)
    if attempts and int(attempts) >= MAX_FAILED:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again in 1 hour.",
        )


async def _record_failed_attempt(email: str):
    v = get_valkey()
    key = f"failed_login:{email}"
    await v.incr(key)
    await v.expire(key, RATE_LIMIT_TTL)


async def _reset_failed_attempts(email: str):
    v = get_valkey()
    await v.delete(f"failed_login:{email}")


async def _store_refresh_token(user_id: str, token: str):
    v = get_valkey()
    await v.setex(f"refresh:{token}", REFRESH_TTL, user_id)


async def _delete_refresh_token(token: str):
    v = get_valkey()
    await v.delete(f"refresh:{token}")


def _oauth_error_detail(response: httpx.Response, fallback: str) -> str:
    try:
        data = response.json()
    except ValueError:
        data = {}
    if isinstance(data, dict):
        for key in ("error_description", "error", "message"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value
    text = response.text.strip()
    return text or fallback


async def _blacklist_access_token(jti: str, ttl: int):
    v = get_valkey()
    await v.setex(f"blacklist:{jti}", ttl, "1")


def get_oauth_authorize_url(
    provider: str,
    redirect_uri: str,
    mode: str = "login",
    state_token: str | None = None,
) -> dict:
    if provider not in {"google", "github"}:
        raise HTTPException(status_code=400, detail="Unsupported auth provider.")
    if mode not in {"login", "connect"}:
        raise HTTPException(status_code=400, detail="Invalid OAuth mode.")

    state = f"{mode}:{provider}"
    if state_token:
        state = f"{state}:{state_token}"
    if provider == "google":
        if not settings.google_client_id or settings.google_client_id == "your-google-client-id":
            raise HTTPException(status_code=400, detail="Google sign-in is not configured.")
        params = urlencode({
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        })
        return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{params}"}

    if not settings.github_client_id or settings.github_client_id == "your-github-client-id":
        raise HTTPException(status_code=400, detail="GitHub sign-in is not configured.")
    params = urlencode({
        "client_id": settings.github_client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
        "state": state,
    })
    return {"url": f"https://github.com/login/oauth/authorize?{params}"}


async def _upsert_oauth_token(
    db: AsyncSession,
    user: User,
    provider: str,
    access_token: str | None,
    refresh_token: str | None = None,
    expires_at: datetime | None = None,
):
    result = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == provider,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.expires_at = expires_at
        return

    db.add(OAuthToken(
        user_id=user.id,
        provider=provider,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    ))


# ---------- Register ----------

async def register(db: AsyncSession, full_name: str, email: str, password: str) -> dict:
    existing = await _get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        email=email,
        password_hash=hash_password(password),
        provider="email",
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    profile = Profile(user_id=user.id, full_name=full_name)
    db.add(profile)

    # Start the 15-day Individual free trial for every new account.
    from app.models.platform import Subscription
    from app.services.plans import trial_end_from
    db.add(Subscription(
        user_id=user.id,
        plan="individual",
        status="active",
        current_period_end=trial_end_from(),
    ))

    await create_notification(
        db,
        str(user.id),
        "success",
        "Account created",
        "Your AIveilix account was created successfully. Verify your email to unlock everything.",
    )
    await db.commit()
    await db.refresh(user)

    # Store email verification token in Valkey
    token = str(uuid.uuid4())
    v = get_valkey()
    await v.setex(f"email_verify:{token}", VERIFY_TTL, str(user.id))

    send_verification_email(email, token)
    return {"message": "Account created. Please check your email to verify your account."}


# ---------- Verify Email ----------

async def verify_email(db: AsyncSession, token: str) -> dict:
    v = get_valkey()
    user_id = await v.get(f"email_verify:{token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link.")

    user = await _get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_verified = True
    _stamp_login(user)
    await create_notification(
        db,
        str(user.id),
        "success",
        "Email verified",
        "Your email address has been verified successfully.",
    )
    await db.commit()
    await v.delete(f"email_verify:{token}")

    # Auto-login on verify: issue a session so the user lands straight in the
    # onboarding flow without re-entering their credentials.
    access_token = create_access_token(str(user.id), user.email)
    refresh_token = create_refresh_token()
    await _store_refresh_token(str(user.id), refresh_token)
    return {
        "message": "Email verified successfully.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# ---------- Login ----------

async def login(db: AsyncSession, email: str, password: str) -> dict:
    await _check_rate_limit(email)

    user = await _get_user_by_email(db, email)
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        await _record_failed_attempt(email)
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")

    await _reset_failed_attempts(email)

    if user.two_factor_enabled:
        temp_token = create_temp_token(str(user.id))
        return {"requires_2fa": True, "temp_token": temp_token}

    access_token = create_access_token(str(user.id), user.email)
    refresh_token = create_refresh_token()
    await _store_refresh_token(str(user.id), refresh_token)
    _stamp_login(user)
    await create_notification(
        db,
        str(user.id),
        "info",
        "Signed in",
        "You signed in to your AIveilix account.",
        commit=True,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# ---------- 2FA Verify ----------

async def verify_2fa(db: AsyncSession, temp_token: str, code: str) -> dict:
    payload = decode_token_safe(temp_token)
    if not payload or payload.get("type") != "2fa_temp":
        raise HTTPException(status_code=401, detail="Invalid or expired 2FA session.")

    user = await _get_user_by_id(db, payload["user_id"])
    if not user or not user.two_factor_secret:
        raise HTTPException(status_code=401, detail="2FA not configured.")

    # Check backup codes first
    if user.two_factor_backup_codes:
        backup_codes = list(user.two_factor_backup_codes)
        if code in backup_codes:
            backup_codes.remove(code)
            user.two_factor_backup_codes = backup_codes
            _stamp_login(user)
            await create_notification(
                db,
                str(user.id),
                "info",
                "Signed in with backup code",
                "You signed in using a two-factor backup code.",
            )
            await db.commit()
            access_token = create_access_token(str(user.id), user.email)
            refresh_token = create_refresh_token()
            await _store_refresh_token(str(user.id), refresh_token)
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    if not verify_totp(user.two_factor_secret, code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code.")

    access_token = create_access_token(str(user.id), user.email)
    refresh_token = create_refresh_token()
    await _store_refresh_token(str(user.id), refresh_token)
    _stamp_login(user)
    await create_notification(
        db,
        str(user.id),
        "info",
        "Signed in",
        "You signed in with two-factor authentication.",
        commit=True,
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# ---------- Enable 2FA ----------

async def enable_2fa(db: AsyncSession, user_id: str) -> dict:
    user = await _get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    secret = generate_totp_secret()
    user.two_factor_secret = secret
    await create_notification(
        db,
        str(user.id),
        "info",
        "2FA setup started",
        "Two-factor authentication setup has started. Confirm it to finish enabling protection.",
    )
    await db.commit()

    return {"secret": secret, "qr_uri": get_totp_uri(secret, user.email)}


# ---------- Confirm 2FA ----------

async def confirm_2fa(db: AsyncSession, user_id: str, code: str) -> dict:
    user = await _get_user_by_id(db, user_id)
    if not user or not user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA setup not started.")

    if not verify_totp(user.two_factor_secret, code):
        raise HTTPException(status_code=400, detail="Invalid code.")

    backup_codes = generate_backup_codes()
    user.two_factor_enabled = True
    user.two_factor_backup_codes = backup_codes
    await create_notification(
        db,
        str(user.id),
        "success",
        "2FA enabled",
        "Two-factor authentication is now enabled on your account.",
    )
    await db.commit()

    return {"message": "Two-factor authentication enabled successfully.", "backup_codes": backup_codes}


# ---------- Disable 2FA ----------

async def disable_2fa(db: AsyncSession, user_id: str, code: str) -> dict:
    user = await _get_user_by_id(db, user_id)
    if not user or not user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA is not enabled.")

    if not verify_totp(user.two_factor_secret, code):
        raise HTTPException(status_code=400, detail="Invalid code.")

    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.two_factor_backup_codes = []
    await create_notification(
        db,
        str(user.id),
        "warning",
        "2FA disabled",
        "Two-factor authentication has been disabled on your account.",
    )
    await db.commit()
    return {"message": "Two-factor authentication disabled successfully."}


# ---------- Refresh Token ----------

async def refresh_token(token: str) -> dict:
    v = get_valkey()
    user_id = await v.get(f"refresh:{token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    access_token = create_access_token(user_id, "")
    return {"access_token": access_token, "token_type": "bearer"}


# ---------- Logout ----------

async def logout(jti: str, exp: int, refresh: str | None = None):
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = max(exp - now, 1)
    await _blacklist_access_token(jti, ttl)
    if refresh:
        await _delete_refresh_token(refresh)
    return {"message": "Logged out successfully."}


# ---------- Resend Verification ----------

async def resend_verification(db: AsyncSession, email: str) -> dict:
    user = await _get_user_by_email(db, email)
    if user and not user.is_verified:
        token = str(uuid.uuid4())
        v = get_valkey()
        await v.setex(f"email_verify:{token}", VERIFY_TTL, str(user.id))
        send_verification_email(email, token)
        await create_notification(
            db,
            str(user.id),
            "info",
            "Verification email resent",
            "A new email verification link was sent to your inbox.",
            commit=True,
        )
    return {"message": "If this email exists and is unverified, a new confirmation link has been sent."}


# ---------- Forgot Password ----------

async def forgot_password(db: AsyncSession, email: str) -> dict:
    user = await _get_user_by_email(db, email)
    if user:
        code = str(random.randint(100000, 999999))
        v = get_valkey()
        await v.setex(f"password_reset:{code}", RESET_TTL, str(user.id))
        send_password_reset_email(email, code)
        await create_notification(
            db,
            str(user.id),
            "warning",
            "Password reset requested",
            "A password reset code was requested for your account.",
            commit=True,
        )
    return {"message": "If this email exists, a reset code has been sent."}


# ---------- Reset Password ----------

async def reset_password(db: AsyncSession, token: str, new_password: str) -> dict:
    v = get_valkey()
    user_id = await v.get(f"password_reset:{token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    user = await _get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.password_hash = hash_password(new_password)
    await create_notification(
        db,
        str(user.id),
        "success",
        "Password reset successful",
        "Your account password was reset successfully.",
    )
    await db.commit()
    await v.delete(f"password_reset:{token}")
    return {"message": "Password reset successfully."}


# ---------- Google OAuth ----------

async def exchange_google_oauth(code: str, redirect_uri: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        if token_resp.is_error:
            raise HTTPException(
                status_code=400,
                detail=f"Google token exchange failed: {_oauth_error_detail(token_resp, 'OAuth request was rejected.')}",
            )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Google token exchange did not return an access token.")
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.is_error:
            raise HTTPException(
                status_code=400,
                detail=f"Google user profile fetch failed: {_oauth_error_detail(user_resp, 'Unable to load Google profile.')}",
            )
        user_info = user_resp.json()

    expires_at = None
    if token_data.get("expires_in"):
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(token_data["expires_in"]))

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account did not provide an email address.")
    if user_info.get("verified_email") is False or user_info.get("email_verified") is False:
        raise HTTPException(status_code=400, detail="Google account email is not verified.")

    return {
        "email": email,
        "name": user_info.get("name", ""),
        "provider_id": user_info["id"],
        "access_token": access_token,
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": expires_at,
    }


async def google_oauth(db: AsyncSession, code: str, redirect_uri: str) -> dict:
    result = await exchange_google_oauth(code, redirect_uri)
    return await _oauth_login(
        db,
        email=result["email"],
        name=result["name"],
        provider="google",
        provider_id=result["provider_id"],
        oauth_access_token=result.get("access_token"),
        oauth_refresh_token=result.get("refresh_token"),
        oauth_expires_at=result.get("expires_at"),
    )


# ---------- GitHub OAuth ----------

async def exchange_github_oauth(code: str, redirect_uri: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={"client_id": settings.github_client_id, "client_secret": settings.github_client_secret, "code": code, "redirect_uri": redirect_uri},
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_info = user_resp.json()
        email_resp = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        emails = email_resp.json()
        primary_email = next((e["email"] for e in emails if e["primary"]), user_info.get("email"))

    return {
        "email": primary_email,
        "name": user_info.get("name") or user_info.get("login", ""),
        "provider_id": str(user_info["id"]),
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": None,
    }


async def github_oauth(db: AsyncSession, code: str, redirect_uri: str) -> dict:
    result = await exchange_github_oauth(code, redirect_uri)
    return await _oauth_login(
        db,
        email=result["email"],
        name=result["name"],
        provider="github",
        provider_id=result["provider_id"],
        oauth_access_token=result.get("access_token"),
        oauth_refresh_token=result.get("refresh_token"),
        oauth_expires_at=result.get("expires_at"),
    )


# ---------- OAuth shared login ----------

async def _oauth_login(
    db: AsyncSession,
    email: str,
    name: str,
    provider: str,
    provider_id: str,
    oauth_access_token: str | None = None,
    oauth_refresh_token: str | None = None,
    oauth_expires_at: datetime | None = None,
) -> dict:
    user = await _get_user_by_email(db, email)
    is_new = False

    if not user:
        is_new = True
        user = User(email=email, provider=provider, provider_id=provider_id, is_verified=True)
        db.add(user)
        await db.flush()
        profile = Profile(user_id=user.id, full_name=name)
        db.add(profile)

        # Start the 15-day Individual free trial for every new account.
        from app.models.platform import Subscription
        from app.services.plans import trial_end_from
        db.add(Subscription(
            user_id=user.id,
            plan="individual",
            status="active",
            current_period_end=trial_end_from(),
        ))

        await db.commit()
        await db.refresh(user)
    else:
        user.is_verified = True
        if user.provider == "email" and not user.provider_id:
            user.provider_id = provider_id

    await _upsert_oauth_token(
        db,
        user,
        provider,
        oauth_access_token,
        oauth_refresh_token,
        oauth_expires_at,
    )

    access_token = create_access_token(str(user.id), user.email)
    refresh_token = create_refresh_token()
    await _store_refresh_token(str(user.id), refresh_token)
    _stamp_login(user)
    await create_notification(
        db,
        str(user.id),
        "success" if is_new else "info",
        "Account created" if is_new else "Signed in",
        f"{'Your account was created' if is_new else 'You signed in'} with {provider.title()}.",
        commit=True,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "is_new_user": is_new}
