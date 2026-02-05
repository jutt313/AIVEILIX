"""
Subscription email service for sending payment and billing notifications
"""
import logging
from typing import Optional
from datetime import datetime

from app.config import get_settings
from app.services.supabase import get_supabase
from app.services.notifications import create_notification

settings = get_settings()
logger = logging.getLogger(__name__)


async def send_payment_success_email(user_id: str, plan: str, amount: float) -> None:
    """Send email when payment is successful"""
    try:
        # Create in-app notification
        await create_notification(
            user_id=user_id,
            notification_type="payment_success",
            title="Payment Successful",
            message=f"Your payment of ${amount:.2f} for the {plan.capitalize()} plan was successful. Thank you for subscribing!",
            data={
                "plan": plan,
                "amount": amount,
                "type": "payment_success"
            }
        )

        # TODO: Send actual email via email provider (SendGrid, Resend, etc.)
        # For now, we just log and create notification
        logger.info(f"Payment success notification sent to user {user_id} for {plan} plan")

    except Exception as e:
        logger.error(f"Failed to send payment success email: {e}")


async def send_renewal_reminder_email(user_id: str, plan: str, renewal_date: datetime, amount: float) -> None:
    """Send email 3 days before renewal"""
    try:
        date_str = renewal_date.strftime("%B %d, %Y")

        await create_notification(
            user_id=user_id,
            notification_type="renewal_reminder",
            title="Subscription Renewal Reminder",
            message=f"Your {plan.capitalize()} subscription will renew on {date_str} for ${amount:.2f}.",
            data={
                "plan": plan,
                "amount": amount,
                "renewal_date": date_str,
                "type": "renewal_reminder"
            }
        )

        logger.info(f"Renewal reminder sent to user {user_id}")

    except Exception as e:
        logger.error(f"Failed to send renewal reminder: {e}")


async def send_payment_failed_email(user_id: str, plan: str) -> None:
    """Send email when payment fails"""
    try:
        await create_notification(
            user_id=user_id,
            notification_type="payment_failed",
            title="Payment Failed",
            message=f"We were unable to process your payment for the {plan.capitalize()} plan. Please update your payment method to continue using AIveilix.",
            data={
                "plan": plan,
                "type": "payment_failed"
            }
        )

        logger.info(f"Payment failed notification sent to user {user_id}")

    except Exception as e:
        logger.error(f"Failed to send payment failed email: {e}")


async def send_subscription_renewed_email(user_id: str, plan: str, next_billing_date: datetime) -> None:
    """Send email when subscription is renewed"""
    try:
        date_str = next_billing_date.strftime("%B %d, %Y")

        await create_notification(
            user_id=user_id,
            notification_type="subscription_renewed",
            title="Subscription Renewed",
            message=f"Your {plan.capitalize()} subscription has been renewed. Next billing date: {date_str}.",
            data={
                "plan": plan,
                "next_billing_date": date_str,
                "type": "subscription_renewed"
            }
        )

        logger.info(f"Subscription renewed notification sent to user {user_id}")

    except Exception as e:
        logger.error(f"Failed to send subscription renewed email: {e}")


async def send_plan_changed_email(user_id: str, old_plan: str, new_plan: str) -> None:
    """Send email when user upgrades or downgrades"""
    try:
        is_upgrade = _is_upgrade(old_plan, new_plan)
        action = "upgraded" if is_upgrade else "changed"

        await create_notification(
            user_id=user_id,
            notification_type="plan_changed",
            title=f"Plan {action.capitalize()}",
            message=f"Your subscription has been {action} from {old_plan.capitalize()} to {new_plan.capitalize()}.",
            data={
                "old_plan": old_plan,
                "new_plan": new_plan,
                "is_upgrade": is_upgrade,
                "type": "plan_changed"
            }
        )

        logger.info(f"Plan change notification sent to user {user_id}: {old_plan} -> {new_plan}")

    except Exception as e:
        logger.error(f"Failed to send plan change email: {e}")


async def send_subscription_canceled_email(user_id: str, plan: str, end_date: datetime) -> None:
    """Send email when subscription is canceled"""
    try:
        date_str = end_date.strftime("%B %d, %Y")

        await create_notification(
            user_id=user_id,
            notification_type="subscription_canceled",
            title="Subscription Canceled",
            message=f"Your {plan.capitalize()} subscription has been canceled. You will have access until {date_str}.",
            data={
                "plan": plan,
                "end_date": date_str,
                "type": "subscription_canceled"
            }
        )

        logger.info(f"Subscription canceled notification sent to user {user_id}")

    except Exception as e:
        logger.error(f"Failed to send subscription canceled email: {e}")


async def send_trial_ending_email(user_id: str, days_remaining: int) -> None:
    """Send email when trial is about to end"""
    try:
        await create_notification(
            user_id=user_id,
            notification_type="trial_ending",
            title="Free Trial Ending Soon",
            message=f"Your free trial ends in {days_remaining} day{'s' if days_remaining != 1 else ''}. Upgrade now to keep your documents and continue using AIveilix.",
            data={
                "days_remaining": days_remaining,
                "type": "trial_ending"
            }
        )

        logger.info(f"Trial ending notification sent to user {user_id}, {days_remaining} days remaining")

    except Exception as e:
        logger.error(f"Failed to send trial ending email: {e}")


async def send_trial_expired_email(user_id: str) -> None:
    """Send email when trial has expired"""
    try:
        await create_notification(
            user_id=user_id,
            notification_type="trial_expired",
            title="Free Trial Expired",
            message="Your free trial has expired. Upgrade to a paid plan to continue using AIveilix and access your documents.",
            data={
                "type": "trial_expired"
            }
        )

        logger.info(f"Trial expired notification sent to user {user_id}")

    except Exception as e:
        logger.error(f"Failed to send trial expired email: {e}")


def _is_upgrade(old_plan: str, new_plan: str) -> bool:
    """Determine if plan change is an upgrade"""
    plan_order = {
        "free_trial": 0,
        "starter": 1,
        "pro": 2,
        "premium": 3
    }

    return plan_order.get(new_plan, 0) > plan_order.get(old_plan, 0)


async def create_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    data: dict = None
) -> None:
    """Create an in-app notification"""
    supabase = get_supabase()

    notification = {
        "user_id": user_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "data": data or {},
        "is_read": False
    }

    supabase.table("notifications").insert(notification).execute()
