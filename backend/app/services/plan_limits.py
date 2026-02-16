"""
Plan limits enforcement service
"""
import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from app.config import get_settings
from app.services.supabase import get_supabase

settings = get_settings()
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Plan limits configuration (all tiers)
# ──────────────────────────────────────────────────────────────
PLAN_LIMITS = {
    "free_trial": {
        "storage_bytes": 1 * 1024 * 1024 * 1024,          # 1GB
        "max_file_size_bytes": 50 * 1024 * 1024,           # 50MB
        "max_images_per_file": 3,
        "files_per_upload_batch": 10,
        "max_batch_size_bytes": 250 * 1024 * 1024,         # 250MB
        "max_buckets": 5,
        "max_team_members": 0,
        "chat_messages_per_day": 50,
        "mcp_queries_per_day": 50,
        "mcp_queries_per_min": 5,
        "bucket_chat_per_day": 100,
        "bucket_chat_per_hour": 20,
        "active_conversations_per_bucket": 20,
        "concurrent_processing_jobs": 1,
        "max_documents": -1,                                # Unlimited
        "api_calls_per_day": 50,
    },
    "starter": {
        "storage_bytes": 5 * 1024 * 1024 * 1024,           # 5GB
        "max_file_size_bytes": 100 * 1024 * 1024,          # 100MB
        "max_images_per_file": 20,
        "files_per_upload_batch": 20,
        "max_batch_size_bytes": 1 * 1024 * 1024 * 1024,    # 1GB
        "max_buckets": 25,
        "max_team_members": 3,
        "chat_messages_per_day": 200,
        "mcp_queries_per_day": 300,
        "mcp_queries_per_min": 20,
        "bucket_chat_per_day": 500,
        "bucket_chat_per_hour": 100,
        "active_conversations_per_bucket": 100,
        "concurrent_processing_jobs": 2,
        "max_documents": -1,
        "api_calls_per_day": 300,
    },
    "pro": {
        "storage_bytes": 12 * 1024 * 1024 * 1024,          # 12GB
        "max_file_size_bytes": 250 * 1024 * 1024,          # 250MB
        "max_images_per_file": 100,
        "files_per_upload_batch": 50,
        "max_batch_size_bytes": 3 * 1024 * 1024 * 1024,    # 3GB
        "max_buckets": 100,
        "max_team_members": 10,
        "chat_messages_per_day": 1000,
        "mcp_queries_per_day": 1500,
        "mcp_queries_per_min": 60,
        "bucket_chat_per_day": 2000,
        "bucket_chat_per_hour": 300,
        "active_conversations_per_bucket": 500,
        "concurrent_processing_jobs": 5,
        "max_documents": -1,
        "api_calls_per_day": 1500,
    },
    "premium": {
        "storage_bytes": 25 * 1024 * 1024 * 1024,          # 25GB
        "max_file_size_bytes": 500 * 1024 * 1024,          # 500MB
        "max_images_per_file": 300,
        "files_per_upload_batch": 100,
        "max_batch_size_bytes": 10 * 1024 * 1024 * 1024,   # 10GB
        "max_buckets": -1,                                   # Unlimited
        "max_team_members": 30,
        "chat_messages_per_day": 5000,
        "mcp_queries_per_day": 5000,
        "mcp_queries_per_min": 120,
        "bucket_chat_per_day": 7000,
        "bucket_chat_per_hour": 1000,
        "active_conversations_per_bucket": -1,               # Unlimited
        "concurrent_processing_jobs": 10,
        "max_documents": -1,
        "api_calls_per_day": 5000,
    },
}

# Next plan recommendations for upgrade prompts
NEXT_PLAN = {
    "free_trial": "starter",
    "starter": "pro",
    "pro": "premium",
    "premium": None,
    "expired": "starter",
}

PLAN_NAMES = {
    "free_trial": "Free Trial",
    "starter": "Starter",
    "pro": "Pro",
    "premium": "Premium",
}

# ──────────────────────────────────────────────────────────────
# Expired plan returns all zeros
# ──────────────────────────────────────────────────────────────
EXPIRED_LIMITS = {k: 0 for k in PLAN_LIMITS["free_trial"]}


