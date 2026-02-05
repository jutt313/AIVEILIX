"""
Plan limits enforcement service
"""
import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from fastapi import HTTPException

from app.config import get_settings
from app.services.supabase import get_supabase

settings = get_settings()
logger = logging.getLogger(__name__)

# Plan limits configuration
PLAN_LIMITS = {
    "free_trial": {
        "storage_bytes": 1 * 1024 * 1024 * 1024,  # 1GB
        "max_documents": 50,
        "max_file_size_bytes": 10 * 1024 * 1024,  # 10MB
        "api_calls_per_day": 50
    },
    "starter": {
        "storage_bytes": 3 * 1024 * 1024 * 1024,  # 3GB
        "max_documents": 200,
        "max_file_size_bytes": 25 * 1024 * 1024,  # 25MB
        "api_calls_per_day": 100
    },
    "pro": {
        "storage_bytes": 10 * 1024 * 1024 * 1024,  # 10GB
        "max_documents": -1,  # Unlimited
        "max_file_size_bytes": 50 * 1024 * 1024,  # 50MB
        "api_calls_per_day": 1000
    },
    "premium": {
        "storage_bytes": 50 * 1024 * 1024 * 1024,  # 50GB
        "max_documents": -1,  # Unlimited
        "max_file_size_bytes": 100 * 1024 * 1024,  # 100MB
        "api_calls_per_day": 5000
    }
}


async def get_user_plan(user_id: str) -> str:
    """Get user's current plan"""
    logger.info(f"[get_user_plan] user_id={user_id}")
    supabase = get_supabase()

    try:
        result = supabase.table("subscriptions").select("plan, status, trial_end").eq("user_id", user_id).single().execute()
        logger.info(f"[get_user_plan] DB result: {result.data}")

        if not result.data:
            logger.info(f"[get_user_plan] No subscription found, returning free_trial")
            return "free_trial"

        plan = result.data.get("plan", "free_trial")
        status = result.data.get("status", "trialing")
        trial_end = result.data.get("trial_end")

        logger.info(f"[get_user_plan] plan={plan}, status={status}, trial_end={trial_end}")

        # Check if trial has expired
        if plan == "free_trial" and status == "trialing" and trial_end:
            trial_end_dt = datetime.fromisoformat(trial_end.replace('Z', '+00:00'))
            if trial_end_dt < datetime.now(timezone.utc):
                logger.info(f"[get_user_plan] Trial expired")
                return "expired"

        # Check if subscription is active
        if status not in ["trialing", "active"]:
            logger.info(f"[get_user_plan] Status not active: {status}")
            return "expired"

        return plan

    except Exception as e:
        logger.error(f"[get_user_plan] Error: {e}\n{traceback.format_exc()}")
        # Default to free_trial on error to not block users
        return "free_trial"


def get_plan_limits(plan: str) -> Dict[str, Any]:
    """Get limits for a plan"""
    if plan == "expired":
        # Expired users get heavily restricted access
        return {
            "storage_bytes": 0,
            "max_documents": 0,
            "max_file_size_bytes": 0,
            "api_calls_per_day": 0
        }

    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free_trial"])


async def get_user_usage(user_id: str) -> Dict[str, Any]:
    """Get user's current usage stats"""
    logger.info(f"[get_user_usage] user_id={user_id}")
    supabase = get_supabase()

    total_storage = 0
    total_documents = 0
    api_calls_today = 0

    try:
        # Get total storage and document count
        buckets_result = supabase.table("buckets").select("file_count, total_size_bytes").eq("user_id", user_id).execute()
        logger.info(f"[get_user_usage] Buckets: {len(buckets_result.data) if buckets_result.data else 0}")

        if buckets_result.data:
            for bucket in buckets_result.data:
                total_storage += bucket.get("total_size_bytes", 0) or 0
                total_documents += bucket.get("file_count", 0) or 0

        logger.info(f"[get_user_usage] storage={total_storage}, docs={total_documents}")

    except Exception as e:
        logger.error(f"[get_user_usage] Error fetching buckets: {e}\n{traceback.format_exc()}")

    try:
        # Get API usage for today
        api_usage = supabase.rpc("get_daily_api_usage", {"p_user_id": user_id}).execute()
        api_calls_today = api_usage.data if api_usage.data else 0
        logger.info(f"[get_user_usage] api_calls_today={api_calls_today}")
    except Exception as e:
        logger.warning(f"[get_user_usage] Error fetching API usage (function may not exist): {e}")
        # API usage function might not exist yet - that's ok
        api_calls_today = 0

    return {
        "storage_bytes": total_storage,
        "document_count": total_documents,
        "api_calls_today": api_calls_today
    }


