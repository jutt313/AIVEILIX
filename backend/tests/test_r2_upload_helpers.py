"""
Unit tests for the R2 presigned-upload helpers, filename sanitization, and the
multipart sizing math, plus finalize_r2_upload's DB-row/status behaviour.

The boto3 client is mocked — these tests never touch the network.
"""
from __future__ import annotations

import math
import uuid
from unittest.mock import AsyncMock, MagicMock

from botocore.exceptions import ClientError

from app.services.storage import r2


# ── filename sanitization ────────────────────────────────────────────────────

def test_safe_filename_strips_path_traversal():
    out = r2.safe_object_filename("../../etc/passwd")
    assert out == "passwd"
    assert "/" not in out and ".." not in out


def test_safe_filename_strips_backslash_paths():
    assert r2.safe_object_filename("a/b\\c.txt") == "c.txt"


def test_safe_filename_strips_control_chars():
    out = r2.safe_object_filename("re\x00port\x1f.pdf")
    assert "\x00" not in out and "\x1f" not in out
    assert out.endswith(".pdf")


def test_safe_filename_empty_falls_back():
    assert r2.safe_object_filename("") == "file"
    assert r2.safe_object_filename("...") == "file"


def test_safe_filename_keeps_readable_names():
    assert r2.safe_object_filename("Q3 Report (final) v2.pdf") == "Q3 Report (final) v2.pdf"


# ── multipart sizing ─────────────────────────────────────────────────────────

def test_compute_part_size_small_uses_default():
    assert r2.compute_part_size(10 * 1024 * 1024) == r2.DEFAULT_PART_SIZE_BYTES


def test_compute_part_size_never_below_minimum():
    assert r2.compute_part_size(1) >= r2.MIN_PART_SIZE_BYTES


def test_compute_part_size_huge_stays_under_max_parts():
    size = 5 * 1024 ** 4  # 5 TiB
    part = r2.compute_part_size(size)
    assert math.ceil(size / part) <= r2.MAX_PARTS
    assert part % (1024 * 1024) == 0  # whole-MiB boundary for clean browser chunking


# ── presigned URLs ───────────────────────────────────────────────────────────

def test_create_presigned_put_url_signs_content_type(monkeypatch):
    client = MagicMock()
    client.generate_presigned_url.return_value = "https://signed-put"
    monkeypatch.setattr(r2, "_get_client", lambda: client)

    url = r2.create_presigned_put_url("raw/x/v1/a.pdf", "application/pdf", 900)
    assert url == "https://signed-put"
    _, kwargs = client.generate_presigned_url.call_args
    assert client.generate_presigned_url.call_args[0][0] == "put_object"
    assert kwargs["Params"]["ContentType"] == "application/pdf"
    assert kwargs["ExpiresIn"] == 900


def test_create_presigned_part_url(monkeypatch):
    client = MagicMock()
    client.generate_presigned_url.return_value = "https://signed-part"
    monkeypatch.setattr(r2, "_get_client", lambda: client)

    url = r2.create_presigned_upload_part_url("k", "up-1", 3, 3600)
    assert url == "https://signed-part"
    _, kwargs = client.generate_presigned_url.call_args
    assert client.generate_presigned_url.call_args[0][0] == "upload_part"
    assert kwargs["Params"]["UploadId"] == "up-1"
    assert kwargs["Params"]["PartNumber"] == 3


# ── multipart lifecycle ──────────────────────────────────────────────────────

def test_create_multipart_returns_upload_id(monkeypatch):
    client = MagicMock()
    client.create_multipart_upload.return_value = {"UploadId": "up-123"}
    monkeypatch.setattr(r2, "_get_client", lambda: client)
    assert r2.create_multipart_upload("k", "application/pdf") == "up-123"


def test_complete_multipart_orders_parts(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(r2, "_get_client", lambda: client)
    r2.complete_multipart_upload(
        "k", "up", [{"PartNumber": 2, "ETag": "b"}, {"PartNumber": 1, "ETag": "a"}]
    )
    _, kwargs = client.complete_multipart_upload.call_args
    nums = [p["PartNumber"] for p in kwargs["MultipartUpload"]["Parts"]]
    assert nums == [1, 2]


def test_abort_multipart_swallows_client_error(monkeypatch):
    client = MagicMock()
    client.abort_multipart_upload.side_effect = ClientError(
        {"Error": {"Code": "NoSuchUpload"}}, "AbortMultipartUpload"
    )
    monkeypatch.setattr(r2, "_get_client", lambda: client)
    # Should not raise — abort is best-effort cleanup.
    r2.abort_multipart_upload("k", "up")


# ── HEAD verification ────────────────────────────────────────────────────────

def test_head_object_missing_returns_none(monkeypatch):
    client = MagicMock()
    client.head_object.side_effect = ClientError({"Error": {"Code": "404"}}, "HeadObject")
    monkeypatch.setattr(r2, "_get_client", lambda: client)
    assert r2.head_object("missing") is None


def test_head_object_returns_size(monkeypatch):
    client = MagicMock()
    client.head_object.return_value = {
        "ContentLength": 123456,
        "ContentType": "application/pdf",
        "ETag": '"abc"',
    }
    monkeypatch.setattr(r2, "_get_client", lambda: client)
    head = r2.head_object("k")
    assert head["size"] == 123456
    assert head["content_type"] == "application/pdf"


# ── finalize_r2_upload ───────────────────────────────────────────────────────

async def test_finalize_r2_upload_creates_processing_file():
    from app.services.pipeline import upload as upload_mod

    db = AsyncMock()
    db.add = MagicMock()  # add() is synchronous on a real Session

    file_id = uuid.uuid4()
    bucket_id = uuid.uuid4()
    user_id = uuid.uuid4()

    file_row, trace_run_id = await upload_mod.finalize_r2_upload(
        db,
        file_id=file_id,
        bucket_id=bucket_id,
        user_id=user_id,
        filename="big.pdf",
        content_type="application/pdf",
        size=999,
        r2_key="raw/x/v1/big.pdf",
    )

    assert file_row.id == file_id
    assert file_row.status == "processing"
    assert file_row.r2_path == "raw/x/v1/big.pdf"
    assert file_row.size == 999
    assert file_row.type == "pdf"
    assert isinstance(trace_run_id, str) and trace_run_id
    db.commit.assert_awaited()
    # files row, file_versions row, and two investigation events were added.
    assert db.add.call_count >= 4
