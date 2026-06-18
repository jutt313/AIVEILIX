"""
MCP account-layer data access — operate across the buckets an account token
is permitted to reach.

Permission scope comes from the AccountMcpToken:
  bucket_mode = "all"      -> every bucket the user owns (and future ones)
  bucket_mode = "selected" -> only token.allowed_bucket_ids; buckets created
                              through the token are appended automatically

Functions:
  acct_list_buckets      — buckets in scope
  acct_create_bucket     — create a bucket (added to scope when "selected")
  acct_get_bucket        — one bucket, if in scope
  acct_delete_bucket     — delete a bucket, if in scope
  acct_get_account_info  — account info and usage stats (scoped)
"""

from __future__ import annotations

import logging
import secrets
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.bucket import Bucket
from app.models.file import File
from app.models.mcp_token import AccountMcpToken, BucketMcpToken
from app.models.user import User
from app.services.notifications import create_notification

logger = logging.getLogger(__name__)


def _mcp_base() -> str:
    return getattr(settings, "mcp_base_url", "https://mcp.aiveilix.com").rstrip("/")


def bucket_mcp_url(token: str) -> str:
    """Canonical MCP endpoint URL for a bucket token."""
    return f"{_mcp_base()}/v1/mcp/bucket/{token}"


def account_mcp_url(token: str) -> str:
    """Canonical MCP endpoint URL for an account token."""
    return f"{_mcp_base()}/v1/mcp/account/{token}"


# ── scope helpers ─────────────────────────────────────────────────────────────

def _scope(token: AccountMcpToken) -> set[uuid.UUID] | None:
    """Allowed bucket id set, or None when the token can reach every bucket."""
    if token.bucket_mode == "all":
        return None
    return {b if isinstance(b, uuid.UUID) else uuid.UUID(str(b)) for b in (token.allowed_bucket_ids or [])}


def _in_scope(token: AccountMcpToken, bucket_id: uuid.UUID) -> bool:
    scope = _scope(token)
    return scope is None or bucket_id in scope


async def _bucket_stats(db: AsyncSession, bucket_id: uuid.UUID) -> tuple[int, int]:
    """Returns (files_count, storage_used) for ready files of a bucket."""
    files_count = (
        await db.execute(
            select(func.count()).where(File.bucket_id == bucket_id, File.status == "ready")
        )
    ).scalar_one()
    storage_used = (
        await db.execute(
            select(func.coalesce(func.sum(File.size), 0)).where(
                File.bucket_id == bucket_id, File.status == "ready"
            )
        )
    ).scalar_one()
    return files_count, int(storage_used or 0)


async def _first_token_url(db: AsyncSession, bucket_id: uuid.UUID) -> str | None:
    """First active bucket-MCP token URL for a bucket, if one exists."""
    token = (
        await db.execute(
            select(BucketMcpToken.token)
            .where(BucketMcpToken.bucket_id == bucket_id, BucketMcpToken.is_active.is_(True))
            .order_by(BucketMcpToken.created_at.asc())
            .limit(1)
        )
    ).scalar_one_or_none()
    return bucket_mcp_url(token) if token else None


# ── list_buckets ──────────────────────────────────────────────────────────────

async def acct_list_buckets(db: AsyncSession, token: AccountMcpToken) -> dict:
    scope = _scope(token)
    if scope is not None and not scope:
        return {"buckets": [], "total": 0}

    query = select(Bucket).where(Bucket.user_id == token.user_id)
    if scope is not None:
        query = query.where(Bucket.id.in_(scope))
    buckets = (await db.execute(query.order_by(Bucket.created_at.desc()))).scalars().all()

    out = []
    for b in buckets:
        files_count, storage_used = await _bucket_stats(db, b.id)
        out.append({
            "bucket_id": str(b.id),
            "name": b.name,
            "description": b.description or "",
            "color": b.color,
            "files_count": files_count,
            "storage_used": storage_used,
            "mcp_url": await _first_token_url(db, b.id),
            "created_at": b.created_at.isoformat(),
        })
    return {"buckets": out, "total": len(out)}


# ── create_bucket ─────────────────────────────────────────────────────────────

