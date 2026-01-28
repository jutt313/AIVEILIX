"""
OAuth Client Management Router

User-facing endpoints for managing OAuth clients (for ChatGPT integration, etc.)
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from app.models.oauth import (
    OAuthClientCreate,
    OAuthClientResponse,
    OAuthClientInfo,
)
from app.services.oauth2 import get_oauth2_service
from app.routers.buckets import get_current_user_id
from app.utils.error_logger import log_error, get_correlation_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


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
