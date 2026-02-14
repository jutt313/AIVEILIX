"""
OAuth2 Authentication Service for AIveilix MCP Server

Implements OAuth2 authorization code flow with PKCE (RFC 7636) for ChatGPT and other MCP clients.
"""
import hashlib
import secrets
import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, Request
from app.config import get_settings
from app.services.supabase import get_supabase
from app.models.oauth import (
    OAuthClientCreate,
    OAuthClientResponse,
    OAuthClientInfo,
    OAuthTokenResponse,
    OAuthAuthorizeRequest,
    OAuthTokenRequest,
)

settings = get_settings()
logger = logging.getLogger(__name__)


def generate_client_id() -> str:
    """Generate a unique client ID"""
    return f"mcp_{secrets.token_urlsafe(24)}"


def generate_client_secret() -> str:
    """Generate a secure client secret"""
    return secrets.token_urlsafe(48)


def generate_authorization_code() -> str:
    """Generate a secure authorization code"""
    return secrets.token_urlsafe(32)


def generate_access_token() -> str:
    """Generate a secure access token"""
    return secrets.token_urlsafe(48)


def generate_refresh_token() -> str:
    """Generate a secure refresh token"""
    return secrets.token_urlsafe(64)


def hash_secret(secret: str) -> str:
    """Hash a secret using SHA-256"""
    return hashlib.sha256(secret.encode()).hexdigest()


def base64url_encode(data: bytes) -> str:
    """Base64URL encode (RFC 4648 Section 5)"""
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def create_s256_code_challenge(code_verifier: str) -> str:
    """
    Create S256 code challenge from code verifier (RFC 7636).
    
    Returns: BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))
    """
    # SHA256 hash of code_verifier
    digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
    # Base64URL encode
    return base64url_encode(digest)


def verify_pkce_code_verifier(code_verifier: str, code_challenge: str, code_challenge_method: str) -> bool:
    """
    Verify PKCE code_verifier against code_challenge.
    
    Args:
        code_verifier: The code verifier from token request
        code_challenge: The stored code challenge from authorization request
        code_challenge_method: The method used (S256 or plain)
    
    Returns:
        True if verification succeeds, False otherwise
    """
    if code_challenge_method == "S256":
        expected_challenge = create_s256_code_challenge(code_verifier)
        return expected_challenge == code_challenge
    elif code_challenge_method == "plain":
        return code_verifier == code_challenge
    else:
        logger.warning(f"Unsupported code_challenge_method: {code_challenge_method}")
        return False


