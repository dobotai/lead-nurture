#!/usr/bin/env python3
"""
Quick test script to verify the lead nurture system is working.
Run this before deploying to production.
"""

import os
import sys

# Add execution directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

from dotenv import load_dotenv
load_dotenv()

def test_environment():
    """Test that environment variables are set."""
    print("\n=== Testing Environment Variables ===")

    api_key = os.getenv('CLOSE_IO_API_KEY')
    if not api_key:
        print("❌ CLOSE_IO_API_KEY not set in .env")
        return False

    print(f"✓ CLOSE_IO_API_KEY found: {api_key[:10]}...")

    test_email = os.getenv('TEST_EMAIL')
    if test_email:
        print(f"✓ TEST_EMAIL set: {test_email}")
    else:
        print("⚠ TEST_EMAIL not set (optional)")

    return True

def test_close_io_connection():
    """Test Close.io API connection."""
    print("\n=== Testing Close.io Connection ===")

    try:
        from close_io_client import CloseIOClient

        client = CloseIOClient()
        print("✓ Close.io client initialized")

        # Try to get leads
        leads = client.get_leads_with_upcoming_calls(days_ahead=30)
        print(f"✓ Successfully fetched leads: {len(leads)} with upcoming calls")

        if leads:
            lead = leads[0]
            name = client.get_lead_name(lead)
            email = client.get_lead_email(lead)
            print(f"  Example: {name} ({email})")
        else:
            print("  (No leads with upcoming calls found)")

        return True

    except Exception as e:
        print(f"❌ Error connecting to Close.io: {str(e)}")
        return False

def test_email_sender():
    """Test email sending capability."""
    print("\n=== Testing Email Sender ===")

    try:
        from send_email import EmailSender

        sender = EmailSender()
        print("✓ Email sender initialized with Close.io API")

        test_email = os.getenv('TEST_EMAIL')
        if not test_email:
            print("⚠ Skipping email send test (TEST_EMAIL not set)")
            print("  Set TEST_EMAIL in .env to test email sending")
            return True

        print(f"\nSending test email to {test_email}...")
        print("(Check your inbox)")

        success = sender.send_email(
            to_email=test_email,
            subject="Test Email - Lead Nurture System",
            html_content="<h1>Success!</h1><p>Your lead nurture system is working correctly.</p>",
            text_content="Success! Your lead nurture system is working correctly."
        )

        if success:
            print("✓ Test email sent successfully!")
            print("  Check your inbox and Close.io Sent folder")
        else:
            print("❌ Test email failed to send")
            return False

        return True

    except Exception as e:
        print(f"❌ Error with email sender: {str(e)}")
        return False

def test_email_templates():
    """Test email template generation."""
    print("\n=== Testing Email Templates ===")

    try:
        from email_templates import EmailTemplates

        templates = EmailTemplates()

        # Test welcome email
        welcome = templates.get_welcome_email(
            name="John",
            call_time="Monday, Jan 15 at 2:00 PM EST",
            call_duration=30
        )

        if welcome and 'subject' in welcome and 'html' in welcome:
            print("✓ Welcome email template works")
        else:
            print("❌ Welcome email template failed")
            return False

        # Test other templates
        templates.get_midpoint_email("John", "Monday, Jan 15 at 2:00 PM EST")
        print("✓ Midpoint email template works")

        templates.get_day_before_email("John", "Monday, Jan 15 at 2:00 PM EST")
        print("✓ Day-before email template works")

        templates.get_hour_before_email("John", "Monday, Jan 15 at 2:00 PM EST")
        print("✓ Hour-before email template works")

        return True

    except Exception as e:
        print(f"❌ Error with email templates: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Lead Nurture System - Test Suite")
    print("=" * 60)

    all_passed = True

    # Run tests
    all_passed &= test_environment()
    all_passed &= test_close_io_connection()
    all_passed &= test_email_templates()
    all_passed &= test_email_sender()

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nYour system is ready to run.")
        print("\nNext steps:")
        print("1. Customize email templates in execution/email_templates.py")
        print("2. Run: python execution/lead_nurture_orchestrator.py")
        print("3. Or run continuously: python execution/lead_nurture_orchestrator.py --continuous 300")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the errors above before running the system.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
