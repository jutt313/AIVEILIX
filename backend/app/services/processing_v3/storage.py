"""
R2 storage adapter for pipeline v3.

Ported from Aiveilix-pipline app/adapters/storage.py. Returns r2:// URIs for
artifacts referenced inside the export JSON (page screenshots, visual crops).
Raw-file download and layout-JSON upload use the backend's plain-key r2.py.
"""

import asyncio
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class R2StorageAdapter:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto",
        )

    def _upload(self, data: bytes, key: str) -> None:
        self._client.put_object(Bucket=settings.r2_bucket_name, Key=key, Body=data)

    async def _put(self, data: bytes, key: str, kind: str) -> str:
        try:
            await asyncio.to_thread(self._upload, data, key)
        except (BotoCoreError, ClientError) as exc:
            logger.exception("r2_upload_failed kind=%s key=%s", kind, key)
            raise RuntimeError(f"R2 upload failed ({kind}): {exc}") from exc
        return f"r2://{settings.r2_bucket_name}/{key}"

    async def upload_page_screenshot(self, data: bytes, doc_id: str, page_number: int) -> str:
        return await self._put(data, f"pages/{doc_id}/page_{page_number}.png", "page_screenshot")

    async def upload_page_asset(self, data: bytes, doc_id: str, page_number: int, asset_name: str) -> str:
        return await self._put(data, f"page-assets/{doc_id}/page_{page_number}/{asset_name}", "page_asset")

    async def upload_ocr_json(self, data: bytes, doc_id: str, page_number: int) -> str:
        return await self._put(data, f"ocr/{doc_id}/page_{page_number}.json", "ocr_json")


def get_storage_adapter() -> R2StorageAdapter:
    if not all([settings.r2_account_id, settings.r2_access_key_id, settings.r2_secret_access_key, settings.r2_bucket_name]):
        raise RuntimeError("Storage not configured — set R2 credentials in .env")
    return R2StorageAdapter()