class OAuth2Service:
    """OAuth2 service for managing clients, codes, and tokens"""

    def __init__(self):
        self.supabase = get_supabase()

    # ==================== Client Management ====================

    async def create_client(
        self,
        user_id: str,
        client_data: OAuthClientCreate
    ) -> OAuthClientResponse:
        """Create a new OAuth client for a user"""
        client_id = generate_client_id()
        client_secret = generate_client_secret()
        client_secret_hash = hash_secret(client_secret)

        try:
            result = self.supabase.table("oauth_clients").insert({
                "client_id": client_id,
                "client_secret_hash": client_secret_hash,
                "user_id": user_id,
                "name": client_data.name,
                "redirect_uri": client_data.redirect_uri,
                "scopes": client_data.scopes,
                "is_active": True,
            }).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create OAuth client")

            logger.info(f"Created OAuth client {client_id} for user {user_id}")

            return OAuthClientResponse(
                client_id=client_id,
                client_secret=client_secret,  # Only returned once!
                name=client_data.name,
                redirect_uri=client_data.redirect_uri,
                scopes=client_data.scopes,
                created_at=datetime.fromisoformat(result.data[0]["created_at"].replace("Z", "+00:00"))
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating OAuth client: {e}")
            raise HTTPException(status_code=500, detail="Failed to create OAuth client")

    async def create_client_public(
        self,
        client_data: OAuthClientCreate
    ) -> OAuthClientResponse:
        """
        Create an OAuth client without a user association (for DCR).
        ChatGPT/Claude register before any user is authenticated.
        The user_id is set during the authorization flow.
        """
        client_id = generate_client_id()
        client_secret = generate_client_secret()
        client_secret_hash = hash_secret(client_secret)

        try:
            result = self.supabase.table("oauth_clients").insert({
                "client_id": client_id,
                "client_secret_hash": client_secret_hash,
                "user_id": None,
                "name": client_data.name,
                "redirect_uri": client_data.redirect_uri,
                "scopes": client_data.scopes,
                "is_active": True,
            }).execute()

            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create OAuth client")

            logger.info(f"Created public OAuth client {client_id} (no user)")

            return OAuthClientResponse(
                client_id=client_id,
                client_secret=client_secret,
                name=client_data.name,
                redirect_uri=client_data.redirect_uri,
                scopes=client_data.scopes,
                created_at=datetime.fromisoformat(result.data[0]["created_at"].replace("Z", "+00:00"))
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating public OAuth client: {e}")
            raise HTTPException(status_code=500, detail="Failed to create OAuth client")

    async def get_client(self, client_id: str) -> Optional[dict]:
        """Get client by client_id"""
        try:
            result = self.supabase.table("oauth_clients").select("*").eq(
                "client_id", client_id
            ).eq("is_active", True).single().execute()
            return result.data
        except Exception:
            return None

    async def validate_client(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None
    ) -> Tuple[bool, Optional[dict]]:
        """Validate client credentials"""
        client = await self.get_client(client_id)
        
        if not client:
            return False, None

        # Validate client_secret if provided
        if client_secret:
            secret_hash = hash_secret(client_secret)
            if secret_hash != client["client_secret_hash"]:
                return False, None

        # Validate redirect_uri if provided
        if redirect_uri and redirect_uri != client["redirect_uri"]:
            return False, None

        return True, client

    async def list_user_clients(self, user_id: str) -> list[OAuthClientInfo]:
        """List all OAuth clients for a user"""
        try:
            result = self.supabase.table("oauth_clients").select(
                "client_id, name, redirect_uri, scopes, created_at, is_active"
            ).eq("user_id", user_id).order("created_at", desc=True).execute()

            return [
                OAuthClientInfo(
                    client_id=c["client_id"],
                    name=c["name"],
                    redirect_uri=c["redirect_uri"],
                    scopes=c.get("scopes", []),
                    created_at=datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")),
                    is_active=c.get("is_active", True)
                )
                for c in result.data or []
            ]
        except Exception as e:
            logger.error(f"Error listing OAuth clients: {e}")
            return []

    async def revoke_client(self, user_id: str, client_id: str) -> bool:
        """Revoke an OAuth client"""
        try:
            result = self.supabase.table("oauth_clients").update({
                "is_active": False
            }).eq("client_id", client_id).eq("user_id", user_id).execute()
            
            if result.data:
                # Also revoke all tokens for this client
                self.supabase.table("oauth_tokens").update({
                    "is_revoked": True
                }).eq("client_id", client_id).execute()
                logger.info(f"Revoked OAuth client {client_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error revoking OAuth client: {e}")
            return False

    # ==================== Authorization Code ====================

    async def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scope: str,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        resource: Optional[str] = None
    ) -> str:
        """
        Create an authorization code for the OAuth flow with PKCE support.
        
        Args:
            client_id: OAuth client ID
            user_id: User ID
            redirect_uri: Redirect URI
            scope: Requested scopes
            code_challenge: PKCE code challenge (optional but recommended)
            code_challenge_method: PKCE method (S256 or plain, default S256)
            resource: RFC 8707 Resource Indicator (optional)
        """
        code = generate_authorization_code()
        code_hash = hash_secret(code)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        # Default to S256 if challenge provided but method not specified
        if code_challenge and not code_challenge_method:
            code_challenge_method = "S256"
        
        # Validate code_challenge_method
        if code_challenge_method and code_challenge_method not in ["S256", "plain"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported code_challenge_method: {code_challenge_method}. Supported: S256, plain"
            )

        try:
            insert_data = {
                "code_hash": code_hash,
                "client_id": client_id,
                "user_id": user_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "expires_at": expires_at.isoformat(),
                "used": False,
            }
            
            # Add PKCE fields if provided
            if code_challenge:
                insert_data["code_challenge"] = code_challenge
                insert_data["code_challenge_method"] = code_challenge_method or "S256"
            
            # Add resource if provided
            if resource:
                insert_data["resource"] = resource
            
            self.supabase.table("oauth_authorization_codes").insert(insert_data).execute()

            logger.info(f"Created authorization code for client {client_id}, user {user_id}, PKCE: {bool(code_challenge)}")
            return code
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating authorization code: {e}")
            raise HTTPException(status_code=500, detail="Failed to create authorization code")

    async def validate_authorization_code(
        self,
        code: str,
        client_id: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Optional[dict]:
        """
        Validate and consume an authorization code with optional PKCE verification.
        
        Args:
            code: Authorization code
            client_id: OAuth client ID
            redirect_uri: Redirect URI
            code_verifier: PKCE code verifier (required if code_challenge was provided)
        
        Returns:
            Code data dict if valid, None otherwise
        """
        code_hash = hash_secret(code)

        try:
            # Find the code
            result = self.supabase.table("oauth_authorization_codes").select("*").eq(
                "code_hash", code_hash
            ).eq("client_id", client_id).eq("redirect_uri", redirect_uri).eq(
                "used", False
            ).single().execute()

            if not result.data:
                logger.warning(f"Authorization code not found or already used: client={client_id}")
                return None

            code_data = result.data

            # Check expiration
            expires_at = datetime.fromisoformat(code_data["expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"Authorization code expired for client {client_id}")
                return None

            # Verify PKCE if code_challenge was stored
            stored_challenge = code_data.get("code_challenge")
            stored_method = code_data.get("code_challenge_method")
            
            if stored_challenge:
                # PKCE is required for this code
                if not code_verifier:
                    logger.warning(f"PKCE code_verifier required but not provided: client={client_id}")
                    return None
                
                if not verify_pkce_code_verifier(code_verifier, stored_challenge, stored_method or "S256"):
                    logger.warning(f"PKCE verification failed: client={client_id}")
                    return None
                
                logger.info(f"PKCE verification successful: client={client_id}")
            elif code_verifier:
                # Code verifier provided but no challenge stored (optional PKCE)
                logger.debug(f"Code verifier provided but no challenge stored: client={client_id}")

            # Mark as used
            self.supabase.table("oauth_authorization_codes").update({
                "used": True
            }).eq("id", code_data["id"]).execute()

            return code_data
        except Exception as e:
            logger.error(f"Error validating authorization code: {e}")
            return None

    # ==================== Token Management ====================

    async def create_tokens(
        self,
        client_id: str,
        user_id: str,
        scope: str,
        resource: Optional[str] = None,
        audience: Optional[str] = None
    ) -> OAuthTokenResponse:
        """
        Create access and refresh tokens with resource and audience support.
        
        Args:
            client_id: OAuth client ID
            user_id: User ID
            scope: Token scopes
            resource: RFC 8707 Resource Indicator (optional)
            audience: Token audience, typically MCP server URL (optional)
        """
        access_token = generate_access_token()
        refresh_token = generate_refresh_token()
        
        access_token_hash = hash_secret(access_token)
        refresh_token_hash = hash_secret(refresh_token)
        
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.oauth_token_expire_minutes)
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.oauth_refresh_token_expire_days)
        
        # Set default audience to MCP server URL if not provided
        if not audience:
            audience = f"{settings.backend_url.rstrip('/')}/mcp/server"

        try:
            insert_data = {
                "access_token_hash": access_token_hash,
                "refresh_token_hash": refresh_token_hash,
                "client_id": client_id,
                "user_id": user_id,
                "scope": scope,
                "expires_at": expires_at.isoformat(),
                "refresh_expires_at": refresh_expires_at.isoformat(),
                "is_revoked": False,
                "audience": audience,
            }
            
            # Add resource if provided
            if resource:
                insert_data["resource"] = resource
            
            self.supabase.table("oauth_tokens").insert(insert_data).execute()

            logger.info(f"Created tokens for client {client_id}, user {user_id}, audience={audience}")

            # Create response dict to include all fields
            response_dict = {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.oauth_token_expire_minutes * 60,
                "refresh_token": refresh_token,
                "scope": scope,
                "aud": audience
            }
            
            if resource:
                response_dict["resource"] = resource
            
            return OAuthTokenResponse(**response_dict)
        except Exception as e:
            logger.error(f"Error creating tokens: {e}")
            raise HTTPException(status_code=500, detail="Failed to create tokens")

    async def validate_access_token(self, access_token: str) -> Optional[dict]:
        """Validate an access token and return token data"""
        token_hash = hash_secret(access_token)

        try:
            result = self.supabase.table("oauth_tokens").select("*").eq(
                "access_token_hash", token_hash
            ).eq("is_revoked", False).single().execute()

            if not result.data:
                return None

            token_data = result.data

            # Check expiration
            expires_at = datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"Access token expired for client {token_data['client_id']}")
                return None

            return token_data
        except Exception as e:
            logger.error(f"Error validating access token: {e}")
            return None

    async def refresh_tokens(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str
    ) -> Optional[OAuthTokenResponse]:
        """Refresh access token using refresh token"""
        # Validate client
        valid, client = await self.validate_client(client_id, client_secret)
        if not valid:
            return None

        refresh_token_hash = hash_secret(refresh_token)

        try:
            # Find the refresh token
            result = self.supabase.table("oauth_tokens").select("*").eq(
                "refresh_token_hash", refresh_token_hash
            ).eq("client_id", client_id).eq("is_revoked", False).single().execute()

            if not result.data:
                return None

            token_data = result.data

            # Check refresh token expiration
            refresh_expires_at = datetime.fromisoformat(token_data["refresh_expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > refresh_expires_at:
                logger.warning(f"Refresh token expired for client {client_id}")
                return None

            # Revoke old tokens
            self.supabase.table("oauth_tokens").update({
                "is_revoked": True
            }).eq("id", token_data["id"]).execute()

            # Create new tokens (preserve resource and audience from original token)
            return await self.create_tokens(
                client_id=client_id,
                user_id=token_data["user_id"],
                scope=token_data["scope"],
                resource=token_data.get("resource"),
                audience=token_data.get("audience")
            )
        except Exception as e:
            logger.error(f"Error refreshing tokens: {e}")
            return None

    async def refresh_tokens_public(
        self,
        refresh_token: str,
        client_id: str
    ) -> Optional[OAuthTokenResponse]:
        """Refresh access token for public clients (no client_secret)"""
        # Just validate client exists (no secret check)
        client = await self.get_client(client_id)
        if not client:
            return None

        refresh_token_hash = hash_secret(refresh_token)

        try:
            result = self.supabase.table("oauth_tokens").select("*").eq(
                "refresh_token_hash", refresh_token_hash
            ).eq("client_id", client_id).eq("is_revoked", False).single().execute()

            if not result.data:
                return None

            token_data = result.data

            # Check refresh token expiration
            refresh_expires_at = datetime.fromisoformat(token_data["refresh_expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > refresh_expires_at:
                logger.warning(f"Refresh token expired for public client {client_id}")
                return None

            # Revoke old tokens
            self.supabase.table("oauth_tokens").update({
                "is_revoked": True
            }).eq("id", token_data["id"]).execute()

            # Create new tokens
            return await self.create_tokens(
                client_id=client_id,
                user_id=token_data["user_id"],
                scope=token_data["scope"],
                resource=token_data.get("resource"),
                audience=token_data.get("audience")
            )
        except Exception as e:
            logger.error(f"Error refreshing tokens (public): {e}")
            return None

    async def revoke_token(self, access_token: str) -> bool:
        """Revoke an access token"""
        token_hash = hash_secret(access_token)

        try:
            result = self.supabase.table("oauth_tokens").update({
                "is_revoked": True
            }).eq("access_token_hash", token_hash).execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """Revoke all tokens for a user"""
        try:
            self.supabase.table("oauth_tokens").update({
                "is_revoked": True
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Revoked all tokens for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error revoking user tokens: {e}")
            return False


# Singleton instance
_oauth2_service: Optional[OAuth2Service] = None


def get_oauth2_service() -> OAuth2Service:
    """Get OAuth2 service singleton"""
    global _oauth2_service
    if _oauth2_service is None:
        _oauth2_service = OAuth2Service()
    return _oauth2_service
