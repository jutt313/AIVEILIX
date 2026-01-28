"""
Comprehensive Error Logging Utility

Logs errors to database with full context for debugging and monitoring.
Includes timing, timeout detection, and performance metrics.
"""
import logging
import traceback
import uuid
import time
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from fastapi import Request
from app.services.supabase import get_supabase

logger = logging.getLogger(__name__)


def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Remove sensitive headers from logging"""
    sensitive_headers = {
        'authorization', 'cookie', 'x-api-key', 'x-auth-token',
        'x-access-token', 'x-refresh-token', 'password', 'secret'
    }
    
    sanitized = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_headers):
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_body(body: Any) -> Any:
    """Remove sensitive fields from request body"""
    if not isinstance(body, dict):
        return body
    
    sensitive_fields = {
        'password', 'secret', 'token', 'api_key', 'client_secret',
        'access_token', 'refresh_token', 'code_verifier'
    }
    
    sanitized = {}
    for key, value in body.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_fields):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_body(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_body(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    # Check for forwarded headers (from proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    if request.client:
        return request.client.host
    
    return None


async def log_error(
    request: Request,
    error: Exception,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None,
    request_duration_ms: Optional[float] = None,
    is_timeout: bool = False,
    query_details: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Log an error to the database with full context including timing and performance metrics.
    
    Args:
        request: FastAPI Request object
        error: The exception that occurred
        user_id: Optional user ID (if authenticated)
        correlation_id: Optional correlation ID for request tracking
        additional_context: Optional additional context to log
        request_duration_ms: Request duration in milliseconds
        is_timeout: Whether this error is due to a timeout
        query_details: Database query details (query, duration, etc.)
    
    Returns:
        The error log ID
    """
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    
    error_id = str(uuid.uuid4())
    error_type = type(error).__name__
    error_message = str(error)
    stack_trace = traceback.format_exc()
    
    # Extract request details
    endpoint = str(request.url.path)
    method = request.method
    ip_address = get_client_ip(request)
    query_params = dict(request.query_params) if request.query_params else {}
    
    # Get request body (sanitized) - try multiple methods
    request_body = None
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            # Try to get body as JSON
            try:
                body = await request.json()
                request_body = sanitize_body(body)
            except:
                # Try to get raw body
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        request_body = {"raw_body_length": len(body_bytes), "raw_body_preview": body_bytes[:500].decode('utf-8', errors='ignore')}
                except:
                    pass
    except Exception as e:
        logger.debug(f"Could not read request body: {e}")
    
    # Get headers (sanitized)
    headers = sanitize_headers(dict(request.headers))
    
    # Detect timeout errors
    if is_timeout or "timeout" in error_message.lower() or "timed out" in error_message.lower():
        is_timeout = True
    
    # Prepare comprehensive error log data
    error_data = {
        "id": error_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "method": method,
        "user_id": user_id,
        "error_type": error_type,
        "error_message": error_message,
        "stack_trace": stack_trace,
        "request_body": request_body,
        "headers": headers,
        "ip_address": ip_address,
        "correlation_id": correlation_id,
        "query_params": query_params,
        "request_duration_ms": request_duration_ms,
        "is_timeout": is_timeout,
        "query_details": query_details,
    }
    
    # Add additional context if provided
    if additional_context:
        error_data["additional_context"] = additional_context
    
    try:
        supabase = get_supabase()
        result = supabase.table("error_logs").insert(error_data).execute()
        
        if result.data:
            logger.error(f"Error logged: id={error_id}, endpoint={endpoint}, error_type={error_type}, timeout={is_timeout}, duration={request_duration_ms}ms, correlation_id={correlation_id}")
            return error_id
        else:
            logger.error(f"Failed to insert error log: {error_id}")
            return error_id
    except Exception as e:
        # Fallback to standard logging if database insert fails
        logger.error(f"Failed to log error to database: {e}")
        logger.error(f"Error details: {error_type}: {error_message}")
        logger.error(f"Stack trace: {stack_trace}")
        logger.error(f"Request duration: {request_duration_ms}ms, Timeout: {is_timeout}")
        return error_id


def get_correlation_id(request: Request) -> str:
    """Get or create correlation ID from request headers"""
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    return correlation_id


async def log_request_with_timing(
    request: Request,
    handler: Callable,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    timeout_seconds: float = 30.0
) -> Any:
    """
    Execute a request handler with timing and timeout detection.
    Logs errors with detailed timing information.
    
    Args:
        request: FastAPI Request object
        handler: Async function to execute
        user_id: Optional user ID
        correlation_id: Optional correlation ID
        timeout_seconds: Timeout threshold in seconds
    
    Returns:
        Handler result
    
    Raises:
        TimeoutError: If request exceeds timeout
        Exception: Any exception from handler
    """
    start_time = time.time()
    correlation_id = correlation_id or get_correlation_id(request)
    
    try:
        # Execute handler with timeout
        result = await asyncio.wait_for(handler(), timeout=timeout_seconds)
        duration_ms = (time.time() - start_time) * 1000
        
        # Log slow requests (over 5 seconds)
        if duration_ms > 5000:
            logger.warning(f"Slow request: endpoint={request.url.path}, duration={duration_ms:.2f}ms, correlation_id={correlation_id}")
        
        return result
        
    except asyncio.TimeoutError:
        duration_ms = (time.time() - start_time) * 1000
        timeout_error = TimeoutError(f"Request timeout after {timeout_seconds}s")
        await log_error(
            request,
            timeout_error,
            user_id=user_id,
            correlation_id=correlation_id,
            request_duration_ms=duration_ms,
            is_timeout=True,
            additional_context={
                "timeout_threshold_seconds": timeout_seconds,
                "actual_duration_seconds": duration_ms / 1000
            }
        )
        raise timeout_error
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        await log_error(
            request,
            e,
            user_id=user_id,
            correlation_id=correlation_id,
            request_duration_ms=duration_ms,
            is_timeout=isinstance(e, (asyncio.TimeoutError, TimeoutError)),
        )
        raise
