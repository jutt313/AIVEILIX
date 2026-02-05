"""
Stripe service for subscription management
"""
import stripe
import logging
import traceback
from typing import Optional, Dict, Any
from app.config import get_settings
from app.services.supabase import get_supabase

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key
    logger.info(f"Stripe initialized with key: {settings.stripe_secret_key[:12]}...")
else:
    logger.warning("STRIPE_SECRET_KEY not configured!")

# Price ID to plan name mapping
PRICE_TO_PLAN = {
    settings.stripe_price_starter: "starter",
    settings.stripe_price_pro: "pro",
    settings.stripe_price_premium: "premium",
}

PLAN_TO_PRICE = {
    "starter": settings.stripe_price_starter,
    "pro": settings.stripe_price_pro,
    "premium": settings.stripe_price_premium,
}


async def get_or_create_customer(user_id: str, email: str) -> str:
    """Get existing Stripe customer or create new one"""
    logger.info(f"[get_or_create_customer] user_id={user_id}, email={email}")
    supabase = get_supabase()

    try:
        # Check if user already has a subscription record
        result = supabase.table("subscriptions").select("stripe_customer_id").eq("user_id", user_id).execute()
        logger.info(f"[get_or_create_customer] DB result: {result.data}")

        # If subscription exists and has customer ID, return it
        if result.data and len(result.data) > 0 and result.data[0].get("stripe_customer_id"):
            logger.info(f"[get_or_create_customer] Found existing customer: {result.data[0]['stripe_customer_id']}")
            return result.data[0]["stripe_customer_id"]

        # Create new Stripe customer
        logger.info(f"[get_or_create_customer] Creating new Stripe customer...")
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id}
        )
        logger.info(f"[get_or_create_customer] Created customer: {customer.id}")

        # Check if subscription record exists
        if result.data and len(result.data) > 0:
            # Update existing subscription with customer ID
            update_result = supabase.table("subscriptions").update({
                "stripe_customer_id": customer.id
            }).eq("user_id", user_id).execute()
            logger.info(f"[get_or_create_customer] Updated subscription: {update_result.data}")
        else:
            # Create new subscription record (free trial)
            from datetime import datetime, timezone, timedelta
            trial_end = datetime.now(timezone.utc) + timedelta(days=14)
            insert_result = supabase.table("subscriptions").insert({
                "user_id": user_id,
                "plan": "free_trial",
                "status": "trialing",
                "stripe_customer_id": customer.id,
                "trial_end": trial_end.isoformat()
            }).execute()
            logger.info(f"[get_or_create_customer] Created subscription: {insert_result.data}")

        return customer.id

    except Exception as e:
        logger.error(f"[get_or_create_customer] Error: {e}\n{traceback.format_exc()}")
        raise


async def create_checkout_session(
    user_id: str,
    email: str,
    plan: str,
    success_url: str,
    cancel_url: str
) -> Dict[str, Any]:
    """Create Stripe Checkout session for subscription"""
    logger.info(f"[create_checkout_session] user_id={user_id}, plan={plan}")

    if plan not in PLAN_TO_PRICE:
        logger.error(f"[create_checkout_session] Invalid plan: {plan}. Valid: {list(PLAN_TO_PRICE.keys())}")
        raise ValueError(f"Invalid plan: {plan}. Valid plans: {list(PLAN_TO_PRICE.keys())}")

    price_id = PLAN_TO_PRICE[plan]
    if not price_id:
        logger.error(f"[create_checkout_session] Price ID not configured for plan: {plan}")
        raise ValueError(f"Price ID not configured for plan: {plan}. Check STRIPE_PRICE_{plan.upper()} in .env")

    logger.info(f"[create_checkout_session] Using price_id={price_id}")

    try:
        # Get or create customer
        customer_id = await get_or_create_customer(user_id, email)
        logger.info(f"[create_checkout_session] customer_id={customer_id}")

        # Create checkout session
        logger.info(f"[create_checkout_session] Creating Stripe session...")
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user_id,
                "plan": plan,
            },
            subscription_data={
                "metadata": {
                    "user_id": user_id,
                    "plan": plan,
                }
            },
            allow_promotion_codes=True,
        )

        logger.info(f"[create_checkout_session] Success! session_id={session.id}, url={session.url[:50]}...")

        return {
            "session_id": session.id,
            "url": session.url,
        }

    except stripe.error.StripeError as e:
        logger.error(f"[create_checkout_session] Stripe error: {e}\n{traceback.format_exc()}")
        raise
    except Exception as e:
        logger.error(f"[create_checkout_session] Unexpected error: {e}\n{traceback.format_exc()}")
        raise


