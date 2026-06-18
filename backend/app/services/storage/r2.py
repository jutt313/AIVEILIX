"""Cloudflare R2 storage service — S3-compatible via boto3."""

import io
import logging
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

_r2_client = None


def _get_client():
    global _r2_client
    if _r2_client is None:
        _r2_client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto",
        )
    return _r2_client


def upload_file(file_data: bytes | BinaryIO, r2_key: str, content_type: str = "application/octet-stream") -> str:
    """Upload bytes or file-like object to R2. Returns the r2_key."""
    client = _get_client()
    if isinstance(file_data, bytes):
        file_data = io.BytesIO(file_data)
    client.upload_fileobj(
        file_data,
        settings.r2_bucket_name,
        r2_key,
        ExtraArgs={"ContentType": content_type},
    )
    logger.info("R2 upload OK: %s", r2_key)
    return r2_key


def download_file(r2_key: str) -> bytes:
    """Download a file from R2 and return raw bytes."""
    client = _get_client()
    buf = io.BytesIO()
    client.download_fileobj(settings.r2_bucket_name, r2_key, buf)
    buf.seek(0)
    return buf.read()


def upload_json(data: str | bytes, r2_key: str) -> str:
    """Upload a JSON document to R2. Returns the r2_key."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return upload_file(data, r2_key, content_type="application/json")


def delete_file(r2_key: str) -> None:
    """Delete a file from R2."""
    client = _get_client()
    try:
        client.delete_object(Bucket=settings.r2_bucket_name, Key=r2_key)
        logger.info("R2 delete OK: %s", r2_key)
    except ClientError as exc:
        logger.warning("R2 delete failed for %s: %s", r2_key, exc)


def get_presigned_url(r2_key: str, expires_in: int = 3600) -> str:
    """Generate a presigned download URL valid for expires_in seconds."""
    client = _get_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.r2_bucket_name, "Key": r2_key},
        ExpiresIn=expires_in,
    )


def build_raw_key(file_id: str, filename: str, version: int | None = None) -> str:
    if version is not None:
        return f"raw/{file_id}/v{version}/{filename}"
    return f"raw/{file_id}/{filename}"


def build_layout_key(file_id: str) -> str:
    return f"layouts/{file_id}/layout.json"