async def check_storage_limit(user_id: str, additional_bytes: int = 0) -> Tuple[bool, Optional[str]]:
    """Check if user can add more storage"""
    plan = await get_user_plan(user_id)
    limits = get_plan_limits(plan)
    usage = await get_user_usage(user_id)

    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."

    max_storage = limits["storage_bytes"]
    current_storage = usage["storage_bytes"]

    if current_storage + additional_bytes > max_storage:
        storage_gb = max_storage / (1024 * 1024 * 1024)
        return False, f"Storage limit reached ({storage_gb}GB). Upgrade your plan for more storage."

    return True, None


async def check_document_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    """Check if user can upload more documents"""
    plan = await get_user_plan(user_id)
    limits = get_plan_limits(plan)
    usage = await get_user_usage(user_id)

    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."

    max_docs = limits["max_documents"]
    current_docs = usage["document_count"]

    if max_docs != -1 and current_docs >= max_docs:
        return False, f"Document limit reached ({max_docs} documents). Upgrade your plan for more documents."

    return True, None


async def check_file_size_limit(user_id: str, file_size_bytes: int) -> Tuple[bool, Optional[str]]:
    """Check if file size is within plan limits"""
    plan = await get_user_plan(user_id)
    limits = get_plan_limits(plan)

    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue uploading files."

    max_size = limits["max_file_size_bytes"]

    if file_size_bytes > max_size:
        max_mb = max_size / (1024 * 1024)
        file_mb = file_size_bytes / (1024 * 1024)
        return False, f"File size ({file_mb:.1f}MB) exceeds limit ({max_mb}MB). Upgrade your plan for larger files."

    return True, None


async def check_api_rate_limit(user_id: str) -> Tuple[bool, Optional[str]]:
    """Check if user has API calls remaining"""
    plan = await get_user_plan(user_id)
    limits = get_plan_limits(plan)
    usage = await get_user_usage(user_id)

    if plan == "expired":
        return False, "Your trial has expired. Please upgrade to continue using the API."

    max_calls = limits["api_calls_per_day"]
    current_calls = usage["api_calls_today"]

    if current_calls >= max_calls:
        return False, f"Daily API limit reached ({max_calls} calls/day). Upgrade your plan for more API calls."

    return True, None


async def increment_api_usage(user_id: str) -> int:
    """Increment API usage counter and return new count"""
    supabase = get_supabase()
    result = supabase.rpc("increment_api_usage", {"p_user_id": user_id}).execute()
    return result.data if result.data else 0


async def check_all_upload_limits(user_id: str, file_size_bytes: int) -> None:
    """Check all limits before file upload. Raises HTTPException if any limit exceeded."""

    # Check file size
    can_upload, error = await check_file_size_limit(user_id, file_size_bytes)
    if not can_upload:
        raise HTTPException(status_code=402, detail={
            "error": "file_size_limit",
            "message": error,
            "upgrade_required": True
        })

    # Check document count
    can_upload, error = await check_document_limit(user_id)
    if not can_upload:
        raise HTTPException(status_code=402, detail={
            "error": "document_limit",
            "message": error,
            "upgrade_required": True
        })

    # Check storage
    can_upload, error = await check_storage_limit(user_id, file_size_bytes)
    
    # Check for usage alerts (after successful checks)
    try:
        await check_and_send_usage_alerts(user_id, file_size_bytes)
    except Exception as e:
        logger.error(f"Failed to send usage alert: {e}")

    if not can_upload:
        raise HTTPException(status_code=402, detail={
            "error": "storage_limit",
            "message": error,
            "upgrade_required": True
        })