def _build_upgrade_detail(error_type: str, message: str, plan: str) -> dict:
    """Build standardised upgrade error payload."""
    next_plan = NEXT_PLAN.get(plan)
    next_limits = PLAN_LIMITS.get(next_plan, {}) if next_plan else {}
    return {
        "error": error_type,
        "message": message,
        "upgrade_required": True,
        "current_plan": plan,
        "current_plan_name": PLAN_NAMES.get(plan, plan),
        "next_plan": next_plan,
        "next_plan_name": PLAN_NAMES.get(next_plan, ""),
        "next_plan_limits": next_limits,
    }


# ──────────────────────────────────────────────────────────────
# 24-hour early-bird bonus helpers
# ──────────────────────────────────────────────────────────────
async def _get_subscription_row(user_id: str) -> Optional[dict]:
    """Fetch subscription row for user."""
    supabase = get_supabase()
    try:
        result = (
            supabase.table("subscriptions")
            .select("plan, status, trial_end, created_at, subscribed_at, early_bird, early_bird_end")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data
    except Exception:
        return None


async def is_early_bird_active(user_id: str) -> bool:
    """Check if user is in the 24hr early-bird 2x bonus period (first month)."""
    row = await _get_subscription_row(user_id)
    if not row:
        return False
    if not row.get("early_bird"):
        return False
    end = row.get("early_bird_end")
    if not end:
        return False
    end_dt = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
    return datetime.now(timezone.utc) < end_dt


def apply_early_bird(limits: Dict[str, Any]) -> Dict[str, Any]:
    """Double all numeric limits (skip -1 = unlimited)."""
    doubled = {}
    for k, v in limits.items():
        if isinstance(v, (int, float)) and v > 0:
            doubled[k] = v * 2
        else:
            doubled[k] = v
    return doubled


# ──────────────────────────────────────────────────────────────
# Core plan / limits helpers
# ──────────────────────────────────────────────────────────────
async def get_user_plan(user_id: str) -> str:
    """Get user's current plan string."""
    row = await _get_subscription_row(user_id)
    if not row:
        return "free_trial"

    plan = row.get("plan", "free_trial")
    status = row.get("status", "trialing")
    trial_end = row.get("trial_end")

    # Trial expiry
    if plan == "free_trial" and status == "trialing" and trial_end:
        trial_end_dt = datetime.fromisoformat(str(trial_end).replace("Z", "+00:00"))
        if trial_end_dt < datetime.now(timezone.utc):
            return "expired"

    if status not in ("trialing", "active"):
        return "expired"

    return plan


async def get_plan_limits_for_user(user_id: str) -> Tuple[str, Dict[str, Any]]:
    """Return (plan, effective_limits) with early-bird doubling applied."""
    plan = await get_user_plan(user_id)
    limits = get_plan_limits(plan)
    if plan not in ("free_trial", "expired") and await is_early_bird_active(user_id):
        limits = apply_early_bird(limits)
    return plan, limits


def get_plan_limits(plan: str) -> Dict[str, Any]:
    """Get raw limits for a plan."""
    if plan == "expired":
        return dict(EXPIRED_LIMITS)
    return dict(PLAN_LIMITS.get(plan, PLAN_LIMITS["free_trial"]))


# ──────────────────────────────────────────────────────────────
# Usage helpers
# ──────────────────────────────────────────────────────────────
async def get_user_usage(user_id: str) -> Dict[str, Any]:
    """Get user's current usage stats."""
    supabase = get_supabase()

    total_storage = 0
    total_documents = 0
    bucket_count = 0
    team_member_count = 0
    api_calls_today = 0

    try:
        buckets_result = supabase.table("buckets").select("file_count, total_size_bytes").eq("user_id", user_id).execute()
        if buckets_result.data:
            bucket_count = len(buckets_result.data)
            for bucket in buckets_result.data:
                total_storage += bucket.get("total_size_bytes", 0) or 0
                total_documents += bucket.get("file_count", 0) or 0
    except Exception as e:
        logger.error(f"[get_user_usage] Error fetching buckets: {e}")

    try:
        tm_res = (
            supabase.table("team_members")
            .select("id", count="exact")
            .eq("owner_id", user_id)
            .eq("is_active", True)
            .execute()
        )
        team_member_count = tm_res.count if tm_res.count is not None else len(tm_res.data or [])
    except Exception as e:
        logger.warning(f"[get_user_usage] Error fetching team members: {e}")

    try:
        api_usage = supabase.rpc("get_daily_api_usage", {"p_user_id": user_id}).execute()
        api_calls_today = api_usage.data if api_usage.data else 0
    except Exception:
        api_calls_today = 0

    return {
        "storage_bytes": total_storage,
        "document_count": total_documents,
        "bucket_count": bucket_count,
        "team_member_count": team_member_count,
        "api_calls_today": api_calls_today,
    }


async def get_metric_count(user_id: str, metric: str, period: str = "daily") -> int:
    """Get a usage metric count from usage_tracking table."""
    supabase = get_supabase()
    now = datetime.now(timezone.utc)

    if period == "daily":
        period_key = now.strftime("%Y-%m-%d")
    elif period == "hourly":
        period_key = now.strftime("%Y-%m-%d-%H")
    elif period == "minute":
        period_key = now.strftime("%Y-%m-%d-%H-%M")
    else:
        period_key = now.strftime("%Y-%m-%d")

    try:
        result = (
            supabase.table("usage_tracking")
            .select("count")
            .eq("user_id", user_id)
            .eq("metric_type", metric)
            .eq("period_type", period)
            .eq("period_key", period_key)
            .maybe_single()
            .execute()
        )
        if result.data:
            return result.data.get("count", 0)
        return 0
    except Exception as e:
        logger.warning(f"[get_metric_count] {metric}/{period}: {e}")
        return 0


async def increment_metric(user_id: str, metric: str, period: str = "daily") -> int:
    """Increment a usage metric, upserting the row."""
    supabase = get_supabase()
    now = datetime.now(timezone.utc)

    if period == "daily":
        period_key = now.strftime("%Y-%m-%d")
    elif period == "hourly":
        period_key = now.strftime("%Y-%m-%d-%H")
    elif period == "minute":
        period_key = now.strftime("%Y-%m-%d-%H-%M")
    else:
        period_key = now.strftime("%Y-%m-%d")

    try:
        result = supabase.rpc("increment_usage_metric", {
            "p_user_id": user_id,
            "p_metric_type": metric,
            "p_period_type": period,
            "p_period_key": period_key,
        }).execute()
        return result.data if result.data else 1
    except Exception as e:
        logger.error(f"[increment_metric] {metric}/{period}: {e}")
        return 0


# ──────────────────────────────────────────────────────────────
# Limit check helpers (return Tuple[bool, Optional[str]])
# ──────────────────────────────────────────────────────────────
async def check_storage_limit(user_id: str, additional_bytes: int = 0) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."
    usage = await get_user_usage(user_id)
    max_storage = limits["storage_bytes"]
    if usage["storage_bytes"] + additional_bytes > max_storage:
        gb = max_storage / (1024 ** 3)
        return False, f"Storage limit reached ({gb:.0f}GB). Upgrade your plan for more storage."
    return True, None


async def check_file_size_limit(user_id: str, file_size_bytes: int) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."
    max_size = limits["max_file_size_bytes"]
    if file_size_bytes > max_size:
        return False, f"File size ({file_size_bytes / (1024*1024):.1f}MB) exceeds limit ({max_size / (1024*1024):.0f}MB). Upgrade your plan for larger files."
    return True, None


async def check_document_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."
    max_docs = limits["max_documents"]
    if max_docs == -1:
        return True, None
    usage = await get_user_usage(user_id)
    if usage["document_count"] >= max_docs:
        return False, f"Document limit reached ({max_docs}). Upgrade your plan for more documents."
    return True, None


async def check_bucket_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue."
    max_buckets = limits["max_buckets"]
    if max_buckets == -1:
        return True, None
    usage = await get_user_usage(user_id)
    if usage["bucket_count"] >= max_buckets:
        next_plan = NEXT_PLAN.get(plan, "")
        next_name = PLAN_NAMES.get(next_plan, "")
        next_limit = PLAN_LIMITS.get(next_plan, {}).get("max_buckets", "more")
        if next_limit == -1:
            next_limit = "Unlimited"
        return False, f"Bucket limit reached ({max_buckets}). Upgrade to {next_name} for {next_limit} buckets."
    return True, None


async def check_team_member_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    """Check team member seat limits for owners."""
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue."
    max_members = limits["max_team_members"]
    if max_members == -1:
        return True, None
    usage = await get_user_usage(user_id)
    if usage["team_member_count"] >= max_members:
        next_plan = NEXT_PLAN.get(plan, "")
        next_name = PLAN_NAMES.get(next_plan, "")
        next_limit = PLAN_LIMITS.get(next_plan, {}).get("max_team_members", "more")
        if next_limit == -1:
            next_limit = "Unlimited"
        return False, f"Team member limit reached ({max_members}). Upgrade to {next_name} for {next_limit} seats."
    return True, None


async def check_batch_limits(user_id: str, file_count: int, total_bytes: int) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."
    max_files = limits["files_per_upload_batch"]
    if file_count > max_files:
        return False, f"Batch limit: max {max_files} files per upload. Upgrade for more."
    max_batch = limits["max_batch_size_bytes"]
    if total_bytes > max_batch:
        mb = max_batch / (1024 * 1024)
        return False, f"Batch size exceeds limit ({mb:.0f}MB). Upgrade for larger batch uploads."
    return True, None


async def check_image_limit(user_id: str, image_count: int) -> Tuple[bool, Optional[str]]:
    """Check max images per single file."""
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."
    max_images = limits["max_images_per_file"]
    if image_count > max_images:
        return False, f"Image limit exceeded ({image_count} images in file, plan allows {max_images}). Upgrade for larger image-heavy files."
    return True, None


async def check_chat_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue chatting."
    max_msgs = limits["chat_messages_per_day"]
    current = await get_metric_count(user_id, "chat_messages", "daily")
    if current >= max_msgs:
        next_plan = NEXT_PLAN.get(plan, "")
        next_name = PLAN_NAMES.get(next_plan, "")
        next_limit = PLAN_LIMITS.get(next_plan, {}).get("chat_messages_per_day", "more")
        return False, f"Chat limit reached ({max_msgs}/day). Upgrade to {next_name} for {next_limit}/day."
    return True, None


async def check_conversation_limit(user_id: str, bucket_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue."
    max_convos = limits["active_conversations_per_bucket"]
    if max_convos == -1:
        return True, None
    supabase = get_supabase()
    try:
        result = (
            supabase.table("conversations")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("bucket_id", bucket_id)
            .execute()
        )
        count = result.count if result.count is not None else len(result.data or [])
        if count >= max_convos:
            return False, f"Conversation limit reached ({max_convos} per bucket). Delete old ones or upgrade."
        return True, None
    except Exception:
        return True, None


async def check_mcp_query_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade."
    # Per-minute check
    per_min = limits["mcp_queries_per_min"]
    current_min = await get_metric_count(user_id, "mcp_queries", "minute")
    if current_min >= per_min:
        return False, f"MCP rate limit: {per_min} queries/minute. Please wait."
    # Per-day check
    per_day = limits["mcp_queries_per_day"]
    current_day = await get_metric_count(user_id, "mcp_queries", "daily")
    if current_day >= per_day:
        next_plan = NEXT_PLAN.get(plan, "")
        next_name = PLAN_NAMES.get(next_plan, "")
        next_limit = PLAN_LIMITS.get(next_plan, {}).get("mcp_queries_per_day", "more")
        return False, f"MCP daily limit reached ({per_day}/day). Upgrade to {next_name} for {next_limit}/day."
    return True, None


async def check_bucket_chat_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade."
    # Hourly
    per_hour = limits["bucket_chat_per_hour"]
    current_hour = await get_metric_count(user_id, "bucket_chat", "hourly")
    if current_hour >= per_hour:
        return False, f"Bucket chat limit: {per_hour}/hour. Please wait or upgrade."
    # Daily
    per_day = limits["bucket_chat_per_day"]
    current_day = await get_metric_count(user_id, "bucket_chat", "daily")
    if current_day >= per_day:
        next_plan = NEXT_PLAN.get(plan, "")
        next_name = PLAN_NAMES.get(next_plan, "")
        next_limit = PLAN_LIMITS.get(next_plan, {}).get("bucket_chat_per_day", "more")
        return False, f"Bucket chat limit reached ({per_day}/day). Upgrade to {next_name} for {next_limit}/day."
    return True, None


async def check_concurrent_jobs(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade."
    max_jobs = limits["concurrent_processing_jobs"]
    supabase = get_supabase()
    try:
        result = (
            supabase.table("files")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("status", "processing")
            .execute()
        )
        count = result.count if result.count is not None else len(result.data or [])
        if count >= max_jobs:
            return False, f"Processing limit: {max_jobs} concurrent files. Wait for current files to finish or upgrade."
        return True, None
    except Exception:
        return True, None


async def check_api_rate_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    plan, limits = await get_plan_limits_for_user(user_id)
    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue using the API."
    max_calls = limits["api_calls_per_day"]
    usage = await get_user_usage(user_id)
    if usage["api_calls_today"] >= max_calls:
        return False, f"Daily API limit reached ({max_calls} calls/day). Upgrade your plan for more API calls."
    return True, None


# ──────────────────────────────────────────────────────────────
# Raise helpers (for use in routers)
# ──────────────────────────────────────────────────────────────
async def _raise_if_blocked(check_fn, error_type: str, user_id: str, *args):
    """Run a check function and raise 402/429 if blocked."""
    ok, msg = await check_fn(user_id, *args)
    if not ok:
        plan = await get_user_plan(user_id)
        code = 429 if "rate" in error_type or "wait" in (msg or "").lower() else 402
        raise HTTPException(status_code=code, detail=_build_upgrade_detail(error_type, msg, plan))


async def enforce_upload_limits(
    user_id: str,
    file_size_bytes: int,
    batch_count: int = 1,
    batch_total_bytes: int = 0,
    image_count: int = 0
) -> None:
    """Check all upload-related limits. Raises HTTPException on failure."""
    await _raise_if_blocked(check_file_size_limit, "file_size_limit", user_id, file_size_bytes)
    if image_count > 0:
        await _raise_if_blocked(check_image_limit, "file_image_limit", user_id, image_count)
    await _raise_if_blocked(check_document_limit, "document_limit", user_id)
    await _raise_if_blocked(check_storage_limit, "storage_limit", user_id, file_size_bytes)
    await _raise_if_blocked(check_concurrent_jobs, "concurrent_limit", user_id)
    if batch_count > 1 or batch_total_bytes > 0:
        await _raise_if_blocked(check_batch_limits, "batch_limit", user_id, batch_count, batch_total_bytes)

    try:
        await check_and_send_usage_alerts(user_id, file_size_bytes)
    except Exception as e:
        logger.error(f"Failed to send usage alert: {e}")


async def enforce_chat_limits(user_id: str, bucket_id: str = None) -> None:
    """Check chat limits. Raises HTTPException on failure."""
    await _raise_if_blocked(check_chat_limit, "chat_limit", user_id)
    if bucket_id:
        await _raise_if_blocked(check_bucket_chat_limit, "bucket_chat_limit", user_id)


async def enforce_conversation_limit(user_id: str, bucket_id: str) -> None:
    """Check conversation limit. Raises HTTPException on failure."""
    await _raise_if_blocked(check_conversation_limit, "conversation_limit", user_id, bucket_id)


async def enforce_bucket_limit(user_id: str) -> None:
    """Check bucket creation limit. Raises HTTPException on failure."""
    await _raise_if_blocked(check_bucket_limit, "bucket_limit", user_id)


async def enforce_team_member_limit(user_id: str) -> None:
    """Check team member seat limit. Raises HTTPException on failure."""
    await _raise_if_blocked(check_team_member_limit, "team_member_limit", user_id)


async def enforce_mcp_limits(user_id: str) -> None:
    """Check MCP query limits. Raises HTTPException on failure."""
    await _raise_if_blocked(check_mcp_query_limit, "mcp_limit", user_id)


async def increment_api_usage(user_id: str) -> int:
    supabase = get_supabase()
    try:
        result = supabase.rpc("increment_api_usage", {"p_user_id": user_id}).execute()
        return result.data if result.data else 0
    except Exception:
        return 0


async def check_api_limit(user_id: str) -> None:
    """Check API rate limit before API call. Raises HTTPException if exceeded."""
    ok, msg = await check_api_rate_limit(user_id)
    if not ok:
        plan = await get_user_plan(user_id)
        raise HTTPException(status_code=429, detail=_build_upgrade_detail("api_rate_limit", msg, plan))
    await increment_api_usage(user_id)


# Keep backward compat
async def check_all_upload_limits(
    user_id: str,
    file_size_bytes: int,
    batch_count: int = 1,
    batch_total_bytes: int = 0,
    image_count: int = 0
) -> None:
    await enforce_upload_limits(
        user_id,
        file_size_bytes,
        batch_count=batch_count,
        batch_total_bytes=batch_total_bytes,
        image_count=image_count
    )


# ──────────────────────────────────────────────────────────────
# Usage alerts
# ──────────────────────────────────────────────────────────────
from app.services import email_service

async def check_and_send_usage_alerts(user_id: str, additional_bytes: int = 0) -> None:
    try:
        plan, limits = await get_plan_limits_for_user(user_id)
        if plan == "expired":
            return
        usage = await get_user_usage(user_id)

        max_storage = limits["storage_bytes"]
        if max_storage > 0:
            pct = int(((usage["storage_bytes"] + additional_bytes) / max_storage) * 100)
            if 80 <= pct < 85:
                supabase = get_supabase()
                user = supabase.auth.admin.get_user_by_id(user_id)
                if user and user.user and user.user.email:
                    email_service.send_storage_warning_email(to_email=user.user.email, usage_percent=pct, plan=plan)
    except Exception as e:
        logger.error(f"Error checking usage alerts: {e}")


# ──────────────────────────────────────────────────────────────
# Usage summary (for frontend / settings page)
# ──────────────────────────────────────────────────────────────
async def get_usage_summary(user_id: str) -> Dict[str, Any]:
    """Return comprehensive usage summary for the frontend."""
    plan, limits = await get_plan_limits_for_user(user_id)
    usage = await get_user_usage(user_id)
    early_bird = await is_early_bird_active(user_id)

    # Fetch chat / mcp counts
    chat_today = await get_metric_count(user_id, "chat_messages", "daily")
    mcp_today = await get_metric_count(user_id, "mcp_queries", "daily")
    bucket_chat_today = await get_metric_count(user_id, "bucket_chat", "daily")

    # Trial info
    row = await _get_subscription_row(user_id)
    trial_end = None
    subscribed_at = None
    signup_time = None
    if row:
        trial_end = row.get("trial_end")
        subscribed_at = row.get("subscribed_at")
        signup_time = row.get("created_at")

    def pct(used, limit):
        if not limit or limit <= 0 or limit == -1:
            return 0
        return round((used / limit) * 100, 1)

    return {
        "plan": plan,
        "plan_name": PLAN_NAMES.get(plan, plan),
        "early_bird_active": early_bird,
        "trial_end": trial_end,
        "subscribed_at": subscribed_at,
        "signup_time": signup_time,
        "limits": limits,
        "usage": {
            "storage": {
                "used_bytes": usage["storage_bytes"],
                "limit_bytes": limits["storage_bytes"],
                "used_gb": round(usage["storage_bytes"] / (1024 ** 3), 2),
                "limit_gb": round(limits["storage_bytes"] / (1024 ** 3), 2),
                "percentage": pct(usage["storage_bytes"], limits["storage_bytes"]),
            },
            "documents": {
                "count": usage["document_count"],
                "limit": limits["max_documents"],
                "percentage": pct(usage["document_count"], limits["max_documents"]),
            },
            "buckets": {
                "count": usage["bucket_count"],
                "limit": limits["max_buckets"],
                "percentage": pct(usage["bucket_count"], limits["max_buckets"]),
            },
            "team_members": {
                "count": usage["team_member_count"],
                "limit": limits["max_team_members"],
                "percentage": pct(usage["team_member_count"], limits["max_team_members"]),
            },
            "chat_messages": {
                "today": chat_today,
                "limit": limits["chat_messages_per_day"],
                "percentage": pct(chat_today, limits["chat_messages_per_day"]),
            },
            "mcp_queries": {
                "today": mcp_today,
                "limit": limits["mcp_queries_per_day"],
                "percentage": pct(mcp_today, limits["mcp_queries_per_day"]),
            },
            "bucket_chat": {
                "today": bucket_chat_today,
                "limit": limits["bucket_chat_per_day"],
                "percentage": pct(bucket_chat_today, limits["bucket_chat_per_day"]),
            },
            "api_calls": {
                "today": usage["api_calls_today"],
                "limit": limits["api_calls_per_day"],
                "percentage": pct(usage["api_calls_today"], limits["api_calls_per_day"]),
            },
            "max_file_size_mb": limits["max_file_size_bytes"] / (1024 * 1024),
        },
    }
