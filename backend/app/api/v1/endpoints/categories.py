from fastapi import APIRouter

router = APIRouter(prefix="/buckets", tags=["categories"])


@router.get("/{bucket_id}/categories")
async def list_categories():
    pass


@router.post("/{bucket_id}/categories")
async def create_category():
    pass


@router.delete("/{bucket_id}/categories/{category_id}")
async def delete_category():
    pass
