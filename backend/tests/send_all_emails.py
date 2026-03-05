"""
Send all 8 email templates to test email for preview
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import email_service

TEST_EMAIL = "mrproblem6677@gmail.com"
TEST_USER = "Test User"

def send_all_emails():
    print("=" * 60)
    print("Sending all 8 email templates to:", TEST_EMAIL)
    print("=" * 60)

    results = []

    print("📧 1/8 Email Verification...")
    success = email_service.send_verification_email(
        to_email=TEST_EMAIL,
        verification_link="https://aiveilix.com/verify?token=test123",
        user_name=TEST_USER
    )
    results.append(("Email Verification", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 2/8 Password Reset...")
    success = email_service.send_password_reset_email(
        to_email=TEST_EMAIL,
        reset_link="https://aiveilix.com/reset-password?token=test123",
        user_name=TEST_USER
    )
    results.append(("Password Reset", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 3/8 Payment Success...")
    success = email_service.send_payment_success_email(
        to_email=TEST_EMAIL,
        amount=9.99,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Payment Success", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 4/8 Payment Failed...")
    success = email_service.send_payment_failed_email(
        to_email=TEST_EMAIL,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Payment Failed", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 5/8 Subscription Canceled...")
    success = email_service.send_subscription_canceled_email(
        to_email=TEST_EMAIL,
        plan="pro",
        end_date="March 2, 2026",
        user_name=TEST_USER
    )
    results.append(("Subscription Canceled", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 6/8 Plan Changed...")
    success = email_service.send_plan_changed_email(
        to_email=TEST_EMAIL,
        old_plan="starter",
        new_plan="pro",
        user_name=TEST_USER
    )
    results.append(("Plan Changed", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 7/8 Subscription Renewed...")
    success = email_service.send_subscription_renewed_email(
        to_email=TEST_EMAIL,
        plan="pro",
        amount=19.99,
        next_billing_date="March 2, 2026",
        user_name=TEST_USER
    )
    results.append(("Subscription Renewed", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("📧 8/8 Storage Warning...")
    success = email_service.send_storage_warning_email(
        to_email=TEST_EMAIL,
        usage_percent=85,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Storage Warning", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")

    print("=" * 60)
    successful = sum(1 for _, s in results if s)
    print(f"✅ Sent: {successful}/8")
    print(f"❌ Failed: {8 - successful}/8")
    if successful == 8:
        print(f"🎉 All emails sent! Check {TEST_EMAIL}")
    print("=" * 60)

if __name__ == "__main__":
    send_all_emails()
