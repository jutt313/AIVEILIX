import base64
import uuid
from zoneinfo import ZoneInfo

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.config import settings
from app.core.security import hash_password, verify_password
from app.models.user import OAuthToken, Profile, User
from app.services.auth import exchange_github_oauth, exchange_google_oauth, get_oauth_authorize_url
from app.services.notifications import create_notification
from app.services.storage.r2 import upload_file

MAX_AVATAR_BYTES = 2 * 1024 * 1024


async def _get_user(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()


async def _get_profile_row(db: AsyncSession, user_id: str) -> Profile | None:
    result = await db.execute(select(Profile).where(Profile.user_id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()


async def _ensure_profile(db: AsyncSession, user_id: str, email: str) -> Profile:
    profile = await _get_profile_row(db, user_id)
    if profile:
        return profile

    profile = Profile(user_id=uuid.UUID(user_id), full_name=email.split("@")[0] or "User")
    db.add(profile)
    await db.flush()
    return profile


async def _connected_provider_set(db: AsyncSession, user: User) -> set[str]:
    connected: set[str] = set()
    if user.provider in {"google", "github"}:
        connected.add(user.provider)

    token_rows = await db.execute(
        select(OAuthToken.provider).where(OAuthToken.user_id == user.id)
    )
    connected.update(token_rows.scalars().all())
    return connected


async def get_profile(db: AsyncSession, user_id: str) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = await _ensure_profile(db, user_id, user.email)
    connected_providers = await _connected_provider_set(db, user)
    await db.commit()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "full_name": profile.full_name or "User",
        "avatar_url": profile.avatar_url,
        "bio": profile.bio,
        "theme": profile.theme,
        "language": profile.language,
        "timezone": profile.timezone,
        "two_factor_enabled": user.two_factor_enabled,
        "auth_provider": user.provider,
        "auth_provider_label": user.provider.title() if user.provider != "email" else "Email",
        "has_password": bool(user.password_hash),
        "can_disconnect_provider": user.provider in {"google", "github"} and bool(user.password_hash),
        "connected_providers": sorted(connected_providers),
        "google_connected": "google" in connected_providers,
        "github_connected": "github" in connected_providers,
        "google_available": bool(settings.google_client_id and settings.google_client_id != "your-google-client-id"),
        "github_available": bool(settings.github_client_id and settings.github_client_id != "your-github-client-id"),
    }


async def update_profile(
    db: AsyncSession,
    user_id: str,
    full_name: str,
    bio: str | None,
    theme: str,
    language: str,
    timezone: str,
) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if theme not in {"light", "dark"}:
        raise HTTPException(status_code=400, detail="Invalid theme.")
    try:
        ZoneInfo(timezone)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid timezone.") from exc

    profile = await _ensure_profile(db, user_id, user.email)
    profile.full_name = (full_name or "").strip() or "User"
    profile.bio = (bio or "").strip() or None
    profile.theme = theme
    profile.language = (language or "").strip() or "en"
    profile.timezone = timezone
    await create_notification(
        db,
        user_id,
        "info",
        "Profile updated",
        "Your profile settings were updated successfully.",
    )
    await db.commit()
    return {"message": "Profile updated successfully."}


async def upload_avatar(db: AsyncSession, user_id: str, file: UploadFile) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Avatar file is empty.")
    if len(raw) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=400, detail="Avatar must be 2MB or smaller.")

    profile = await _ensure_profile(db, user_id, user.email)

    if settings.r2_account_id and settings.r2_access_key_id and settings.r2_secret_access_key and settings.r2_public_url:
        key = f"avatars/{user_id}/{uuid.uuid4().hex}"
        upload_file(raw, key, file.content_type)
        avatar_url = f"{settings.r2_public_url.rstrip('/')}/{key}"
    else:
        avatar_url = f"data:{file.content_type};base64,{base64.b64encode(raw).decode('ascii')}"

    profile.avatar_url = avatar_url
    await create_notification(
        db,
        user_id,
        "success",
        "Avatar updated",
        "Your profile picture was updated successfully.",
    )
    await db.commit()
    return {"avatar_url": avatar_url}


async def change_password(db: AsyncSession, user_id: str, current_password: str, new_password: str) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.password_hash and not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters.")

    is_first_password = not bool(user.password_hash)
    user.password_hash = hash_password(new_password)
    await create_notification(
        db,
        user_id,
        "success",
        "Password created" if is_first_password else "Password changed",
        "A password login was added to your account." if is_first_password else "Your account password was changed successfully.",
    )
    await db.commit()
    return {"message": "Password set successfully." if is_first_password else "Password changed successfully."}


async def get_auth_provider_connect_url(provider: str, redirect_uri: str) -> dict:
    return get_oauth_authorize_url(provider, redirect_uri, mode="connect")


async def connect_auth_provider(db: AsyncSession, user_id: str, provider: str, code: str, redirect_uri: str) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if provider not in {"google", "github"}:
        raise HTTPException(status_code=400, detail="Unsupported auth provider.")

    result = await (exchange_google_oauth(code, redirect_uri) if provider == "google" else exchange_github_oauth(code, redirect_uri))
    if result["email"].lower() != user.email.lower():
        raise HTTPException(
            status_code=400,
            detail=f"This {provider.title()} account uses a different email address than your current profile.",
        )

    already_linked = provider in await _connected_provider_set(db, user)
    existing = await db.execute(
        select(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == provider,
        )
    )
    token_row = existing.scalar_one_or_none()
    if token_row:
        token_row.access_token = result.get("access_token")
        token_row.refresh_token = result.get("refresh_token")
        token_row.expires_at = result.get("expires_at")
    else:
        db.add(OAuthToken(
            user_id=user.id,
            provider=provider,
            access_token=result.get("access_token"),
            refresh_token=result.get("refresh_token"),
            expires_at=result.get("expires_at"),
        ))

    if user.provider == provider:
        user.provider_id = result["provider_id"]

    await create_notification(
        db,
        user_id,
        "success",
        f"{provider.title()} connected",
        f"Your {provider.title()} sign-in connection is now linked to this account.",
    )
    await db.commit()
    return {
        "message": f"{provider.title()} connected successfully." if not already_linked else f"{provider.title()} connection refreshed successfully.",
        "connected_providers": sorted(await _connected_provider_set(db, user)),
    }


async def disconnect_auth_provider(db: AsyncSession, user_id: str, provider: str | None = None) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    connected_providers = await _connected_provider_set(db, user)
    target_provider = provider or user.provider
    if target_provider not in {"google", "github"} or target_provider not in connected_providers:
        raise HTTPException(status_code=400, detail="No social sign-in provider is connected.")
    if user.provider == target_provider and not user.password_hash:
        raise HTTPException(status_code=400, detail="Set a password before disconnecting this provider.")

    provider_label = target_provider.title()
    if user.provider == target_provider:
        user.provider = "email"
        user.provider_id = None
    await db.execute(
        delete(OAuthToken).where(
            OAuthToken.user_id == user.id,
            OAuthToken.provider == target_provider,
        )
    )
    await create_notification(
        db,
        user_id,
        "warning",
        f"{provider_label} disconnected",
        f"Your {provider_label} sign-in connection was removed from this account.",
    )
    await db.commit()
    return {
        "message": f"{provider_label} disconnected successfully.",
        "auth_provider": user.provider,
        "connected_providers": sorted(await _connected_provider_set(db, user)),
    }


async def delete_account(db: AsyncSession, user_id: str, password: str) -> dict:
    user = await _get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.password_hash and not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Password confirmation failed.")

    await db.delete(user)
    await db.commit()
    return {"message": "Account deleted successfully."}


async def save_onboarding(db: AsyncSession, user_id: str, use_case: str, need: str, referral_source: str):
    result = await db.execute(select(Profile).where(Profile.user_id == uuid.UUID(user_id)))
    profile = result.scalar_one_or_none()
    if not profile:
        return

    profile.use_case = use_case
    profile.bio = need
    profile.referral_source = referral_source
    await create_notification(
        db,
        user_id,
        "success",
        "Onboarding completed",
        "Your onboarding details were saved successfully.",
    )
    await db.commit()