from app.services import email_service

async def check_and_send_usage_alerts(user_id: str, additional_bytes: int = 0) -> None:
    """Check usage levels and send warning emails if thresholds reached"""
    try:
        plan = await get_user_plan(user_id)
        if plan == "expired":
            return
            
        limits = get_plan_limits(plan)
        usage = await get_user_usage(user_id)
        
        # 1. Storage Alert (80%)
        max_storage = limits["storage_bytes"]
        if max_storage > 0:
            current_storage = usage["storage_bytes"] + additional_bytes
            usage_percent = int((current_storage / max_storage) * 100)
            
            # Send alert if between 80% and 90% (to avoid spamming on every byte near 100%)
            # Ideally we'd track "alert_sent" state, but for now this window reduces spam
            if 80 <= usage_percent < 85: 
                # Get email
                supabase = get_supabase()
                user = supabase.auth.admin.get_user_by_id(user_id)
                if user and user.user and user.user.email:
                    email_service.send_storage_warning_email(
                        to_email=user.user.email,
                        usage_percent=usage_percent,
                        plan=plan
                    )
                    
        # 2. Document Alert (Approaching limit)
        max_docs = limits["max_documents"]
        if max_docs != -1 and max_docs > 0:
            current_docs = usage["document_count"]
            # Warn if within 10% or 5 docs of limit
            if current_docs >= (max_docs * 0.9) or (max_docs - current_docs) <= 5:
                # Avoid spamming if already over limit (user can't upload anyway)
                if current_docs < max_docs:
                    # Get email (if not fetched above)
                    supabase = get_supabase()
                    user = supabase.auth.admin.get_user_by_id(user_id)
                    if user and user.user and user.user.email:
                        email_service.send_document_limit_warning_email(
                            to_email=user.user.email,
                            current_count=current_docs,
                            limit=max_docs,
                            plan=plan
                        )
                        
    except Exception as e:
        logger.error(f"Error checking usage alerts: {e}")


async def check_api_limit(user_id: str) -> None:
    """Check API rate limit before API call. Raises HTTPException if limit exceeded."""

    can_call, error = await check_api_rate_limit(user_id)
    if not can_call:
        raise HTTPException(status_code=429, detail={
            "error": "api_rate_limit",
            "message": error,
            "upgrade_required": True
        })

    # Increment usage
    await increment_api_usage(user_id)


async def get_usage_summary(user_id: str) -> Dict[str, Any]:
    """Get complete usage summary for user"""
    logger.info(f"[get_usage_summary] user_id={user_id}")

    try:
        plan = await get_user_plan(user_id)
        limits = get_plan_limits(plan)
        usage = await get_user_usage(user_id)

        logger.info(f"[get_usage_summary] plan={plan}, limits={limits}")

        summary = {
            "plan": plan,
            "usage": {
                "storage": {
                    "used_bytes": usage["storage_bytes"],
                    "limit_bytes": limits["storage_bytes"],
                    "used_gb": round(usage["storage_bytes"] / (1024 * 1024 * 1024), 2),
                    "limit_gb": round(limits["storage_bytes"] / (1024 * 1024 * 1024), 2),
                    "percentage": round((usage["storage_bytes"] / limits["storage_bytes"]) * 100, 1) if limits["storage_bytes"] > 0 else 0
                },
                "documents": {
                    "count": usage["document_count"],
                    "limit": limits["max_documents"],
                    "percentage": round((usage["document_count"] / limits["max_documents"]) * 100, 1) if limits["max_documents"] > 0 else 0
                },
                "api_calls": {
                    "today": usage["api_calls_today"],
                    "limit": limits["api_calls_per_day"],
                    "percentage": round((usage["api_calls_today"] / limits["api_calls_per_day"]) * 100, 1) if limits["api_calls_per_day"] > 0 else 0
                },
                "max_file_size_mb": limits["max_file_size_bytes"] / (1024 * 1024)
            }
        }

        logger.info(f"[get_usage_summary] Success")
        return summary

    except Exception as e:
        logger.error(f"[get_usage_summary] Error: {e}\n{traceback.format_exc()}")
        raise