async def acct_create_bucket(
    db: AsyncSession,
    token: AccountMcpToken,
    name: str,
    description: str | None = None,
    color: str = "#3B82F6",
) -> dict:
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Bucket name is required.")

    bucket = Bucket(
        user_id=token.user_id,
        name=name.strip(),
        description=description,
        color=color or "#3B82F6",
        icon="folder",
        mcp_token=secrets.token_urlsafe(32),
    )
    db.add(bucket)
    try:
        await db.flush()
        await create_notification(
            db,
            str(token.user_id),
            "success",
            "Bucket created",
            f'Bucket "{bucket.name}" was created via MCP.',
        )
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        if "buckets_name_per_user_unique" in str(getattr(exc, "orig", exc)):
            raise HTTPException(status_code=409, detail="A bucket with this name already exists.") from exc
        raise
    await db.refresh(bucket)

    # A "selected"-scope token gains access to buckets it creates itself.
    if token.bucket_mode == "selected":
        token.allowed_bucket_ids = list(token.allowed_bucket_ids or []) + [bucket.id]
        await db.commit()

    return {
        "bucket_id": str(bucket.id),
        "name": bucket.name,
        "description": bucket.description or "",
        "color": bucket.color,
        "created_at": bucket.created_at.isoformat(),
    }


# ── get_bucket ────────────────────────────────────────────────────────────────

async def acct_get_bucket(db: AsyncSession, token: AccountMcpToken, bucket_id: uuid.UUID) -> dict | None:
    if not _in_scope(token, bucket_id):
        return None
    bucket = (
        await db.execute(
            select(Bucket).where(Bucket.id == bucket_id, Bucket.user_id == token.user_id)
        )
    ).scalar_one_or_none()
    if bucket is None:
        return None
    files_count, storage_used = await _bucket_stats(db, bucket.id)
    return {
        "bucket_id": str(bucket.id),
        "name": bucket.name,
        "description": bucket.description or "",
        "color": bucket.color,
        "files_count": files_count,
        "storage_used": storage_used,
        "mcp_url": await _first_token_url(db, bucket.id),
        "created_at": bucket.created_at.isoformat(),
    }


# ── delete_bucket ─────────────────────────────────────────────────────────────

async def acct_delete_bucket(db: AsyncSession, token: AccountMcpToken, bucket_id: uuid.UUID) -> dict | None:
    if not _in_scope(token, bucket_id):
        return None
    bucket = (
        await db.execute(
            select(Bucket).where(Bucket.id == bucket_id, Bucket.user_id == token.user_id)
        )
    ).scalar_one_or_none()
    if bucket is None:
        return None
    bucket_name = bucket.name
    await db.delete(bucket)
    await create_notification(
        db,
        str(token.user_id),
        "warning",
        "Bucket deleted",
        f'Bucket "{bucket_name}" was deleted via MCP.',
    )

    if token.bucket_mode == "selected":
        token.allowed_bucket_ids = [
            b for b in (token.allowed_bucket_ids or [])
            if str(b) != str(bucket_id)
        ]

    await db.commit()
    return {"success": True, "message": f'Bucket "{bucket_name}" deleted successfully.'}


# ── get_account_info ──────────────────────────────────────────────────────────

async def acct_get_account_info(db: AsyncSession, token: AccountMcpToken) -> dict | None:
    user = (
        await db.execute(select(User).where(User.id == token.user_id))
    ).scalar_one_or_none()
    if user is None:
        return None

    scope = _scope(token)
    bucket_filter = [Bucket.user_id == token.user_id]
    file_filter = [File.user_id == token.user_id, File.status == "ready"]
    if scope is not None:
        if not scope:
            return {
                "user_id": str(user.id),
                "email": user.email,
                "buckets_count": 0,
                "files_count": 0,
                "storage_used": 0,
                "scope": "selected",
                "created_at": user.created_at.isoformat(),
            }
        bucket_filter.append(Bucket.id.in_(scope))
        file_filter.append(File.bucket_id.in_(scope))

    buckets_count = (await db.execute(select(func.count()).where(*bucket_filter))).scalar_one()
    files_count = (await db.execute(select(func.count()).where(*file_filter))).scalar_one()
    storage_used = (
        await db.execute(select(func.coalesce(func.sum(File.size), 0)).where(*file_filter))
    ).scalar_one()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "buckets_count": buckets_count,
        "files_count": files_count,
        "storage_used": int(storage_used or 0),
        "scope": "all" if scope is None else "selected",
        "created_at": user.created_at.isoformat(),
    }
