from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from app.models.api_keys import (
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    APIKeyResponse,
    APIKeysListResponse
)
from app.services.supabase import get_supabase
from app.routers.buckets import get_current_user_id
from app.utils.error_logger import log_error, get_correlation_id
import uuid
import hashlib
import secrets
import logging
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)

# API Key prefix
API_KEY_PREFIX = "aiveilix_sk_live_"


def generate_api_key() -> tuple[str, str, str]:
    """Generate API key: returns (full_key, key_hash, key_prefix)"""
    # Generate 32 random bytes (256 bits)
    random_part = secrets.token_urlsafe(32)
    full_key = f"{API_KEY_PREFIX}{random_part}"
    
    # Hash the full key (SHA256)
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Prefix is first 12 chars after prefix
    key_prefix = f"{API_KEY_PREFIX}{random_part[:12]}..."
    
    return full_key, key_hash, key_prefix


@router.post("/", response_model=CreateAPIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new API key (returns full key once)"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase = get_supabase()
        
        # Validate scopes
        valid_scopes = ['read', 'write', 'delete']
        for scope in request.scopes:
            if scope not in valid_scopes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid scope: {scope}. Valid scopes are: {valid_scopes}"
                )
        
        # Generate API key
        full_key, key_hash, key_prefix = generate_api_key()
        
        # Create API key record
        # Note: allowed_buckets can be None (all buckets) or list (specific buckets)
        # Don't convert None to [] as it changes semantics
        api_key_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": request.name,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "scopes": request.scopes,
            "allowed_buckets": request.allowed_buckets,  # Preserve None for "all buckets"
            "is_active": True,
            "request_count": 0
        }
        
        response = supabase.table("api_keys").insert(api_key_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create API key")
        
        key_record = response.data[0]
        
        return CreateAPIKeyResponse(
            success=True,
            message="API key created successfully",
            api_key=full_key,  # Return full key ONLY once
            key_data=APIKeyResponse(
                id=str(key_record["id"]),
                name=key_record["name"],
                key_prefix=key_record["key_prefix"],
                scopes=key_record["scopes"],
                allowed_buckets=key_record.get("allowed_buckets"),
                is_active=key_record["is_active"],
                last_used_at=key_record.get("last_used_at"),
                request_count=key_record["request_count"],
                created_at=key_record["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/", response_model=APIKeysListResponse)
async def list_api_keys(
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """List all API keys for current user (never returns full key)"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase = get_supabase()
        
        response = supabase.table("api_keys").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        keys_data = response.data if response.data else []
        keys = [
            APIKeyResponse(
                id=str(key["id"]),
                name=key["name"],
                key_prefix=key["key_prefix"],
                scopes=key["scopes"],
                allowed_buckets=key.get("allowed_buckets"),
                is_active=key["is_active"],
                last_used_at=key.get("last_used_at"),
                request_count=key["request_count"],
                created_at=key["created_at"]
            )
            for key in keys_data
        ]
        
        return APIKeysListResponse(keys=keys, total=len(keys))
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list API keys: {str(e)}"
        )


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """Delete/revoke an API key"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase = get_supabase()
        
        # Check if key exists and belongs to user
        response = supabase.table("api_keys").select("id").eq("id", key_id).eq("user_id", user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Delete the key
        supabase.table("api_keys").delete().eq("id", key_id).execute()
        
        return {"success": True, "message": "API key deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete API key: {str(e)}"
        )
