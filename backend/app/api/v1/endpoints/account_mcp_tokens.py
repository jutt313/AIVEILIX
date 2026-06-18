"""
Account MCP Token Management — CRUD for account-level MCP tokens.

An account MCP token exposes the 5 account tools (list/create/get/delete bucket,
account info) over one MCP URL. Each token carries a bucket-permission scope:

  bucket_mode = "all"      -> reaches every bucket the user owns
  bucket_mode = "selected" -> reaches only allowed_bucket_ids; buckets created
                              through the token are added to that list

Endpoints (all user-scoped):
  GET    /user/account-mcp-tokens             list tokens + the user's buckets
  POST   /user/account-mcp-tokens             create a token
  PATCH  /user/account-mcp-tokens/{token_id}  update name / scope / active
  DELETE /user/account-mcp-tokens/{token_id}  delete a token
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_context
from app.database import get_db
from app.models.bucket import Bucket
from app.models.mcp_token import AccountMcpToken
from app.services.mcp.account_tools import account_mcp_url
from app.services.team.permissions import UserContext, require_owner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/account-mcp-tokens", tags=["account-mcp-tokens"])

MAX_TOKENS_PER_USER = 10
VALID_MODES = {"all", "selected"}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _user_bucket_ids(db: AsyncSession, user_id: uuid.UUID) -> set[uuid.UUID]:
    rows = (await db.execute(select(Bucket.id).where(Bucket.user_id == user_id))).scalars().all()
    return set(rows)


async def _get_token(db: AsyncSession, user_id: uuid.UUID, token_id: str) -> AccountMcpToken:
    try:
        tid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token id.")
    token = (
        await db.execute(
            select(AccountMcpToken).where(
                AccountMcpToken.id == tid, AccountMcpToken.user_id == user_id
            )
        )
    ).scalar_one_or_none()
    if token is None:
        raise HTTPException(status_code=404, detail="Account MCP token not found.")
    return token


def _token_response(token: AccountMcpToken) -> dict:
    return {
        "id": str(token.id),
        "name": token.name,
        "token": token.token,
        "account_mcp_url": account_mcp_url(token.token),
        "is_active": token.is_active,
        "bucket_mode": token.bucket_mode,
        "allowed_bucket_ids": [str(b) for b in (token.allowed_bucket_ids or [])],
        "created_at": token.created_at.isoformat(),
        "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
    }


def _normalize_scope(
    bucket_mode: str,
    allowed_bucket_ids: list[str] | None,
    owned: set[uuid.UUID],
) -> tuple[str, list[uuid.UUID]]:
    if bucket_mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail="bucket_mode must be 'all' or 'selected'.")
    if bucket_mode == "all":
        return "all", []
    ids: list[uuid.UUID] = []
    for raw in allowed_bucket_ids or []:
        try:
            bid = uuid.UUID(str(raw))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid bucket id: {raw}")
        if bid not in owned:
            raise HTTPException(status_code=400, detail="One or more buckets do not belong to you.")
        if bid not in ids:
            ids.append(bid)
    return "selected", ids


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateAccountTokenRequest(BaseModel):
    name: str = "Account MCP"
    bucket_mode: str = "all"
    allowed_bucket_ids: list[str] = []


class UpdateAccountTokenRequest(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    bucket_mode: str | None = None
    allowed_bucket_ids: list[str] | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
async def list_account_tokens(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    user_id = uuid.UUID(str(current_user["user_id"]))
    tokens = (
        await db.execute(
            select(AccountMcpToken)
            .where(AccountMcpToken.user_id == user_id)
            .order_by(AccountMcpToken.created_at.asc())
        )
    ).scalars().all()
    buckets = (
        await db.execute(
            select(Bucket).where(Bucket.user_id == user_id).order_by(Bucket.created_at.desc())
        )
    ).scalars().all()
    return {
        "tokens": [_token_response(t) for t in tokens],
        "total": len(tokens),
        "max": MAX_TOKENS_PER_USER,
        "buckets": [
            {"id": str(b.id), "name": b.name, "color": b.color}
            for b in buckets
        ],
    }


@router.post("")
async def create_account_token(
    body: CreateAccountTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    user_id = uuid.UUID(str(current_user["user_id"]))

    count = (
        await db.execute(
            select(func.count()).where(AccountMcpToken.user_id == user_id)
        )
    ).scalar_one()
    if count >= MAX_TOKENS_PER_USER:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_TOKENS_PER_USER} account MCP tokens.")

    owned = await _user_bucket_ids(db, user_id)
    mode, ids = _normalize_scope(body.bucket_mode, body.allowed_bucket_ids, owned)

    token = AccountMcpToken(
        user_id=user_id,
        name=body.name.strip() or "Account MCP",
        bucket_mode=mode,
        allowed_bucket_ids=ids,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    logger.info("Account MCP token created: user=%s token=%s mode=%s", user_id, token.id, mode)
    return _token_response(token)


@router.patch("/{token_id}")
async def update_account_token(
    token_id: str,
    body: UpdateAccountTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    user_id = uuid.UUID(str(current_user["user_id"]))
    token = await _get_token(db, user_id, token_id)

    if body.name is not None:
        token.name = body.name.strip() or token.name
    if body.is_active is not None:
        token.is_active = body.is_active

    if body.bucket_mode is not None or body.allowed_bucket_ids is not None:
        owned = await _user_bucket_ids(db, user_id)
        mode = body.bucket_mode if body.bucket_mode is not None else token.bucket_mode
        raw_ids = (
            body.allowed_bucket_ids
            if body.allowed_bucket_ids is not None
            else [str(b) for b in (token.allowed_bucket_ids or [])]
        )
        token.bucket_mode, token.allowed_bucket_ids = _normalize_scope(mode, raw_ids, owned)

    await db.commit()
    await db.refresh(token)
    logger.info("Account MCP token updated: token=%s", token_id)
    return _token_response(token)


@router.delete("/{token_id}")
async def delete_account_token(
    token_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    user_id = uuid.UUID(str(current_user["user_id"]))
    token = await _get_token(db, user_id, token_id)
    await db.delete(token)
    await db.commit()
    logger.info("Account MCP token deleted: token=%s", token_id)
    return {"message": "Account MCP token deleted.", "token_id": token_id}
