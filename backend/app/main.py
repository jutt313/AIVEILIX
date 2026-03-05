from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import get_settings
import traceback
import logging
import uuid
import time
from collections import deque, defaultdict
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.limiter import limiter

settings = get_settings()

# ── Local dev error store ─────────────────────────────────────────────────────
# Keeps the last 200 errors in memory. View at GET /dev/errors (localhost only).
_error_store: deque = deque(maxlen=200)

def _capture_error(request: Request, exc: Exception, context: str = "") -> str:
    error_id = str(uuid.uuid4())[:8]
    _error_store.appendleft({
        "id": error_id,
        "timestamp": datetime.now().isoformat(),
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
        "context": context,
        "request": {
            "method": request.method,
            "path": request.url.path,
            "url": str(request.url),
            "origin": request.headers.get("origin", ""),
            "content_type": request.headers.get("content-type", ""),
        },
    })
    return error_id
# ─────────────────────────────────────────────────────────────────────────────

# Setup rate limiter (disabled for OPTIONS/CORS preflight)
limiter.default_limits = ["200/minute"]

# Setup Sentry error tracking (before anything else)
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env or "development",
        traces_sample_rate=0.1,  # 10% of requests for performance monitoring
        profiles_sample_rate=0.1,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        send_default_pii=False,  # Don't send personal info
    )
    logging.info("✅ Sentry error tracking initialized")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Suppress noisy third-party HTTP loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("voyageai").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIveilix API",
    description="Knowledge bucket platform API",
    version="0.1.0",
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for frontend and OAuth
_cors_origins = [
    settings.frontend_url,
    # Production frontend
    "https://aiveilix.com",
    "https://www.aiveilix.com",
    # Production backend (for same-origin requests)
    "https://api.aiveilix.com",
    # Local development
    "http://localhost:6677",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:6677",
    "http://127.0.0.1:5173",
    # OAuth / MCP partners
    "https://chat.openai.com",
    "https://chatgpt.com",
    "https://claude.ai",
]
# Remove None values
_cors_origins = [o for o in _cors_origins if o]
if settings.cors_extra_origins:
    _cors_origins.extend(o.strip() for o in settings.cors_extra_origins.split(",") if o.strip())

# Log allowed origins on startup for debugging
logger.info(f"✅ CORS allowed origins: {_cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length", "Content-Range", "X-Response-Time"],
)


# ── Per-endpoint timing stats (in-memory, resets on restart) ─────────────────
_timing_stats: dict = defaultdict(lambda: {"count": 0, "total_ms": 0, "min_ms": float("inf"), "max_ms": 0, "errors": 0})
_SLOW_WARN_MS  = 1000   # log WARNING above this
_SLOW_ERROR_MS = 5000   # log ERROR above this

def _record_timing(key: str, ms: float, is_error: bool):
    s = _timing_stats[key]
    s["count"]    += 1
    s["total_ms"] += ms
    s["min_ms"]    = min(s["min_ms"], ms)
    s["max_ms"]    = max(s["max_ms"], ms)
    if is_error:
        s["errors"] += 1
# ─────────────────────────────────────────────────────────────────────────────


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    """Track timing for every request; add X-Response-Time header."""
    method  = request.method
    path    = request.url.path
    origin  = request.headers.get("origin", "")

    # Skip OPTIONS — no useful timing info
    if method == "OPTIONS":
        if settings.app_env == "development":
            logger.debug(f"🔍 OPTIONS {path}  origin={origin}")
        return await call_next(request)

    t0 = time.perf_counter()
    status_code = 500
    try:
        response   = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        error_id = _capture_error(request, e, context="middleware")
        logger.error(f"💥 [{error_id}] EXCEPTION: {method} {path} — {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        ms  = round((time.perf_counter() - t0) * 1000, 1)
        key = f"{method} {path}"
        is_error = status_code >= 400
        _record_timing(key, ms, is_error)

        # Speed emoji
        if ms >= _SLOW_ERROR_MS:
            speed = "🔴 VERY SLOW"
            log = logger.error
        elif ms >= _SLOW_WARN_MS:
            speed = "🟡 SLOW"
            log = logger.warning
        else:
            speed = "🟢"
            log = logger.info

        log(f"⏱  {method} {path}  →  {status_code}  {ms}ms  {speed}")

    # Attach timing to response header (visible in browser Network tab)
    response.headers["X-Response-Time"] = f"{ms}ms"
    if status_code == 400:
        logger.error(f"❌ 400 BAD REQUEST: {method} {path}")
    return response


@app.get("/")
async def root():
    return {"message": "AIveilix API", "status": "running"}


@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    """Handle CORS preflight requests explicitly"""
    return JSONResponse(content={"status": "ok"}, status_code=200)


@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}


# ==================== OAuth Discovery Endpoints ====================

@app.api_route("/.well-known/oauth-authorization-server", methods=["GET", "POST"])
async def oauth_authorization_server(request: Request):
    """OAuth2 Authorization Server Metadata (RFC 8414) - Supports both GET and POST"""
    base_url = settings.backend_url.rstrip('/')
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/mcp/server/oauth/authorize",
        "token_endpoint": f"{base_url}/mcp/server/oauth/token",
        "registration_endpoint": f"{base_url}/mcp/server/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["read:buckets", "read:files", "query", "chat", "offline_access"],
        "revocation_endpoint": f"{base_url}/mcp/server/oauth/revoke",
        "mcp_endpoint": f"{base_url}/mcp/server",
        "mcp_sse_endpoint": f"{base_url}/mcp/server/protocol/sse"
    }