async def create_customer_portal(user_id: str) -> str:
    """Create Stripe Customer Portal session for billing management"""
    supabase = get_supabase()

    # Get customer ID
    result = supabase.table("subscriptions").select("stripe_customer_id").eq("user_id", user_id).single().execute()

    if not result.data or not result.data.get("stripe_customer_id"):
        raise ValueError("No Stripe customer found for user")

    customer_id = result.data["stripe_customer_id"]

    # Create portal session
    portal_session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.frontend_url}/dashboard",
    )

    return portal_session.url


async def get_user_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's current subscription details"""
    supabase = get_supabase()

    result = supabase.table("subscriptions").select("*").eq("user_id", user_id).single().execute()

    if not result.data:
        return None

    return result.data


async def update_subscription_from_stripe(subscription_id: str) -> None:
    """Sync subscription data from Stripe"""
    supabase = get_supabase()

    # Get subscription from Stripe
    stripe_sub = stripe.Subscription.retrieve(subscription_id)

    # Get plan from price ID
    price_id = stripe_sub["items"]["data"][0]["price"]["id"]
    plan = PRICE_TO_PLAN.get(price_id, "starter")

    # Update in database
    supabase.table("subscriptions").update({
        "plan": plan,
        "status": stripe_sub["status"],
        "current_period_start": stripe_sub["current_period_start"],
        "current_period_end": stripe_sub["current_period_end"],
        "cancel_at_period_end": stripe_sub["cancel_at_period_end"],
    }).eq("stripe_subscription_id", subscription_id).execute()

    logger.info(f"Updated subscription {subscription_id} to plan {plan}, status {stripe_sub['status']}")


from app.services import email_service


