from fastapi import APIRouter, HTTPException, Header, Depends, Request, Query
from typing import Optional
from app.models.buckets import BucketCreate, BucketResponse, BucketsListResponse, DashboardStats, DeleteAllBucketsRequest, ActivityDataResponse, ActivityDataPoint
from app.services.supabase import get_supabase_auth, get_supabase
from app.config import get_settings
from app.utils.error_logger import log_error, get_correlation_id
from app.utils.tracer import Tracer
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import logging
import traceback

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


async def get_current_user_id(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Extract user ID from JWT token — decode locally, NO Supabase round-trip."""
    import time as _time
    import base64, json as _json
    _t0 = _time.perf_counter()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    # ── Fast path: decode JWT payload locally (no network call) ──────────────
    try:
        parts = token.split(".")
        if len(parts) == 3:
            payload_b64 = parts[1]
            # Add padding if needed
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
            user_id = payload.get("sub")
            exp = payload.get("exp", 0)
            import time as _t
            if user_id and exp > _t.time():
                ms = round((_time.perf_counter() - _t0) * 1000, 1)
                logger.debug(f"🟢 JWT local decode {ms}ms  user={user_id[:8]}...")
                return str(user_id)
            elif exp <= _t.time():
                raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except HTTPException:
        raise
    except Exception:
        pass  # fall through to Supabase validation

    # ── Slow path fallback: verify with Supabase (catches revoked tokens) ────
    try:
        supabase_auth = get_supabase_auth()
        user = supabase_auth.auth.get_user(token)
        ms = round((_time.perf_counter() - _t0) * 1000, 1)
        logger.warning(f"🟡 get_current_user_id Supabase fallback {ms}ms")
        if not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return str(user.user.id)
    except HTTPException:
        raise
    except Exception as e:
        ms = round((_time.perf_counter() - _t0) * 1000, 1)
        logger.error(f"🔴 get_current_user_id FAILED {ms}ms: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed. Please log in again.")


@router.get("/", response_model=BucketsListResponse)
async def list_buckets(http_request: Request, user_id: str = Depends(get_current_user_id)):
    """Get all buckets for current user"""
    correlation_id = get_correlation_id(http_request)
    t = Tracer("GET /api/buckets", user_id=user_id)
    try:
        from app.services.team_service import get_effective_user_id, get_member_accessible_buckets
        effective_uid = get_effective_user_id(user_id)
        t.step("get_effective_user_id")

        supabase = get_supabase()

        accessible = get_member_accessible_buckets(user_id)
        t.step("get_member_accessible_buckets")
        if accessible is not None:
            if not accessible:
                t.done()
                return BucketsListResponse(buckets=[], total=0)
            response = supabase.table("buckets").select("*").eq("user_id", effective_uid).in_("id", accessible).order("created_at", desc=True).execute()
        else:
            response = supabase.table("buckets").select("*").eq("user_id", effective_uid).order("created_at", desc=True).execute()
        t.step("DB query buckets", count=len(response.data) if response.data else 0)

        buckets_data = response.data if response.data else []
        buckets = [
            BucketResponse(
                id=str(bucket["id"]),
                user_id=str(bucket["user_id"]),
                name=bucket["name"],
                description=bucket.get("description"),
                is_private=bucket["is_private"],
                file_count=bucket.get("file_count", 0),
                total_size_bytes=bucket.get("total_size_bytes", 0),
                created_at=bucket["created_at"],
                updated_at=bucket["updated_at"]
            )
            for bucket in buckets_data
        ]

        t.done()
        return BucketsListResponse(buckets=buckets, total=len(buckets))

    except HTTPException:
        t.done(status_code=400)
        raise
    except Exception as e:
        t.error("list buckets failed", e)
        t.done(status_code=500)
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to load buckets. Please try again."
        )


@router.post("/", response_model=BucketResponse)
async def create_bucket(
    bucket_data: BucketCreate,
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new bucket"""
    correlation_id = get_correlation_id(http_request)
    t = Tracer("POST /api/buckets", user_id=user_id, name=bucket_data.name)
    try:
        from app.services.team_service import get_team_member_context
        if get_team_member_context(user_id):
            raise HTTPException(status_code=403, detail="Team members cannot create buckets")
        t.step("Team member check")

        from app.services.plan_limits import enforce_bucket_limit
        await enforce_bucket_limit(user_id)
        t.step("Enforce bucket limit")

        supabase = get_supabase()

        new_bucket = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": bucket_data.name,
            "description": bucket_data.description,
            "is_private": True,
            "file_count": 0,
            "total_size_bytes": 0
        }

        response = supabase.table("buckets").insert(new_bucket).execute()
        t.step("DB insert bucket")

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create bucket")

        bucket = response.data[0]
        t.done()
        return BucketResponse(
            id=str(bucket["id"]),
            user_id=str(bucket["user_id"]),
            name=bucket["name"],
            description=bucket.get("description"),
            is_private=bucket["is_private"],
            file_count=bucket["file_count"],
            total_size_bytes=bucket["total_size_bytes"],
            created_at=bucket["created_at"],
            updated_at=bucket["updated_at"]
        )

    except HTTPException:
        t.done(status_code=400)
        raise
    except Exception as e:
        t.error("create bucket failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Create bucket error for user {user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create bucket. Please try again."
        )