@app.api_route("/.well-known/oauth-protected-resource", methods=["GET", "POST"])
async def oauth_protected_resource():
    """OAuth2 Protected Resource Metadata - Supports both GET and POST"""
    return {
        "resource": "AIveilix MCP Server",
        "scopes_supported": ["read:buckets", "read:files", "query", "chat", "offline_access"]
    }


@app.api_route("/.well-known/openid-configuration", methods=["GET", "POST"])
async def openid_configuration(request: Request):
    """OpenID Connect Discovery (for ChatGPT compatibility) - Supports both GET and POST"""
    base_url = settings.backend_url.rstrip('/')
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/mcp/server/oauth/authorize",
        "token_endpoint": f"{base_url}/mcp/server/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "mcp_endpoint": f"{base_url}/mcp/server",
        "mcp_sse_endpoint": f"{base_url}/mcp/server/protocol/sse"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    error_id = _capture_error(request, exc, context="global_exception_handler")
    logger.error(f"[{error_id}] Unhandled exception: {exc}", exc_info=True)

    if settings.sentry_dsn:
        sentry_sdk.set_context("request", {
            "url": str(request.url),
            "method": request.method,
            "error_id": error_id,
        })
        sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred",
            "error_id": error_id,
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    
    # Convert errors to serializable format (handle bytes in input)
    errors = []
    for error in exc.errors():
        error_dict = dict(error)
        # Convert bytes to string if present
        if 'input' in error_dict and isinstance(error_dict['input'], bytes):
            try:
                error_dict['input'] = error_dict['input'].decode('utf-8')
            except:
                error_dict['input'] = '<bytes>'
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "type": "ValidationError",
            "path": str(request.url),
        }
    )


# ── Dev error viewer endpoints (development only) ─────────────────────────────
@app.get("/dev/errors", tags=["dev"])
async def get_dev_errors(request: Request, limit: int = 50):
    """View recent backend errors (local dev only). Latest first."""
    if settings.app_env != "development":
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    errors = list(_error_store)[:limit]
    return {
        "total": len(_error_store),
        "showing": len(errors),
        "errors": errors,
    }

@app.delete("/dev/errors", tags=["dev"])
async def clear_dev_errors(request: Request):
    """Clear the in-memory error store."""
    if settings.app_env != "development":
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    _error_store.clear()
    return {"message": "Error store cleared"}


@app.get("/dev/timing", tags=["dev"])
async def get_timing_stats(request: Request, sort: str = "avg"):
    """
    Live per-endpoint timing stats since last restart.
    sort options: avg | max | count | errors
    No auth required — restrict to internal use only.
    """
    rows = []
    for endpoint, s in _timing_stats.items():
        n = s["count"]
        if n == 0:
            continue
        avg_ms = round(s["total_ms"] / n, 1)
        rows.append({
            "endpoint":   endpoint,
            "count":      n,
            "avg_ms":     avg_ms,
            "min_ms":     round(s["min_ms"], 1),
            "max_ms":     round(s["max_ms"], 1),
            "errors":     s["errors"],
            "error_rate": f"{round(s['errors'] / n * 100, 1)}%",
            "flag":       "🔴" if avg_ms >= _SLOW_ERROR_MS else "🟡" if avg_ms >= _SLOW_WARN_MS else "🟢",
        })

    sort_key = {"avg": "avg_ms", "max": "max_ms", "count": "count", "errors": "errors"}.get(sort, "avg_ms")
    rows.sort(key=lambda r: r[sort_key], reverse=True)

    return {
        "endpoints_tracked": len(rows),
        "sort_by": sort,
        "thresholds": {"warn_ms": _SLOW_WARN_MS, "error_ms": _SLOW_ERROR_MS},
        "stats": rows,
    }


@app.delete("/dev/timing", tags=["dev"])
async def clear_timing_stats():
    """Reset all timing stats."""
    _timing_stats.clear()
    return {"message": "Timing stats cleared"}
# ─────────────────────────────────────────────────────────────────────────────

# Routers
from app.routers import auth, buckets, files, chat, api_keys, mcp, mcp_server, oauth, notifications, stripe, team
from app.routers import processing_stream
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(buckets.router, prefix="/api/buckets", tags=["buckets"])
app.include_router(files.router, prefix="/api/buckets", tags=["files"])
app.include_router(processing_stream.router, tags=["processing-stream"])
app.include_router(chat.router, prefix="/api/buckets", tags=["chat"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys"])
app.include_router(oauth.router, prefix="/api/oauth", tags=["oauth"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(stripe.router, prefix="/api/stripe", tags=["stripe"])
app.include_router(team.router, prefix="/api/team", tags=["team"])
app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# MCP Protocol Server routes (for ChatGPT and Cursor integration)
app.include_router(mcp_server.router, prefix="/mcp/server", tags=["mcp-protocol"])


# Direct /mcp/server route - Claude.ai hits this exact path (no trailing slash)
# FastAPI router prefix creates /mcp/server/ but Claude sends to /mcp/server
@app.api_route("/mcp/server", methods=["GET", "POST", "OPTIONS"])
async def mcp_server_root(request: Request):
    """Handle /mcp/server directly for Claude.ai MCP integration"""
    from app.routers.mcp_server import mcp_protocol_endpoint, mcp_sse_endpoint
    authorization = request.headers.get("authorization")
    if request.method == "POST":
        return await mcp_protocol_endpoint(request, authorization)
    elif request.method == "GET":
        return await mcp_sse_endpoint(request, authorization)
    else:
        return JSONResponse(content={"status": "ok"}, status_code=200)
