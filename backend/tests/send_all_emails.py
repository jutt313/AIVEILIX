"""
Send all 12 email templates to mrproblem6677@gmail.com for preview
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import email_service

TEST_EMAIL = "mrproblem6677@gmail.com"
TEST_USER = "Test User"

def send_all_emails():
    """Send all 12 email types"""
    
    print("=" * 60)
    print("Sending all 12 email templates to:", TEST_EMAIL)
    print("=" * 60)
    print()
    
    results = []
    
    # 1. Email Verification
    print("📧 1/12 Sending Email Verification...")
    success = email_service.send_verification_email(
        to_email=TEST_EMAIL,
        verification_link="https://aiveilix.com/verify?token=test123",
        user_name=TEST_USER
    )
    results.append(("Email Verification", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 2. Password Reset
    print("📧 2/12 Sending Password Reset...")
    success = email_service.send_password_reset_email(
        to_email=TEST_EMAIL,
        reset_link="https://aiveilix.com/reset-password?token=test123",
        user_name=TEST_USER
    )
    results.append(("Password Reset", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 3. Payment Success
    print("📧 3/12 Sending Payment Success...")
    success = email_service.send_payment_success_email(
        to_email=TEST_EMAIL,
        amount=9.99,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Payment Success", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 4. Payment Failed
    print("📧 4/12 Sending Payment Failed...")
    success = email_service.send_payment_failed_email(
        to_email=TEST_EMAIL,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Payment Failed", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 5. Renewal Reminder
    print("📧 5/12 Sending Renewal Reminder...")
    success = email_service.send_renewal_reminder_email(
        to_email=TEST_EMAIL,
        plan="pro",
        renewal_date="February 5, 2026",
        amount=19.99,
        user_name=TEST_USER
    )
    results.append(("Renewal Reminder", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 6. Subscription Renewed
    print("📧 6/12 Sending Subscription Renewed...")
    success = email_service.send_subscription_renewed_email(
        to_email=TEST_EMAIL,
        plan="pro",
        amount=19.99,
        next_billing_date="March 2, 2026",
        user_name=TEST_USER
    )
    results.append(("Subscription Renewed", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 7. Plan Changed
    print("📧 7/12 Sending Plan Changed...")
    success = email_service.send_plan_changed_email(
        to_email=TEST_EMAIL,
        old_plan="starter",
        new_plan="pro",
        user_name=TEST_USER
    )
    results.append(("Plan Changed", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 8. Subscription Canceled
    print("📧 8/12 Sending Subscription Canceled...")
    success = email_service.send_subscription_canceled_email(
        to_email=TEST_EMAIL,
        plan="pro",
        end_date="March 2, 2026",
        user_name=TEST_USER
    )
    results.append(("Subscription Canceled", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 9. Trial Ending
    print("📧 9/12 Sending Trial Ending...")
    success = email_service.send_trial_ending_email(
        to_email=TEST_EMAIL,
        days_remaining=3,
        user_name=TEST_USER
    )
    results.append(("Trial Ending", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 10. Trial Expired
    print("📧 10/12 Sending Trial Expired...")
    success = email_service.send_trial_expired_email(
        to_email=TEST_EMAIL,
        user_name=TEST_USER
    )
    results.append(("Trial Expired", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 11. Storage Warning
    print("📧 11/12 Sending Storage Warning...")
    success = email_service.send_storage_warning_email(
        to_email=TEST_EMAIL,
        usage_percent=85,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Storage Warning", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # 12. Document Limit Warning
    print("📧 12/12 Sending Document Limit Warning...")
    success = email_service.send_document_limit_warning_email(
        to_email=TEST_EMAIL,
        current_count=45,
        limit=50,
        plan="starter",
        user_name=TEST_USER
    )
    results.append(("Document Limit Warning", success))
    print(f"   {'✅ Sent' if success else '❌ Failed'}\n")
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = sum(1 for _, success in results if success)
    print(f"✅ Sent: {successful}/12")
    print(f"❌ Failed: {12 - successful}/12")
    print()
    
    if successful == 12:
        print("🎉 All emails sent successfully!")
        print(f"📬 Check {TEST_EMAIL} inbox")
    else:
        print("⚠️  Some emails failed. Check the logs above.")
    
    print("=" * 60)


if __name__ == "__main__":
    send_all_emails()
