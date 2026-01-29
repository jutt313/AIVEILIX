from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import get_settings
import traceback
import logging

settings = get_settings()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIveilix API",
    description="Knowledge bucket platform API",
    version="0.1.0",
)

# CORS for frontend and OAuth
_cors_origins = [
    settings.frontend_url,
    "http://localhost:6677",
    "https://aiveilix-frontend.onrender.com",  # Production frontend (Render)
    "https://chat.openai.com",  # ChatGPT OAuth
    "https://chatgpt.com",  # ChatGPT new domain
]
if settings.cors_extra_origins:
    _cors_origins.extend(o.strip() for o in settings.cors_extra_origins.split(",") if o.strip())
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "AIveilix API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}


# ==================== OAuth Discovery Endpoints ====================

@app.api_route("/.well-known/oauth-authorization-server", methods=["GET", "POST"])
async def oauth_authorization_server(request: Request):
    """OAuth2 Authorization Server Metadata (RFC 8414) - Supports both GET and POST"""
    base_url = str(request.base_url).rstrip('/')
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/mcp/server/oauth/authorize",
        "token_endpoint": f"{base_url}/mcp/server/oauth/token",
        "registration_endpoint": f"{base_url}/mcp/server/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["read:buckets", "read:files", "query", "chat", "offline_access"],
        "revocation_endpoint": f"{base_url}/mcp/server/oauth/revoke",
        "mcp_endpoint": f"{base_url}/mcp/server/protocol",
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
    base_url = str(request.base_url).rstrip('/')
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/mcp/server/oauth/authorize",
        "token_endpoint": f"{base_url}/mcp/server/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "mcp_endpoint": f"{base_url}/mcp/server/protocol",
        "mcp_sse_endpoint": f"{base_url}/mcp/server/protocol/sse"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url),
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


# Routers
from app.routers import auth, buckets, files, chat, api_keys, mcp, mcp_server, oauth, notifications
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(buckets.router, prefix="/api/buckets", tags=["buckets"])
app.include_router(files.router, prefix="/api/buckets", tags=["files"])
app.include_router(chat.router, prefix="/api/buckets", tags=["chat"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys"])
app.include_router(oauth.router, prefix="/api/oauth", tags=["oauth"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])

# MCP Protocol Server routes (for ChatGPT and Cursor integration)
app.include_router(mcp_server.router, prefix="/mcp/server", tags=["mcp-protocol"])
