"""Cloudflare R2 storage service — S3-compatible via boto3."""

import io
import logging
import math
import re
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

_r2_client = None

# ── Multipart policy (encodes S3/R2 constraints) ─────────────────────────────
# Files at/above this size use multipart; smaller files use a single PUT.
MULTIPART_THRESHOLD_BYTES = 100 * 1024 * 1024   # 100 MiB
# Default chunk size for multipart uploads.
DEFAULT_PART_SIZE_BYTES = 16 * 1024 * 1024      # 16 MiB
# S3/R2 require every part except the last to be at least 5 MiB.
MIN_PART_SIZE_BYTES = 5 * 1024 * 1024           # 5 MiB
# S3/R2 allow at most 10,000 parts per multipart upload.
MAX_PARTS = 10_000


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


# ── object-key safety ────────────────────────────────────────────────────────

def safe_object_filename(filename: str) -> str:
    """Sanitize a user-supplied filename for use as the final segment of an R2
    object key. Strips any path components and restricts to a safe charset so a
    crafted name can never escape the ``raw/{file_id}/v{n}/`` prefix."""
    raw = (filename or "").strip().replace("\\", "/")
    base = raw.rsplit("/", 1)[-1]                      # drop any path prefix
    base = re.sub(r"[\x00-\x1f]", "", base)            # strip control chars
    base = re.sub(r"[^A-Za-z0-9._ +()\-]", "_", base)  # safe charset only
    base = base.strip().strip(".")                     # no leading/trailing dots
    base = base[:200] or "file"
    return base


# ── multipart sizing ─────────────────────────────────────────────────────────

def compute_part_size(total_size: int) -> int:
    """Pick a multipart part size that keeps the part count at or below
    ``MAX_PARTS`` while respecting the 5 MiB minimum. Rounds up to whole MiB so
    the browser can chunk on a clean boundary."""
    part = DEFAULT_PART_SIZE_BYTES
    if total_size > part * MAX_PARTS:
        needed = math.ceil(total_size / MAX_PARTS)
        mib = 1024 * 1024
        part = math.ceil(needed / mib) * mib
    return max(part, MIN_PART_SIZE_BYTES)


# ── presigned single PUT ─────────────────────────────────────────────────────

def create_presigned_put_url(r2_key: str, content_type: str, expires_in: int = 900) -> str:
    """Presigned URL for a direct browser ``PUT`` of a whole (small) object.
    The browser must send a matching ``Content-Type`` header."""
    client = _get_client()
    return client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.r2_bucket_name,
            "Key": r2_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )


# ── presigned multipart ──────────────────────────────────────────────────────

def create_multipart_upload(r2_key: str, content_type: str) -> str:
    """Begin a multipart upload; returns the R2 ``UploadId``."""
    client = _get_client()
    resp = client.create_multipart_upload(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
        ContentType=content_type,
    )
    return resp["UploadId"]


def create_presigned_upload_part_url(
    r2_key: str, upload_id: str, part_number: int, expires_in: int = 900
) -> str:
    """Presigned URL for a direct browser ``PUT`` of one multipart part."""
    client = _get_client()
    return client.generate_presigned_url(
        "upload_part",
        Params={
            "Bucket": settings.r2_bucket_name,
            "Key": r2_key,
            "UploadId": upload_id,
            "PartNumber": part_number,
        },
        ExpiresIn=expires_in,
    )


def complete_multipart_upload(r2_key: str, upload_id: str, parts: list[dict]) -> dict:
    """Finalize a multipart upload. ``parts`` is a list of
    ``{"PartNumber": int, "ETag": str}`` — they are sorted by part number here."""
    client = _get_client()
    ordered = sorted(parts, key=lambda p: int(p["PartNumber"]))
    return client.complete_multipart_upload(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
        UploadId=upload_id,
        MultipartUpload={"Parts": ordered},
    )


def abort_multipart_upload(r2_key: str, upload_id: str) -> None:
    """Abort an incomplete multipart upload so R2 drops any stored parts."""
    client = _get_client()
    try:
        client.abort_multipart_upload(
            Bucket=settings.r2_bucket_name,
            Key=r2_key,
            UploadId=upload_id,
        )
        logger.info("R2 multipart abort OK: %s (%s)", r2_key, upload_id)
    except ClientError as exc:
        logger.warning("R2 multipart abort failed for %s: %s", r2_key, exc)


def head_object(r2_key: str) -> dict | None:
    """Return ``{size, content_type, etag}`` for an object, or ``None`` if it
    does not exist. Used to verify a direct upload before any DB row is written."""
    client = _get_client()
    try:
        resp = client.head_object(Bucket=settings.r2_bucket_name, Key=r2_key)
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code in ("404", "NoSuchKey", "NotFound"):
            return None
        raise
    return {
        "size": int(resp.get("ContentLength", 0)),
        "content_type": resp.get("ContentType"),
        "etag": resp.get("ETag"),
    }
