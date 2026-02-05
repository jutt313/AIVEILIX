"""
Simple email sender without jinja2 - reads HTML files directly
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# SMTP Config
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "chaffanjutt313@gmail.com"
SMTP_PASSWORD = "rake jifq nuxb tqis"
SMTP_FROM_EMAIL = "noreply@aiveilix.com"
SMTP_FROM_NAME = "AIveilix"

TEST_EMAIL = "mrproblem6677@gmail.com"
TEMPLATE_DIR = Path(__file__).parent.parent / "app" / "templates" / "emails"


def send_html_email(to_email, subject, html_content):
    """Send HTML email"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False


def replace_vars(html, vars_dict):
    """Simple variable replacement"""
    for key, value in vars_dict.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))
    return html


def send_all():
    print("=" * 60)
    print(f"Sending all 12 emails to: {TEST_EMAIL}")
    print("=" * 60)
    print()
    
    emails = [
        {
            "name": "Email Verification",
            "file": "auth/verification.html",
            "subject": "Verify your AIveilix account",
            "vars": {
                "user_name": "Test User",
                "verification_link": "https://aiveilix.com/verify?token=test123",
                "logo_url": "https://aiveilix.com/logo.svg"
            }
        },
        {
            "name": "Password Reset",
            "file": "auth/password_reset.html",
            "subject": "Reset your AIveilix password",
            "vars": {
                "user_name": "Test User",
                "reset_link": "https://aiveilix.com/reset-password?token=test123",
                "logo_url": "https://aiveilix.com/logo.svg"
            }
        },
        {
            "name": "Payment Success",
            "file": "subscription/payment_success.html",
            "subject": "Payment successful - Starter Plan",
            "vars": {
                "user_name": "Test User",
                "plan": "Starter",
                "amount": "$9.99",
                "logo_url": "https://aiveilix.com/logo.svg",
                "dashboard_url": "https://aiveilix.com/dashboard"
            }
        },
        {
            "name": "Payment Failed",
            "file": "subscription/payment_failed.html",
            "subject": "Payment failed - Action required",
            "vars": {
                "user_name": "Test User",
                "plan": "Starter",
                "logo_url": "https://aiveilix.com/logo.svg",
                "billing_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        },
        {
            "name": "Renewal Reminder",
            "file": "subscription/renewal_reminder.html",
            "subject": "Your Pro plan renews in 3 days",
            "vars": {
                "user_name": "Test User",
                "plan": "Pro",
                "renewal_date": "February 5, 2026",
                "amount": "$19.99",
                "logo_url": "https://aiveilix.com/logo.svg",
                "billing_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        },
        {
            "name": "Subscription Renewed",
            "file": "subscription/subscription_renewed.html",
            "subject": "Subscription renewed - Pro Plan",
            "vars": {
                "user_name": "Test User",
                "plan": "Pro",
                "amount": "$19.99",
                "next_billing_date": "March 2, 2026",
                "logo_url": "https://aiveilix.com/logo.svg",
                "dashboard_url": "https://aiveilix.com/dashboard"
            }
        },
        {
            "name": "Plan Changed",
            "file": "subscription/plan_changed.html",
            "subject": "Plan changed to Pro",
            "vars": {
                "user_name": "Test User",
                "old_plan": "Starter",
                "new_plan": "Pro",
                "logo_url": "https://aiveilix.com/logo.svg",
                "dashboard_url": "https://aiveilix.com/dashboard"
            }
        },
        {
            "name": "Subscription Canceled",
            "file": "subscription/subscription_canceled.html",
            "subject": "Subscription canceled",
            "vars": {
                "user_name": "Test User",
                "plan": "Pro",
                "end_date": "March 2, 2026",
                "logo_url": "https://aiveilix.com/logo.svg",
                "reactivate_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        },
        {
            "name": "Trial Ending",
            "file": "subscription/trial_ending.html",
            "subject": "Your trial ends in 3 days",
            "vars": {
                "user_name": "Test User",
                "days_remaining": "3",
                "logo_url": "https://aiveilix.com/logo.svg",
                "upgrade_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        },
        {
            "name": "Trial Expired",
            "file": "subscription/trial_expired.html",
            "subject": "Your trial has expired",
            "vars": {
                "user_name": "Test User",
                "logo_url": "https://aiveilix.com/logo.svg",
                "upgrade_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        },
        {
            "name": "Storage Warning",
            "file": "usage/storage_warning.html",
            "subject": "Storage 85% full",
            "vars": {
                "user_name": "Test User",
                "usage_percent": "85",
                "plan": "Starter",
                "logo_url": "https://aiveilix.com/logo.svg",
                "upgrade_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        },
        {
            "name": "Document Limit Warning",
            "file": "usage/document_limit_warning.html",
            "subject": "Approaching document limit",
            "vars": {
                "user_name": "Test User",
                "current_count": "45",
                "limit": "50",
                "plan": "Starter",
                "logo_url": "https://aiveilix.com/logo.svg",
                "upgrade_url": "https://aiveilix.com/dashboard?tab=billing"
            }
        }
    ]
    
    sent = 0
    for i, email in enumerate(emails, 1):
        print(f"📧 {i}/12 Sending {email['name']}...")
        
        template_path = TEMPLATE_DIR / email['file']
        if not template_path.exists():
            print(f"   ❌ Template not found: {template_path}")
            continue
        
        html = template_path.read_text()
        html = replace_vars(html, email['vars'])
        
        if send_html_email(TEST_EMAIL, email['subject'], html):
            print(f"   ✅ Sent")
            sent += 1
        else:
            print(f"   ❌ Failed")
        print()
    
    print("=" * 60)
    print(f"✅ Sent: {sent}/12")
    print(f"❌ Failed: {12 - sent}/12")
    if sent == 12:
        print(f"\n🎉 Check {TEST_EMAIL} inbox!")
    print("=" * 60)


if __name__ == "__main__":
    send_all()
