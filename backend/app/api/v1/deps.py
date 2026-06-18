import uuid

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.config import settings
from app.core.security import decode_token_safe
from app.database import db_session, get_db
from app.models.user import User
from app.services.team.permissions import UserContext, resolve_user_context
from app.valkey import get_valkey

security = HTTPBearer()

# How often a user's last_seen_at is written to the DB (presence heartbeat).
# Bounds writes to at most one per user per window, keeping the hot auth path cheap.
SEEN_THROTTLE_SECONDS = 60


async def _touch_last_seen(user_id: str) -> None:
    """Best-effort presence heartbeat. Throttled via Valkey, fully isolated from
    the request transaction, and fail-open so it can never break authentication."""
    try:
        v = get_valkey()
        if await v.get(f"seen:{user_id}"):
            return
        await v.set(f"seen:{user_id}", "1", ex=SEEN_THROTTLE_SECONDS)
    except Exception:
        # Valkey unavailable — fall through and still record presence.
        pass
    try:
        async with db_session() as db:
            await db.execute(
                update(User).where(User.id == uuid.UUID(user_id)).values(last_seen_at=func.now())
            )
            await db.commit()
    except Exception:
        pass


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_token_safe(token)

    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    jti = payload.get("jti")
    if jti:
        v = get_valkey()
        blacklisted = await v.get(f"blacklist:{jti}")
        if blacklisted:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked.")

    user_id = payload.get("user_id")
    if user_id:
        await _touch_last_seen(user_id)

    return payload


async def get_user_context(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserContext:
    return await resolve_user_context(db, uuid.UUID(current_user["user_id"]))


def _is_admin_user(user: User | None) -> bool:
    allow = {e.strip().lower() for e in (settings.admin_emails or "").split(",") if e.strip()}
    return user is not None and (bool(user.is_admin) or (user.email or "").lower() in allow)


async def require_admin(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> User:
    """Base admin gate: an authenticated user who is an admin (is_admin flag or ADMIN_EMAILS)."""
    user = await db.get(User, uuid.UUID(current_user["user_id"]))
    if not _is_admin_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access denied.")
    return user


async def require_admin_session(
    x_admin_session: str | None = Header(default=None, alias="X-Admin-Session"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> User:
    """
    Stricter gate for sensitive admin actions (lookup / set-plan): an admin who
    has ALSO verified the 6-digit code, proven by a short-lived admin session
    token stored in Valkey.
    """
    user = await db.get(User, uuid.UUID(current_user["user_id"]))
    if not _is_admin_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access denied.")
    if not x_admin_session:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verify your admin code first.")
    owner = await get_valkey().get(f"admin:session:{x_admin_session}")
    if not owner or owner != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin session expired — verify your code again.")
    return user
