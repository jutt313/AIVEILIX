from fastapi import Request, HTTPException
from app.config import get_settings
from typing import Optional
import time
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory rate limit store (use Redis in production)
_rate_limit_store = {}


def get_rate_limit_key(request: Request, api_key_id: str) -> str:
    """Generate rate limit key for API key"""
    return f"mcp_rate_limit:{api_key_id}"


def check_rate_limit(api_key_id: str) -> tuple[bool, Optional[int]]:
    """
    Check if API key has exceeded rate limit
    Returns: (is_allowed, retry_after_seconds)
    """
    key = f"mcp_rate_limit:{api_key_id}"
    current_time = time.time()
    window_start = current_time - settings.mcp_rate_limit_window
    
    # Get request timestamps for this key
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    
    # Clean old requests outside the window
    _rate_limit_store[key] = [
        ts for ts in _rate_limit_store[key] 
        if ts > window_start
    ]
    
    # Check if limit exceeded
    request_count = len(_rate_limit_store[key])
    
    if request_count >= settings.mcp_rate_limit_per_hour:
        # Calculate retry after (time until oldest request expires)
        if _rate_limit_store[key]:
            oldest_request = min(_rate_limit_store[key])
            retry_after = int(oldest_request + settings.mcp_rate_limit_window - current_time)
            retry_after = max(1, retry_after)  # At least 1 second
        else:
            retry_after = settings.mcp_rate_limit_window
        return False, retry_after
    
    # Record this request
    _rate_limit_store[key].append(current_time)
    return True, None


def enforce_rate_limit(api_key_id: str):
    """
    Enforce rate limit for API key
    Raises HTTPException with 429 if limit exceeded
    """
    is_allowed, retry_after = check_rate_limit(api_key_id)
    
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for API key: {api_key_id}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(retry_after)} if retry_after else {}
        )
