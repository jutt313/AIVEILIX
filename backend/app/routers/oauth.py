"""
OAuth Client Management Router

User-facing endpoints for managing OAuth clients (for ChatGPT integration, etc.)
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Form, Query
from fastapi.responses import RedirectResponse
from typing import List, Optional
from app.models.oauth import (
    OAuthClientCreate,
    OAuthClientResponse,
    OAuthClientInfo,
    OAuthTokenResponse,
    OAuthErrorResponse,
)
from app.services.oauth2 import get_oauth2_service
from app.routers.buckets import get_current_user_id
from app.utils.error_logger import log_error, get_correlation_id
import logging
from urllib.parse import urlencode

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== OAuth Authorization Flow ====================

@router.get("/authorize")
async def authorize(
    response_type: str = Query(..., description="Must be 'code'"),
    client_id: str = Query(..., description="OAuth client ID"),
    redirect_uri: str = Query(..., description="Callback URL"),
    scope: Optional[str] = Query(default="read:buckets read:files query chat", description="Space-separated scopes"),
    state: Optional[str] = Query(default=None, description="CSRF state token"),
    code_challenge: Optional[str] = Query(default=None, description="PKCE code challenge"),
    code_challenge_method: Optional[str] = Query(default="S256", description="PKCE method: S256 or plain"),
    resource: Optional[str] = Query(default=None, description="Resource indicator"),
    user_id: str = Depends(get_current_user_id),
):
    """
    OAuth2 Authorization Endpoint (RFC 6749)

    User must be authenticated (JWT token). Validates client and creates authorization code.
    Redirects to redirect_uri with code parameter.
    """
    try:
        oauth_service = get_oauth2_service()

        # Validate response_type
        if response_type != "code":
            error_params = {
                "error": "unsupported_response_type",
                "error_description": "Only 'code' response_type is supported"
            }
            if state:
                error_params["state"] = state
            return RedirectResponse(url=f"{redirect_uri}?{urlencode(error_params)}")

        # Validate client and redirect_uri
        valid, client = await oauth_service.validate_client(
            client_id=client_id,
            redirect_uri=redirect_uri
        )

        if not valid or not client:
            raise HTTPException(
                status_code=400,
                detail="Invalid client_id or redirect_uri"
            )

        logger.info(f"Authorization request: client={client_id}, user={user_id}, PKCE={bool(code_challenge)}")

        # Create authorization code with PKCE
        code = await oauth_service.create_authorization_code(
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scope=scope or "read:buckets read:files query chat",
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method if code_challenge else None,
            resource=resource
        )

        # Redirect back to client with code
        redirect_params = {"code": code}
        if state:
            redirect_params["state"] = state

        redirect_url = f"{redirect_uri}?{urlencode(redirect_params)}"
        logger.info(f"Authorization granted: client={client_id}, user={user_id}")

        return RedirectResponse(url=redirect_url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authorization error: {e}")
        error_params = {
            "error": "server_error",
            "error_description": "Internal server error"
        }
        if state:
            error_params["state"] = state
        return RedirectResponse(url=f"{redirect_uri}?{urlencode(error_params)}")


@router.post("/token", response_model=OAuthTokenResponse)
async def token(
    grant_type: str = Form(..., description="Grant type: authorization_code or refresh_token"),
    client_id: str = Form(..., description="OAuth client ID"),
    client_secret: str = Form(..., description="OAuth client secret"),
    code: Optional[str] = Form(default=None, description="Authorization code"),
    redirect_uri: Optional[str] = Form(default=None, description="Redirect URI"),
    refresh_token: Optional[str] = Form(default=None, description="Refresh token"),
    code_verifier: Optional[str] = Form(default=None, description="PKCE code verifier"),
    resource: Optional[str] = Form(default=None, description="Resource indicator"),
):
    """
    OAuth2 Token Endpoint (RFC 6749)

    Exchanges authorization code for access token, or refreshes access token.
    Supports PKCE (RFC 7636) and resource indicators (RFC 8707).
    """
    try:
        oauth_service = get_oauth2_service()

        # Handle authorization_code grant
        if grant_type == "authorization_code":
            if not code or not redirect_uri:
                raise HTTPException(
                    status_code=400,
                    detail="code and redirect_uri are required for authorization_code grant"
                )

            # Validate client credentials
            valid, client = await oauth_service.validate_client(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
            )

            if not valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid client credentials"
                )

            # Validate and consume authorization code with PKCE
            code_data = await oauth_service.validate_authorization_code(
                code=code,
                client_id=client_id,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier
            )

            if not code_data:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or expired authorization code"
                )

            logger.info(f"Token exchange: client={client_id}, user={code_data['user_id']}")

            # Create access and refresh tokens
            tokens = await oauth_service.create_tokens(
                client_id=client_id,
                user_id=code_data["user_id"],
                scope=code_data["scope"],
                resource=resource or code_data.get("resource")
            )

            return tokens

        # Handle refresh_token grant
        elif grant_type == "refresh_token":
            if not refresh_token:
                raise HTTPException(
                    status_code=400,
                    detail="refresh_token is required for refresh_token grant"
                )

            logger.info(f"Token refresh: client={client_id}")

            # Refresh tokens
            tokens = await oauth_service.refresh_tokens(
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret
            )

            if not tokens:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token or client credentials"
                )

            return tokens

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported grant_type: {grant_type}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to issue token"
        )


# ==================== OAuth Client Management ====================

@router.post("/clients", response_model=OAuthClientResponse)
async def create_oauth_client(
    request: OAuthClientCreate,
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new OAuth client for the authenticated user.
    Returns client_id and client_secret (secret only shown once).
    """
    correlation_id = get_correlation_id(http_request)
    try:
        oauth_service = get_oauth2_service()
        
        logger.info(f"Creating OAuth client: user_id={user_id}, name={request.name}")
        
        client = await oauth_service.create_client(
            user_id=user_id,
            client_data=request
        )
        
        logger.info(f"OAuth client created: client_id={client.client_id}, user_id={user_id}")
        
        return client
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create OAuth client: {str(e)}"
        )


@router.get("/clients", response_model=List[OAuthClientInfo])
async def list_oauth_clients(
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """List all OAuth clients for the authenticated user"""
    correlation_id = get_correlation_id(http_request)
    try:
        oauth_service = get_oauth2_service()
        
        clients = await oauth_service.list_user_clients(user_id)
        
        logger.info(f"Listed OAuth clients: user_id={user_id}, count={len(clients)}")
        
        return clients
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list OAuth clients: {str(e)}"
        )


@router.delete("/clients/{client_id}")
async def delete_oauth_client(
    client_id: str,
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """Revoke/delete an OAuth client"""
    correlation_id = get_correlation_id(http_request)
    try:
        oauth_service = get_oauth2_service()
        
        success = await oauth_service.revoke_client(user_id, client_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="OAuth client not found")
        
        logger.info(f"OAuth client revoked: client_id={client_id}, user_id={user_id}")
        
        return {"success": True, "message": "OAuth client revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to revoke OAuth client: {str(e)}"
        )