async def handle_webhook_event(payload: bytes, sig_header: str) -> Dict[str, Any]:
    """Handle Stripe webhook events"""

    webhook_secret = settings.stripe_webhook_secret

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # For development without webhook secret
            import json
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {e}")
        raise

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Processing webhook event: {event_type}")

    supabase = get_supabase()

    if event_type == "checkout.session.completed":
        # New subscription created
        user_id = data["metadata"].get("user_id")
        plan = data["metadata"].get("plan")
        subscription_id = data.get("subscription")
        customer_id = data.get("customer")
        
        # Get customer email
        customer_email = data.get("customer_details", {}).get("email")
        if not customer_email and customer_id:
             try:
                 cust = stripe.Customer.retrieve(customer_id)
                 customer_email = cust.email
             except:
                 pass

        if user_id and subscription_id:
            # Get subscription details from Stripe
            stripe_sub = stripe.Subscription.retrieve(subscription_id)

            supabase.table("subscriptions").update({
                "plan": plan,
                "status": "active",
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": subscription_id,
                "current_period_start": stripe_sub["current_period_start"],
                "current_period_end": stripe_sub["current_period_end"],
                "trial_end": None,  # Clear trial
            }).eq("user_id", user_id).execute()

            logger.info(f"Activated subscription for user {user_id}, plan {plan}")

            # Send payment success email
            if customer_email:
                amount_total = data.get("amount_total", 0) / 100.0
                email_service.send_payment_success_email(
                    to_email=customer_email,
                    amount=amount_total,
                    plan=plan,
                )
            
            return {"status": "subscription_activated", "user_id": user_id, "plan": plan}

    elif event_type == "customer.subscription.updated":
        subscription_id = data["id"]
        # Check if plan changed
        old_plan_id = event["data"].get("previous_attributes", {}).get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
        
        await update_subscription_from_stripe(subscription_id)
        
        if old_plan_id:
            # It was a plan change
            new_plan_id = data["items"]["data"][0]["price"]["id"]
            new_plan = PRICE_TO_PLAN.get(new_plan_id, "unknown")
            old_plan = PRICE_TO_PLAN.get(old_plan_id, "unknown")
            
            # Get customer email
            customer_id = data.get("customer")
            try:
                 cust = stripe.Customer.retrieve(customer_id)
                 email_service.send_plan_changed_email(
                     to_email=cust.email,
                     old_plan=old_plan,
                     new_plan=new_plan
                 )
            except Exception as e:
                logger.error(f"Failed to send plan change email: {e}")

        return {"status": "subscription_updated"}

    elif event_type == "customer.subscription.deleted":
        subscription_id = data["id"]
        customer_id = data.get("customer")

        # Downgrade to free trial (expired)
        supabase.table("subscriptions").update({
            "plan": "free_trial",
            "status": "canceled",
            "stripe_subscription_id": None,
        }).eq("stripe_subscription_id", subscription_id).execute()

        logger.info(f"Subscription {subscription_id} canceled")

        # Send cancellation email
        try:
             cust = stripe.Customer.retrieve(customer_id)
             # Get plan name
             plan_id = data["items"]["data"][0]["price"]["id"]
             plan = PRICE_TO_PLAN.get(plan_id, "subscription")
             
             import datetime
             end_date = datetime.datetime.fromtimestamp(data["current_period_end"]).strftime('%B %d, %Y')
             
             email_service.send_subscription_canceled_email(
                 to_email=cust.email,
                 plan=plan,
                 end_date=end_date
             )
        except Exception as e:
            logger.error(f"Failed to send cancellation email: {e}")

        return {"status": "subscription_canceled"}

    elif event_type == "invoice.payment_succeeded":
        subscription_id = data.get("subscription")
        if subscription_id and data.get("billing_reason") == "subscription_cycle":
            await update_subscription_from_stripe(subscription_id)
            
            # Send renewal confirmation email
            try:
                customer_email = data.get("customer_email")
                amount = data.get("amount_paid", 0) / 100.0
                
                # Get plan
                line_items = data.get("lines", {}).get("data", [])
                if line_items:
                    plan_id = line_items[0]["price"]["id"]
                    plan = PRICE_TO_PLAN.get(plan_id, "subscription")
                    
                    import datetime
                    next_date = datetime.datetime.fromtimestamp(line_items[0]["period"]["end"]).strftime('%B %d, %Y')
                    
                    if customer_email:
                        email_service.send_subscription_renewed_email(
                            to_email=customer_email,
                            plan=plan,
                            amount=amount,
                            next_billing_date=next_date
                        )
            except Exception as e:
                logger.error(f"Failed to send renewal email: {e}")
                
        return {"status": "payment_succeeded"}

    elif event_type == "invoice.payment_failed":
        subscription_id = data.get("subscription")
        customer_id = data.get("customer")

        if subscription_id:
            supabase.table("subscriptions").update({
                "status": "past_due"
            }).eq("stripe_subscription_id", subscription_id).execute()

            logger.warning(f"Payment failed for subscription {subscription_id}")

            # Send payment failed email
            try:
                customer_email = data.get("customer_email")
                if customer_email:
                     # Get plan
                    line_items = data.get("lines", {}).get("data", [])
                    plan = "Subscription"
                    if line_items:
                        plan_id = line_items[0]["price"]["id"]
                        plan = PRICE_TO_PLAN.get(plan_id, "Subscription")
                    
                    email_service.send_payment_failed_email(
                        to_email=customer_email,
                        plan=plan
                    )
            except Exception as e:
                logger.error(f"Failed to send payment failed email: {e}")

        return {"status": "payment_failed"}

    return {"status": "unhandled", "event_type": event_type}


async def cancel_subscription(user_id: str) -> bool:
    """Cancel user's subscription at period end"""
    supabase = get_supabase()

    result = supabase.table("subscriptions").select("stripe_subscription_id").eq("user_id", user_id).single().execute()

    if not result.data or not result.data.get("stripe_subscription_id"):
        return False

    subscription_id = result.data["stripe_subscription_id"]

    # Cancel at period end (not immediately)
    stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True
    )

    supabase.table("subscriptions").update({
        "cancel_at_period_end": True
    }).eq("user_id", user_id).execute()

    logger.info(f"Scheduled cancellation for subscription {subscription_id}")
    return True


async def reactivate_subscription(user_id: str) -> bool:
    """Reactivate a subscription that was set to cancel"""
    supabase = get_supabase()

    result = supabase.table("subscriptions").select("stripe_subscription_id").eq("user_id", user_id).single().execute()

    if not result.data or not result.data.get("stripe_subscription_id"):
        return False

    subscription_id = result.data["stripe_subscription_id"]

    stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=False
    )

    supabase.table("subscriptions").update({
        "cancel_at_period_end": False
    }).eq("user_id", user_id).execute()

    logger.info(f"Reactivated subscription {subscription_id}")
    return True
