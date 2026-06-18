from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.api.v1.deps import get_current_user, get_user_context
from app.services.dashboard import get_bucket, list_buckets, create_bucket, delete_all_buckets, delete_bucket as delete_bucket_service, update_bucket as update_bucket_service
from app.services.team.permissions import UserContext, get_accessible_bucket_ids, require_owner
from app.services.quota import enforce_bucket_quota

router = APIRouter(prefix="/buckets", tags=["buckets"])


class CreateBucketRequest(BaseModel):
    name: str
    description: str | None = None
    color: str = "#3B82F6"
    icon: str = "folder"


class UpdateBucketRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    icon: str | None = None


@router.get("")
async def list_buckets_endpoint(
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    all_buckets = await list_buckets(db, str(ctx.owner_user_id))
    if not ctx.is_member:
        return all_buckets
    accessible = {str(bid) for bid in await get_accessible_bucket_ids(db, ctx.team_member_id)}
    return [b for b in all_buckets if b["id"] in accessible]


@router.post("")
async def create_bucket_endpoint(
    body: CreateBucketRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    await enforce_bucket_quota(db, ctx.owner_user_id)
    return await create_bucket(db, str(ctx.user_id), body.name, body.description, body.color, body.icon)


@router.delete("/all")
async def delete_all_buckets_endpoint(
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    return await delete_all_buckets(db, str(ctx.user_id))


@router.get("/{bucket_id}")
async def get_bucket_endpoint(
    bucket_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    import uuid as _uuid
    if ctx.is_member:
        accessible = await get_accessible_bucket_ids(db, ctx.team_member_id)
        if _uuid.UUID(bucket_id) not in accessible:
            raise HTTPException(status_code=403, detail="You don't have access to this bucket.")
    return await get_bucket(db, str(ctx.owner_user_id), bucket_id)


@router.put("/{bucket_id}")
async def update_bucket(
    bucket_id: str,
    body: UpdateBucketRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    return await update_bucket_service(
        db,
        str(ctx.user_id),
        bucket_id,
        body.name,
        body.description,
        body.color,
        body.icon,
    )


@router.delete("/{bucket_id}")
async def delete_bucket(
    bucket_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    require_owner(ctx)
    return await delete_bucket_service(db, str(ctx.user_id), bucket_id)


@router.get("/{bucket_id}/mcp-url")
async def get_mcp_url():
    pass


@router.post("/{bucket_id}/mcp-url/regenerate")
async def regenerate_mcp_url():
    pass


@router.post("/{bucket_id}/mcp-url/revoke")
async def revoke_mcp_url():
    pass