@router.get("/{bucket_id}", response_model=BucketResponse)
async def get_bucket(
    bucket_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific bucket"""
    t = Tracer("GET /api/buckets/{id}", user_id=user_id, bucket_id=bucket_id)
    try:
        from app.services.team_service import get_effective_user_id, check_bucket_permission
        effective_uid = get_effective_user_id(user_id)
        t.step("get_effective_user_id")

        if not check_bucket_permission(user_id, bucket_id, "can_view"):
            raise HTTPException(status_code=403, detail="You don't have access to this bucket")
        t.step("check_bucket_permission")

        supabase = get_supabase()
        response = supabase.table("buckets").select("*").eq("id", bucket_id).eq("user_id", effective_uid).single().execute()
        t.step("DB query bucket")

        if not response.data:
            raise HTTPException(status_code=404, detail="Bucket not found")

        bucket = response.data
        t.done()
        return BucketResponse(
            id=str(bucket["id"]),
            user_id=str(bucket["user_id"]),
            name=bucket["name"],
            description=bucket.get("description"),
            is_private=bucket["is_private"],
            file_count=bucket["file_count"],
            total_size_bytes=bucket["total_size_bytes"],
            created_at=bucket["created_at"],
            updated_at=bucket["updated_at"]
        )

    except HTTPException:
        t.done(status_code=404)
        raise
    except Exception as e:
        t.error("get bucket failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Get bucket error for user {user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load bucket. Please try again."
        )


@router.delete("/{bucket_id}")
async def delete_bucket(
    bucket_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a bucket"""
    try:
        from app.services.team_service import get_team_member_context
        if get_team_member_context(user_id):
            raise HTTPException(status_code=403, detail="Team members cannot delete buckets")

        supabase = get_supabase()

        # Check if bucket exists and belongs to user
        response = supabase.table("buckets").select("id").eq("id", bucket_id).eq("user_id", user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Bucket not found")
        
        # Delete bucket (cascade will delete related files/chunks)
        supabase.table("buckets").delete().eq("id", bucket_id).execute()
        
        return {"success": True, "message": "Bucket deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Delete bucket error for user {user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete bucket. Please try again."
        )


@router.post("/delete-all")
async def delete_all_buckets(
    request: DeleteAllBucketsRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Delete all buckets for current user (requires password verification)"""
    try:
        supabase_auth = get_supabase_auth()
        supabase_service = get_supabase()
        
        # Get user email using admin API
        try:
            admin_user = supabase_service.auth.admin.get_user_by_id(user_id)
            user_email = admin_user.user.email
        except Exception:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify password by attempting login
        try:
            verify_response = supabase_auth.auth.sign_in_with_password({
                "email": user_email,
                "password": request.password
            })
            if not verify_response.user:
                raise HTTPException(status_code=401, detail="Password is incorrect")
        except Exception:
            raise HTTPException(status_code=401, detail="Password is incorrect")
        
        # Get all buckets for user
        buckets_res = supabase_service.table("buckets").select("id").eq("user_id", user_id).execute()
        bucket_ids = [b["id"] for b in (buckets_res.data or [])]
        
        if not bucket_ids:
            return {"success": True, "message": "No buckets to delete"}
        
        # Delete all buckets (cascade will delete related files/chunks)
        for bucket_id in bucket_ids:
            supabase_service.table("buckets").delete().eq("id", bucket_id).execute()
        
        return {"success": True, "message": f"Deleted {len(bucket_ids)} bucket(s)"}
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Delete all buckets error for user {user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete buckets. Please try again."
        )


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(user_id: str = Depends(get_current_user_id)):
    """Get dashboard statistics"""
    t = Tracer("GET /api/buckets/stats/dashboard", user_id=user_id)
    try:
        supabase = get_supabase()

        buckets_response = supabase.table("buckets").select("file_count, total_size_bytes").eq("user_id", user_id).execute()
        t.step("DB query bucket stats")

        buckets_data = buckets_response.data if buckets_response.data else []
        total_buckets = len(buckets_data)
        total_files = sum(bucket.get("file_count", 0) for bucket in buckets_data)
        total_storage = sum(bucket.get("total_size_bytes", 0) for bucket in buckets_data)

        t.done()
        return DashboardStats(
            total_buckets=total_buckets,
            total_files=total_files,
            total_storage_bytes=total_storage
        )

    except HTTPException:
        t.done(status_code=400)
        raise
    except Exception as e:
        t.error("dashboard stats failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Dashboard stats error for user {user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load stats. Please try again."
        )


@router.get("/stats/activity", response_model=ActivityDataResponse)
async def get_activity_stats(
    user_id: str = Depends(get_current_user_id),
    days: Optional[int] = Query(None, description="Number of days to look back (default: 30)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get activity data for date range (true cumulative counts including baseline)"""
    t = Tracer("GET /api/buckets/stats/activity", user_id=user_id)
    try:
        supabase = get_supabase()

        # Determine date range
        if start_date and end_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        elif days:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=days)
        else:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=30)

        start_iso = start_date_obj.isoformat()
        end_iso = end_date_obj.isoformat()

        # ── Baseline: everything created BEFORE the date range window ─────────
        buckets_before = supabase.table("buckets").select("id").eq(
            "user_id", user_id
        ).lt("created_at", start_iso).execute()

        files_before = supabase.table("files").select("size_bytes").eq(
            "user_id", user_id
        ).lt("created_at", start_iso).execute()

        t.step("DB query baselines")
        baseline_buckets = len(buckets_before.data) if buckets_before.data else 0
        baseline_files   = len(files_before.data)   if files_before.data   else 0
        baseline_storage = sum(
            f.get("size_bytes", 0) for f in (files_before.data or [])
        ) / (1024 * 1024)

        # ── Buckets created within the range ──────────────────────────────────
        buckets_in_range = supabase.table("buckets").select("created_at").eq(
            "user_id", user_id
        ).gte("created_at", start_iso).lte("created_at", end_iso).execute()

        # ── Files created within the range (tracked by their own created_at) ──
        files_in_range = supabase.table("files").select("created_at, size_bytes").eq(
            "user_id", user_id
        ).gte("created_at", start_iso).lte("created_at", end_iso).execute()
        t.step("DB query range data")

        # Group daily increments by date
        activity_map = defaultdict(lambda: {"files": 0, "buckets": 0, "storage": 0.0})

        for bucket in (buckets_in_range.data or []):
            date_key = datetime.fromisoformat(
                bucket["created_at"].replace('Z', '+00:00')
            ).date().isoformat()
            activity_map[date_key]["buckets"] += 1

        for file in (files_in_range.data or []):
            date_key = datetime.fromisoformat(
                file["created_at"].replace('Z', '+00:00')
            ).date().isoformat()
            activity_map[date_key]["files"] += 1
            activity_map[date_key]["storage"] += file.get("size_bytes", 0) / (1024 * 1024)

        # Build cumulative series starting from the baseline totals
        current_date      = start_date_obj.date()
        end_date_loop     = end_date_obj.date()
        cumulative_buckets = baseline_buckets
        cumulative_files   = baseline_files
        cumulative_storage = baseline_storage

        activity_data = []

        while current_date <= end_date_loop:
            date_key = current_date.isoformat()
            daily = activity_map.get(date_key, {"files": 0, "buckets": 0, "storage": 0.0})

            cumulative_buckets += daily["buckets"]
            cumulative_files   += daily["files"]
            cumulative_storage += daily["storage"]

            activity_data.append(
                ActivityDataPoint(
                    date=date_key,
                    files=cumulative_files,
                    buckets=cumulative_buckets,
                    storage=round(cumulative_storage, 2)
                )
            )

            current_date += timedelta(days=1)

        t.done()
        return ActivityDataResponse(data=activity_data)

    except HTTPException:
        t.done(status_code=400)
        raise
    except Exception as e:
        t.error("activity stats failed", e)
        t.done(status_code=500)
        error_trace = traceback.format_exc()
        logger.error(f"Activity stats error for user {user_id}: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load activity data. Please try again."
        )
