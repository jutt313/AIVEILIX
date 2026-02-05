"""
Custom SMTP Email Service for AIveilix
Handles all transactional emails with professional HTML templates
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from pathlib import Path
from jinja2 import Template

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render an email template with context data"""
    template_path = TEMPLATE_DIR / template_name
    
    if not template_path.exists():
        logger.error(f"Template not found: {template_path}")
        raise FileNotFoundError(f"Email template not found: {template_name}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    return template.render(**context)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
) -> bool:
    """
    Send an email via SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML content of the email
        from_email: Sender email (defaults to config)
        from_name: Sender name (defaults to config)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from_email = from_email or settings.smtp_from_email
        from_name = from_name or settings.smtp_from_name
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        logger.info(f"[send_email] Connecting to {settings.smtp_host}:{settings.smtp_port}")
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        
        logger.info(f"[send_email] Successfully sent email to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"[send_email] Failed to send email to {to_email}: {e}")
        return False


# ==========================================
# Authentication Emails
# ==========================================

def send_verification_email(to_email: str, verification_link: str, user_name: str = "") -> bool:
    """Send email verification email"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "verification_link": verification_link,
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "app_name": "AIveilix"
    }
    
    html_content = render_template("auth/verification.html", context)
    return send_email(
        to_email=to_email,
        subject="Verify your AIveilix account",
        html_content=html_content
    )


def send_password_reset_email(to_email: str, reset_link: str, user_name: str = "") -> bool:
    """Send password reset email"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "reset_link": reset_link,
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "app_name": "AIveilix"
    }
    
    html_content = render_template("auth/password_reset.html", context)
    return send_email(
        to_email=to_email,
        subject="Reset your AIveilix password",
        html_content=html_content
    )


# ==========================================
# Subscription Emails
# ==========================================

def send_payment_success_email(to_email: str, amount: float, plan: str, user_name: str = "") -> bool:
    """Send payment success confirmation"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "amount": f"${amount:.2f}",
        "plan": plan.title(),
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "dashboard_url": f"{settings.frontend_url}/dashboard"
    }
    
    html_content = render_template("subscription/payment_success.html", context)
    return send_email(
        to_email=to_email,
        subject=f"Payment successful - {plan.title()} Plan",
        html_content=html_content
    )


def send_payment_failed_email(to_email: str, plan: str, user_name: str = "") -> bool:
    """Send payment failed notification"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "plan": plan.title(),
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "billing_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("subscription/payment_failed.html", context)
    return send_email(
        to_email=to_email,
        subject="Payment failed - Action required",
        html_content=html_content
    )


def send_renewal_reminder_email(to_email: str, plan: str, renewal_date: str, amount: float, user_name: str = "") -> bool:
    """Send renewal reminder 3 days before billing"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "plan": plan.title(),
        "renewal_date": renewal_date,
        "amount": f"${amount:.2f}",
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "billing_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("subscription/renewal_reminder.html", context)
    return send_email(
        to_email=to_email,
        subject=f"Your {plan.title()} plan renews in 3 days",
        html_content=html_content
    )


def send_subscription_renewed_email(to_email: str, plan: str, amount: float, next_billing_date: str, user_name: str = "") -> bool:
    """Send subscription renewed confirmation"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "plan": plan.title(),
        "amount": f"${amount:.2f}",
        "next_billing_date": next_billing_date,
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "dashboard_url": f"{settings.frontend_url}/dashboard"
    }
    
    html_content = render_template("subscription/subscription_renewed.html", context)
    return send_email(
        to_email=to_email,
        subject=f"Subscription renewed - {plan.title()} Plan",
        html_content=html_content
    )


def send_plan_changed_email(to_email: str, old_plan: str, new_plan: str, user_name: str = "") -> bool:
    """Send plan change confirmation"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "old_plan": old_plan.title(),
        "new_plan": new_plan.title(),
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "dashboard_url": f"{settings.frontend_url}/dashboard"
    }
    
    html_content = render_template("subscription/plan_changed.html", context)
    return send_email(
        to_email=to_email,
        subject=f"Plan changed to {new_plan.title()}",
        html_content=html_content
    )


def send_subscription_canceled_email(to_email: str, plan: str, end_date: str, user_name: str = "") -> bool:
    """Send subscription cancellation confirmation"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "plan": plan.title(),
        "end_date": end_date,
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "reactivate_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("subscription/subscription_canceled.html", context)
    return send_email(
        to_email=to_email,
        subject="Subscription canceled",
        html_content=html_content
    )


def send_trial_ending_email(to_email: str, days_remaining: int, user_name: str = "") -> bool:
    """Send trial ending reminder"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "days_remaining": days_remaining,
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "upgrade_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("subscription/trial_ending.html", context)
    return send_email(
        to_email=to_email,
        subject=f"Your trial ends in {days_remaining} days",
        html_content=html_content
    )


def send_trial_expired_email(to_email: str, user_name: str = "") -> bool:
    """Send trial expired notification"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "upgrade_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("subscription/trial_expired.html", context)
    return send_email(
        to_email=to_email,
        subject="Your trial has expired",
        html_content=html_content
    )


# ==========================================
# Usage Alert Emails
# ==========================================

def send_storage_warning_email(to_email: str, usage_percent: int, plan: str, user_name: str = "") -> bool:
    """Send storage limit warning"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "usage_percent": usage_percent,
        "plan": plan.title(),
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "upgrade_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("usage/storage_warning.html", context)
    return send_email(
        to_email=to_email,
        subject=f"Storage {usage_percent}% full",
        html_content=html_content
    )


def send_document_limit_warning_email(to_email: str, current_count: int, limit: int, plan: str, user_name: str = "") -> bool:
    """Send document limit warning"""
    context = {
        "user_name": user_name or to_email.split('@')[0],
        "current_count": current_count,
        "limit": limit,
        "plan": plan.title(),
        "logo_url": f"{settings.frontend_url}/logo.svg",
        "upgrade_url": f"{settings.frontend_url}/dashboard?tab=billing"
    }
    
    html_content = render_template("usage/document_limit_warning.html", context)
    return send_email(
        to_email=to_email,
        subject="Approaching document limit",
        html_content=html_content
    )
