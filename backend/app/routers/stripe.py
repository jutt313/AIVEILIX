"""
Stripe payment routes for subscription management
"""
from fastapi import APIRouter, HTTPException, Request, Header, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import traceback
import stripe

from app.config import get_settings
from app.routers.buckets import get_current_user_id
from app.services.supabase import get_supabase
from app.services import stripe_service
from app.services import plan_limits

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def get_stripe_error_detail(e: Exception) -> dict:
    """Extract detailed error info from Stripe exceptions"""
    if isinstance(e, stripe.error.CardError):
        return {
            "error": "card_error",
            "message": e.user_message or str(e),
            "code": e.code,
            "param": e.param,
            "decline_code": getattr(e, 'decline_code', None)
        }
    elif isinstance(e, stripe.error.RateLimitError):
        return {"error": "rate_limit", "message": "Too many requests to payment provider. Please try again."}
    elif isinstance(e, stripe.error.InvalidRequestError):
        return {"error": "invalid_request", "message": str(e), "param": e.param}
    elif isinstance(e, stripe.error.AuthenticationError):
        return {"error": "auth_error", "message": "Payment service configuration error. Contact support."}
    elif isinstance(e, stripe.error.APIConnectionError):
        return {"error": "connection_error", "message": "Could not connect to payment service. Please try again."}
    elif isinstance(e, stripe.error.StripeError):
        return {"error": "stripe_error", "message": str(e)}
    else:
        return {"error": "unknown", "message": str(e)}


class CheckoutRequest(BaseModel):
    plan: str  # starter, pro, premium
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    session_id: str
    url: str


class SubscriptionResponse(BaseModel):
    plan: str
    status: str
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False
    stripe_customer_id: Optional[str] = None


