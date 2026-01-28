"""OAuth2 request and response models for MCP authentication"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OAuthGrantType(str, Enum):
    """Supported OAuth grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class OAuthResponseType(str, Enum):
    """Supported OAuth response types"""
    CODE = "code"


class OAuthScope(str, Enum):
    """Available OAuth scopes"""
    READ_BUCKETS = "read:buckets"
    WRITE_BUCKETS = "write:buckets"
    READ_FILES = "read:files"
    QUERY = "query"
    CHAT = "chat"


# Request Models
class OAuthAuthorizeRequest(BaseModel):
    """OAuth authorization request parameters"""
    response_type: str = Field(..., description="Must be 'code'")
    client_id: str = Field(..., description="OAuth client ID")
    redirect_uri: str = Field(..., description="Callback URL")
    scope: Optional[str] = Field(default="read:buckets read:files query chat", description="Space-separated scopes")
    state: Optional[str] = Field(default=None, description="CSRF state token")
    code_challenge: Optional[str] = Field(default=None, description="PKCE code challenge (RFC 7636)")
    code_challenge_method: Optional[str] = Field(default="S256", description="PKCE method: S256 or plain")
    resource: Optional[str] = Field(default=None, description="RFC 8707 Resource Indicator")


class OAuthTokenRequest(BaseModel):
    """OAuth token exchange request"""
    grant_type: str = Field(..., description="Grant type: authorization_code or refresh_token")
    code: Optional[str] = Field(default=None, description="Authorization code (for authorization_code grant)")
    redirect_uri: Optional[str] = Field(default=None, description="Redirect URI (for authorization_code grant)")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token (for refresh_token grant)")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    code_verifier: Optional[str] = Field(default=None, description="PKCE code verifier (required if code_challenge was provided)")
    resource: Optional[str] = Field(default=None, description="RFC 8707 Resource Indicator")


class OAuthClientCreate(BaseModel):
    """Create new OAuth client"""
    name: str = Field(..., min_length=1, max_length=100, description="Client application name")
    redirect_uri: str = Field(..., description="Authorized redirect URI")
    scopes: List[str] = Field(default=["read:buckets", "read:files", "query", "chat"], description="Allowed scopes")


# Response Models
class OAuthTokenResponse(BaseModel):
    """OAuth token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None
    scope: str
    aud: Optional[str] = Field(default=None, description="Token audience")
    resource: Optional[str] = Field(default=None, description="RFC 8707 Resource Indicator")


class OAuthClientResponse(BaseModel):
    """OAuth client details (returned after creation)"""
    client_id: str
    client_secret: str  # Only shown once on creation
    name: str
    redirect_uri: str
    scopes: List[str]
    created_at: datetime


class OAuthClientInfo(BaseModel):
    """OAuth client info (without secret)"""
    client_id: str
    name: str
    redirect_uri: str
    scopes: List[str]
    created_at: datetime
    is_active: bool


class OAuthErrorResponse(BaseModel):
    """OAuth error response per RFC 6749"""
    error: str  # error code
    error_description: Optional[str] = None
    error_uri: Optional[str] = None


# Database Models (for service layer)
class OAuthClientDB(BaseModel):
    """OAuth client database record"""
    id: str
    client_id: str
    client_secret_hash: str
    user_id: str
    name: str
    redirect_uri: str
    scopes: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class OAuthAuthorizationCodeDB(BaseModel):
    """OAuth authorization code database record"""
    id: str
    code_hash: str
    client_id: str
    user_id: str
    redirect_uri: str
    scope: str
    expires_at: datetime
    used: bool = False
    created_at: datetime


class OAuthTokenDB(BaseModel):
    """OAuth token database record"""
    id: str
    access_token_hash: str
    refresh_token_hash: Optional[str] = None
    client_id: str
    user_id: str
    scope: str
    expires_at: datetime
    refresh_expires_at: Optional[datetime] = None
    is_revoked: bool = False
    created_at: datetime


# MCP-specific models
class MCPUser(BaseModel):
    """Unified user model for MCP authentication"""
    user_id: str
    auth_type: str  # 'oauth' or 'api_key'
    client_id: Optional[str] = None  # For OAuth
    api_key_id: Optional[str] = None  # For API key
    scopes: List[str]
    allowed_buckets: Optional[List[str]] = None  # None = all buckets
