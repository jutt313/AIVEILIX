"""
MCP Authentication Bridge

Unified authentication handler that supports both:
- OAuth2 tokens (from ChatGPT and other MCP clients)
- API keys (from direct access and Cursor)
"""
import logging
from typing import Optional
from fastapi import HTTPException, Header, Depends, Request
from app.config import get_settings
from app.services.oauth2 import get_oauth2_service, OAuth2Service
from app.services.supabase import get_supabase
from app.models.oauth import MCPUser
import hashlib
from datetime import datetime, timezone

settings = get_settings()
logger = logging.getLogger(__name__)


class MCPAuthError(HTTPException):
    """Custom exception for MCP authentication errors"""
    def __init__(self, detail: str, status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)


async def get_mcp_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    request: Request = None
) -> MCPUser:
    """
    Unified authentication handler for MCP requests.
    
    Supports:
    - Bearer tokens (OAuth2 access tokens from ChatGPT)
    - API keys (Bearer <api_key> for direct access)
    
    Returns MCPUser with user info and scopes.
    """
    if not authorization:
        raise MCPAuthError("Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise MCPAuthError("Invalid Authorization header format. Use: Bearer <token>")
    
    token = authorization.replace("Bearer ", "").strip()
    
    if not token:
        raise MCPAuthError("Empty token")
    
    # Try OAuth2 token first (longer tokens, typically 64+ chars)
    if len(token) > 60:
        user = await _authenticate_oauth_token(token)
        if user:
            return user
    
    # Fall back to API key authentication
    user = await _authenticate_api_key(token)
    if user:
        return user
    
    # If both fail, raise error
    raise MCPAuthError("Invalid token or API key")


async def _authenticate_oauth_token(token: str) -> Optional[MCPUser]:
    """Authenticate using OAuth2 access token"""
    try:
        oauth_service = get_oauth2_service()
        token_data = await oauth_service.validate_access_token(token)
        
        if not token_data:
            return None
        
        # Get client info for scopes
        client = await oauth_service.get_client(token_data["client_id"])
        if not client:
            return None
        
        scopes = token_data.get("scope", "").split() if token_data.get("scope") else []
        
        logger.info(f"OAuth token authenticated: client={token_data['client_id']}, user={token_data['user_id']}")
        
        return MCPUser(
            user_id=str(token_data["user_id"]),
            auth_type="oauth",
            client_id=token_data["client_id"],
            api_key_id=None,
            scopes=scopes,
            allowed_buckets=None  # OAuth clients have access to all user buckets by default
        )
    except Exception as e:
        logger.error(f"OAuth token authentication error: {e}")
        return None


async def _authenticate_api_key(api_key: str) -> Optional[MCPUser]:
    """Authenticate using API key"""
    try:
        supabase = get_supabase()
        
        # Hash the API key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Query API key by hash
        response = supabase.table("api_keys").select(
            "id, user_id, allowed_buckets, scopes, is_active, expires_at"
        ).eq("key_hash", key_hash).single().execute()
        
        if not response.data:
            return None
        
        key_data = response.data
        
        # Validate active status
        if not key_data.get("is_active", False):
            logger.warning(f"Revoked API key attempt: {key_data.get('id')}")
            return None
        
        # Validate expiration
        expires_at = key_data.get("expires_at")
        if expires_at:
            if datetime.now(timezone.utc) > datetime.fromisoformat(expires_at.replace('Z', '+00:00')):
                logger.warning(f"Expired API key attempt: {key_data.get('id')}")
                return None
        
        user_id = str(key_data["user_id"])
        api_key_id = str(key_data["id"])
        
        # Map API key scopes to MCP scopes
        api_scopes = key_data.get("scopes", [])
        mcp_scopes = _map_api_scopes_to_mcp(api_scopes)
        
        logger.info(f"API key authenticated: key_id={api_key_id}, user={user_id}")
        
        return MCPUser(
            user_id=user_id,
            auth_type="api_key",
            client_id=None,
            api_key_id=api_key_id,
            scopes=mcp_scopes,
            allowed_buckets=key_data.get("allowed_buckets")
        )
    except Exception as e:
        logger.error(f"API key authentication error: {e}")
        return None


def _map_api_scopes_to_mcp(api_scopes: list) -> list:
    """Map API key scopes to MCP scopes"""
    scope_mapping = {
        "read": ["read:buckets", "read:files"],
        "write": ["write:buckets"],
        "query": ["query"],
        "chat": ["chat"],
        "full": ["read:buckets", "read:files", "write:buckets", "query", "chat"],
    }
    
    mcp_scopes = set()
    for scope in api_scopes:
        if scope in scope_mapping:
            mcp_scopes.update(scope_mapping[scope])
        else:
            mcp_scopes.add(scope)
    
    return list(mcp_scopes)


def check_mcp_scope(user: MCPUser, required_scope: str) -> bool:
    """Check if user has required scope"""
    # Full access scopes
    if "full" in user.scopes or "*" in user.scopes:
        return True
    
    return required_scope in user.scopes


def require_scope(required_scope: str):
    """Dependency that checks for required scope"""
    async def scope_checker(user: MCPUser = Depends(get_mcp_user)) -> MCPUser:
        if not check_mcp_scope(user, required_scope):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required scope: {required_scope}"
            )
        return user
    return scope_checker


async def check_bucket_access_mcp(user: MCPUser, bucket_id: str) -> bool:
    """
    Check if MCP user has access to a bucket.
    
    Returns True if allowed, raises HTTPException if denied.
    """
    supabase = get_supabase()
    
    # Verify bucket exists and get owner
    bucket_res = supabase.table("buckets").select("id, user_id").eq("id", bucket_id).single().execute()
    
    if not bucket_res.data:
        raise HTTPException(status_code=404, detail="Bucket not found")
    
    bucket_user_id = str(bucket_res.data["user_id"])
    
    # Check if bucket belongs to user
    if bucket_user_id != user.user_id:
        logger.warning(
            f"Cross-user bucket access attempt: user {user.user_id} "
            f"({user.auth_type}) tried to access bucket {bucket_id} owned by {bucket_user_id}"
        )
        raise HTTPException(status_code=403, detail="Access denied to this bucket")
    
    # For API keys, check allowed_buckets restriction
    if user.auth_type == "api_key" and user.allowed_buckets is not None:
        if bucket_id not in user.allowed_buckets:
            raise HTTPException(
                status_code=403,
                detail="API key does not have access to this bucket"
            )
    
    return True


# Convenience dependencies for common scope checks
require_read_buckets = require_scope("read:buckets")
require_read_files = require_scope("read:files")
require_write_buckets = require_scope("write:buckets")
require_query = require_scope("query")
require_chat = require_scope("chat")