class PortalResponse(BaseModel):
    url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create Stripe Checkout session for subscription"""
    try:
        logger.info(f"[Checkout] Starting for user={user_id}, plan={request.plan}")

        # Get user email
        supabase = get_supabase()
        user_result = supabase.auth.admin.get_user_by_id(user_id)
        if not user_result or not user_result.user:
            logger.error(f"[Checkout] User not found: {user_id}")
            raise HTTPException(status_code=404, detail={"error": "user_not_found", "message": "User not found"})

        email = user_result.user.email
        logger.info(f"[Checkout] User email: {email}")

        # Default URLs
        success_url = request.success_url or f"{settings.frontend_url}/dashboard?payment=success"
        cancel_url = request.cancel_url or f"{settings.frontend_url}/pricing?payment=canceled"

        result = await stripe_service.create_checkout_session(
            user_id=user_id,
            email=email,
            plan=request.plan,
            success_url=success_url,
            cancel_url=cancel_url
        )

        logger.info(f"[Checkout] Success - session_id={result.get('session_id')}")
        return CheckoutResponse(**result)

    except ValueError as e:
        logger.error(f"[Checkout] ValueError: {e}")
        raise HTTPException(status_code=400, detail={"error": "invalid_request", "message": str(e)})
    except stripe.error.StripeError as e:
        logger.error(f"[Checkout] StripeError: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=get_stripe_error_detail(e))
    except Exception as e:
        logger.error(f"[Checkout] Unexpected error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "checkout_failed", "message": str(e), "trace": traceback.format_exc()})


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()

        result = await stripe_service.handle_webhook_event(
            payload=payload,
            sig_header=stripe_signature or ""
        )

        return result

    except ValueError as e:
        logger.error(f"Webhook value error: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/portal", response_model=PortalResponse)
async def get_billing_portal(
    user_id: str = Depends(get_current_user_id)
):
    """Get Stripe Customer Portal URL for billing management"""
    try:
        logger.info(f"[Portal] Creating portal session for user={user_id}")
        url = await stripe_service.create_customer_portal(user_id)
        logger.info(f"[Portal] Success")
        return PortalResponse(url=url)

    except ValueError as e:
        logger.error(f"[Portal] ValueError: {e}")
        raise HTTPException(status_code=400, detail={"error": "no_customer", "message": str(e)})
    except stripe.error.StripeError as e:
        logger.error(f"[Portal] StripeError: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=get_stripe_error_detail(e))
    except Exception as e:
        logger.error(f"[Portal] Unexpected error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "portal_failed", "message": str(e)})


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user's subscription details"""
    try:
        logger.info(f"[Subscription] Getting subscription for user={user_id}")
        subscription = await stripe_service.get_user_subscription(user_id)

        if not subscription:
            logger.info(f"[Subscription] No subscription found, returning free_trial")
            return SubscriptionResponse(
                plan="free_trial",
                status="trialing",
                cancel_at_period_end=False
            )

        logger.info(f"[Subscription] Found: plan={subscription.get('plan')}, status={subscription.get('status')}")
        return SubscriptionResponse(
            plan=subscription.get("plan", "free_trial"),
            status=subscription.get("status", "trialing"),
            current_period_end=subscription.get("current_period_end"),
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
            stripe_customer_id=subscription.get("stripe_customer_id")
        )

    except Exception as e:
        logger.error(f"[Subscription] Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "subscription_fetch_failed", "message": str(e)})


@router.post("/cancel")
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Cancel subscription at end of billing period"""
    try:
        logger.info(f"[Cancel] Canceling subscription for user={user_id}")
        success = await stripe_service.cancel_subscription(user_id)

        if not success:
            logger.warning(f"[Cancel] No active subscription found for user={user_id}")
            raise HTTPException(status_code=400, detail={"error": "no_subscription", "message": "No active subscription to cancel"})

        logger.info(f"[Cancel] Success")
        return {"status": "canceled", "message": "Subscription will cancel at end of billing period"}

    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"[Cancel] StripeError: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=get_stripe_error_detail(e))
    except Exception as e:
        logger.error(f"[Cancel] Unexpected error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "cancel_failed", "message": str(e)})


@router.post("/reactivate")
async def reactivate_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Reactivate a subscription that was set to cancel"""
    try:
        logger.info(f"[Reactivate] Reactivating subscription for user={user_id}")
        success = await stripe_service.reactivate_subscription(user_id)

        if not success:
            logger.warning(f"[Reactivate] No subscription found for user={user_id}")
            raise HTTPException(status_code=400, detail={"error": "no_subscription", "message": "No subscription to reactivate"})

        logger.info(f"[Reactivate] Success")
        return {"status": "reactivated", "message": "Subscription reactivated"}

    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"[Reactivate] StripeError: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=get_stripe_error_detail(e))
    except Exception as e:
        logger.error(f"[Reactivate] Unexpected error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "reactivate_failed", "message": str(e)})


@router.get("/usage")
async def get_usage(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user's usage summary"""
    try:
        logger.info(f"[Usage] Getting usage for user={user_id}")
        summary = await plan_limits.get_usage_summary(user_id)
        logger.info(f"[Usage] Plan={summary.get('plan')}")
        return summary
    except Exception as e:
        logger.error(f"[Usage] Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": "usage_fetch_failed", "message": str(e)})


@router.get("/prices")
async def get_prices():
    """Get available subscription prices (public endpoint)"""
    return {
        "plans": [
            {
                "id": "starter",
                "name": "Starter",
                "price": 12.78,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "3GB storage",
                    "200 documents",
                    "25MB max file size",
                    "100 API calls/day",
                    "MCP server access",
                    "Community support"
                ]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 24.13,
                "currency": "usd",
                "interval": "month",
                "popular": True,
                "features": [
                    "10GB storage",
                    "Unlimited documents",
                    "50MB max file size",
                    "1000 API calls/day",
                    "MCP server access",
                    "Full API access",
                    "Priority support"
                ]
            },
            {
                "id": "premium",
                "name": "Premium",
                "price": 49.99,
                "currency": "usd",
                "interval": "month",
                "features": [
                    "50GB storage",
                    "Unlimited documents",
                    "100MB max file size",
                    "5000 API calls/day",
                    "MCP server access",
                    "Full API access",
                    "Dedicated support",
                    "Advanced analytics"
                ]
            }
        ],
        "trial_days": 14
    }
