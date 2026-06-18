"""
Unit tests for the direct-to-R2 upload-start enforcement.

Locks in that plan/quota are checked BEFORE any R2 presigning happens:
  - a file larger than the plan's per-file cap is rejected (and rejected before
    we even count documents/storage)
  - storage quota is enforced
  - document count is enforced
  - a locked account is blocked
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.services import quota
from app.services.plans import LOCKED_LIMITS, PLAN_LIMITS, EffectivePlan

OWNER = uuid.uuid4()


def _ep(plan_key: str = "individual", *, locked: bool = False) -> EffectivePlan:
    limits = LOCKED_LIMITS if locked else PLAN_LIMITS[plan_key]
    return EffectivePlan(
        plan="locked" if locked else plan_key,
        limits=limits,
        is_trial=False,
        trial_ends_at=None,
        locked=locked,
    )


@pytest.fixture
def quota_db(monkeypatch):
    """Patch owner_effective_plan and hand back a fake db whose scalar() returns
    the supplied document count then storage-used (the two reads quota does)."""
    def _setup(ep: EffectivePlan, *, docs: int = 0, used: int = 0):
        async def fake_owner_effective_plan(db, owner):  # noqa: ANN001
            return ep
        monkeypatch.setattr(quota, "owner_effective_plan", fake_owner_effective_plan)
        db = AsyncMock()
        db.scalar = AsyncMock(side_effect=[docs, used])
        return db
    return _setup


async def test_oversize_file_blocked_before_counting(quota_db):
    db = quota_db(_ep("individual"))
    too_big = PLAN_LIMITS["individual"].max_file_size_bytes + 1
    with pytest.raises(HTTPException) as ei:
        await quota.enforce_upload_quota(
            db, OWNER, incoming_files=1, incoming_bytes=too_big, single_file_bytes=too_big
        )
    assert ei.value.status_code == 402
    assert "per-file" in ei.value.detail
    # Rejected before any COUNT/SUM query — no signing work wasted.
    db.scalar.assert_not_called()


async def test_storage_quota_blocked(quota_db):
    lim = PLAN_LIMITS["individual"]
    db = quota_db(_ep("individual"), docs=0, used=lim.max_storage_bytes)
    with pytest.raises(HTTPException) as ei:
        await quota.enforce_upload_quota(
            db, OWNER, incoming_files=1, incoming_bytes=4096, single_file_bytes=4096
        )
    assert ei.value.status_code == 402


async def test_document_count_blocked(quota_db):
    lim = PLAN_LIMITS["individual"]
    db = quota_db(_ep("individual"), docs=lim.max_documents, used=0)
    with pytest.raises(HTTPException) as ei:
        await quota.enforce_upload_quota(
            db, OWNER, incoming_files=1, incoming_bytes=10, single_file_bytes=10
        )
    assert ei.value.status_code == 402


async def test_within_limits_passes(quota_db):
    db = quota_db(_ep("individual"), docs=0, used=0)
    size = 10 * 1024 * 1024  # 10 MiB — under the 100 MB individual cap
    ep = await quota.enforce_upload_quota(
        db, OWNER, incoming_files=1, incoming_bytes=size, single_file_bytes=size
    )
    assert ep.limits.name == "Individual"


async def test_locked_account_blocked(quota_db):
    db = quota_db(_ep(locked=True))
    with pytest.raises(HTTPException) as ei:
        await quota.enforce_upload_quota(
            db, OWNER, incoming_files=1, incoming_bytes=1, single_file_bytes=1
        )
    assert ei.value.status_code == 402
    db.scalar.assert_not_called()


async def test_enterprise_cap_is_larger(quota_db):
    # A 1 GB file is rejected on Individual but fine on Enterprise (business).
    one_gb = 1024 ** 3
    assert one_gb > PLAN_LIMITS["individual"].max_file_size_bytes
    assert one_gb < PLAN_LIMITS["business"].max_file_size_bytes
    db = quota_db(_ep("business"), docs=0, used=0)
    ep = await quota.enforce_upload_quota(
        db, OWNER, incoming_files=1, incoming_bytes=one_gb, single_file_bytes=one_gb
    )
    assert ep.plan == "business"
