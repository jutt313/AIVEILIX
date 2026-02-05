"""
Test script for AIveilix custom email system
Run this to verify SMTP connection and template rendering
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import email_service
from app.config import get_settings

settings = get_settings()

def test_smtp_connection():
    """Test SMTP connection"""
    print("🔌 Testing SMTP connection...")
    print(f"   Host: {settings.smtp_host}:{settings.smtp_port}")
    print(f"   User: {settings.smtp_user}")
    
    try:
        import smtplib
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
        print("✅ SMTP connection successful!\n")
        return True
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}\n")
        return False


def test_email_templates():
    """Test that all email templates exist"""
    print("📧 Checking email templates...")
    
    templates = [
        "auth/verification.html",
        "auth/password_reset.html",
        "subscription/payment_success.html",
        "subscription/payment_failed.html",
        "subscription/renewal_reminder.html",
        "subscription/subscription_renewed.html",
        "subscription/plan_changed.html",
        "subscription/subscription_canceled.html",
        "subscription/trial_ending.html",
        "subscription/trial_expired.html",
        "usage/storage_warning.html",
        "usage/document_limit_warning.html",
    ]
    
    from pathlib import Path
    template_dir = Path(__file__).parent.parent / "app" / "templates" / "emails"
    
    all_exist = True
    for template in templates:
        template_path = template_dir / template
        if template_path.exists():
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - NOT FOUND")
            all_exist = False
    
    print()
    return all_exist


def send_test_email():
    """Send a test email"""
    test_email = input("Enter your email to receive a test: ").strip()
    
    if not test_email:
        print("❌ No email provided\n")
        return False
    
    print(f"\n📨 Sending test verification email to {test_email}...")
    
    try:
        success = email_service.send_verification_email(
            to_email=test_email,
            verification_link="https://aiveilix.com/verify?token=test123",
            user_name="Test User"
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"   Check {test_email} for the email\n")
            return True
        else:
            print("❌ Failed to send test email\n")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}\n")
        return False


def main():
    print("=" * 60)
    print("AIveilix Custom Email System - Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: SMTP Connection
    smtp_ok = test_smtp_connection()
    
    # Test 2: Templates
    templates_ok = test_email_templates()
    
    # Test 3: Send test email
    if smtp_ok and templates_ok:
        print("All checks passed! Ready to send a test email.\n")
        send_test_email()
    else:
        print("⚠️  Some checks failed. Please fix the issues above before sending emails.\n")
    
    print("=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
