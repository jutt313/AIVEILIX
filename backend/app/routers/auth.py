from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
from app.models.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    AuthResponse,
)
from app.services.supabase import get_supabase_auth, get_supabase
from app.routers.buckets import get_current_user_id
from app.config import get_settings
from app.utils.error_logger import log_error, get_correlation_id
from app.services import email_service
import logging
import traceback
router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=AuthResponse)
async def signup(signup_request: SignupRequest, request: Request):
    """Create a new user account"""
    correlation_id = get_correlation_id(request)
    try:
        supabase = get_supabase_auth()
        
        response = supabase.auth.sign_up({
            "email": signup_request.email,
            "password": signup_request.password,
            "options": {
                "data": {
                    "full_name": signup_request.full_name or ""
                }
            }
        })
        
        if response.user:
            return AuthResponse(
                success=True,
                message="Account created. Please check your email to verify.",
                user={
                    "id": str(response.user.id),
                    "email": response.user.email,
                    "full_name": signup_request.full_name
                }
            )
        else:
            return AuthResponse(
                success=False,
                message="Failed to create account"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Auth error: {error_trace}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(login_request: LoginRequest, request: Request):
    """Login with email and password"""
    correlation_id = get_correlation_id(request)
    try:
        supabase = get_supabase_auth()
        
        response = supabase.auth.sign_in_with_password({
            "email": login_request.email,
            "password": login_request.password
        })
        
        if response.user and response.session:
            return AuthResponse(
                success=True,
                message="Login successful",
                user={
                    "id": str(response.user.id),
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name", "")
                },
                session={
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            )
        else:
            return AuthResponse(
                success=False,
                message="Invalid credentials"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Auth error: {error_trace}")
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(request: ForgotPasswordRequest, http_request: Request):
    """Send password reset email"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase = get_supabase_auth()
        
        # Custom Password Reset Flow
        # 1. Generate recovery link using Admin client
        supabase_admin = get_supabase()
        try:
             # Generates link but doesn't send email (if configured correctly, or we ignore Supabase one)
             # actually generate_link always returns link, doesn't send email usually (invite does)
             link_res = supabase_admin.auth.admin.generate_link({
                 "type": "recovery",
                 "email": request.email,
                 "options": {
                     "redirect_to": f"{settings.frontend_url}/reset-password"
                 }
             })
             
             if link_res and link_res.properties and link_res.properties.action_link:
                 # 2. Send custom email
                 email_service.send_password_reset_email(
                     to_email=request.email,
                     reset_link=link_res.properties.action_link
                 )
        except Exception as admin_err:
             # Fallback to standard flow if admin fails (or user not found?)
             logger.warning(f"Failed to generate custom link: {admin_err}")
             supabase.auth.reset_password_for_email(
                 request.email,
                 {
                     "redirect_to": f"{settings.frontend_url}/reset-password"
                 }
             )
        
        return AuthResponse(
            success=True,
            message="If an account exists, a password reset link has been sent."
        )
        
    except Exception as e:
        await log_error(http_request, e, correlation_id=correlation_id)
        # Don't reveal if email exists or not
        return AuthResponse(
            success=True,
            message="If an account exists, a password reset link has been sent."
        )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(request: ResetPasswordRequest, http_request: Request):
    """Reset password with token from email"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase = get_supabase_auth()
        
        # Update user password
        response = supabase.auth.update_user({
            "password": request.new_password
        })
        
        if response.user:
            return AuthResponse(
                success=True,
                message="Password updated successfully"
            )
        else:
            return AuthResponse(
                success=False,
                message="Failed to reset password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, correlation_id=correlation_id)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout", response_model=AuthResponse)
async def logout(http_request: Request):
    """Logout user"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase = get_supabase_auth()
        supabase.auth.sign_out()
        
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, correlation_id=correlation_id)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_current_user(http_request: Request, authorization: str = None):
    """Get current user from token"""
    correlation_id = get_correlation_id(http_request)
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")
        
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_auth()
        
        response = supabase.auth.get_user(token)
        
        if response.user:
            return {
                "id": str(response.user.id),
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name", "")
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, correlation_id=correlation_id)
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    request: ChangePasswordRequest,
    http_request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Change password for logged-in user (requires current password)"""
    correlation_id = get_correlation_id(http_request)
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")
        
        token = authorization.replace("Bearer ", "")
        supabase_auth = get_supabase_auth()
        
        # Get current user
        user_response = supabase_auth.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_email = user_response.user.email
        
        # Verify current password by attempting login
        try:
            verify_response = supabase_auth.auth.sign_in_with_password({
                "email": user_email,
                "password": request.current_password
            })
            if not verify_response.user:
                raise HTTPException(status_code=401, detail="Current password is incorrect")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Update password using the verified session
        # Use the session from password verification
        update_supabase = get_supabase_auth()
        # Set the session from verification
        update_supabase.auth.set_session(
            verify_response.session.access_token,
            verify_response.session.refresh_token
        )
        update_response = update_supabase.auth.update_user({
            "password": request.new_password
        })
        
        if update_response.user:
            return AuthResponse(
                success=True,
                message="Password changed successfully"
            )
        else:
            return AuthResponse(
                success=False,
                message="Failed to change password"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id if 'user_id' in locals() else None, correlation_id=correlation_id)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/delete-account", response_model=AuthResponse)
async def delete_account(
    request: DeleteAccountRequest,
    http_request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """Delete user account (requires password verification)"""
    correlation_id = get_correlation_id(http_request)
    try:
        supabase_auth = get_supabase_auth()
        supabase_service = get_supabase()  # Service role client
        
        # Get user email by getting user from auth
        # We need to get email from user_id, but we can't query auth.users directly
        # So we verify password first, then get email from that
        # Actually, we already have user_id, so let's verify password first
        
        # For now, we need to get email from the user's session or verify via password
        # Since we can't easily get email from user_id without admin access,
        # we'll use a workaround: get user info from a test auth call
        # OR better: use admin API to get user by ID, then verify password
        
        # Use admin API to get user email
        try:
            admin_user = supabase_service.auth.admin.get_user_by_id(user_id)
            user_email = admin_user.user.email
        except Exception:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify password by attempting login
        try:
            verify_response = supabase_auth.auth.sign_in_with_password({
                "email": user_email,
                "password": request.password
            })
            if not verify_response.user:
                raise HTTPException(status_code=401, detail="Password is incorrect")
        except Exception:
            raise HTTPException(status_code=401, detail="Password is incorrect")
        
        # Delete user account using admin API (requires service role)
        supabase_service.auth.admin.delete_user(user_id)
        
        return AuthResponse(
            success=True,
            message="Account deleted successfully"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        await log_error(http_request, e, user_id=user_id, correlation_id=correlation_id)
        raise HTTPException(status_code=400, detail=str(e))
