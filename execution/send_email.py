#!/usr/bin/env python3
"""
Email Sending Service
Handles sending emails via Close.io Email API with retry logic.
"""

import os
import json
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()


class EmailSender:
    """Handles email sending via Close.io Email API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize email sender with Close.io API.

        Args:
            api_key: Close.io API key (if not provided, loads from env)
        """
        self.api_key = api_key or os.getenv('CLOSE_IO_API_KEY')
        if not self.api_key:
            raise ValueError("Close.io API key not found in environment variables")

        self.base_url = "https://api.close.com/api/v1"
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

        # Track failed emails
        self.failed_log_path = os.path.join('.tmp', 'failed_emails.json')
        os.makedirs('.tmp', exist_ok=True)

        # Rate limiting
        self.requests_per_minute = 600
        self.request_times = []

        # Get the default email account for sending
        self.sender_account_id, self.sender_email = self._get_default_email_account()

    def _rate_limit(self):
        """Implement rate limiting to stay within API limits."""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.requests_per_minute:
            # Wait until oldest request is 60 seconds old
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_times = []

        self.request_times.append(now)

    def _get_default_email_account(self):
        """
        Get the default email account for sending emails.

        Returns:
            Tuple of (account_id, email_address)
        """
        try:
            response = self.session.get(f"{self.base_url}/email_account/")
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('data', [])
                if accounts:
                    # Return the first email account
                    account_id = accounts[0]['id']
                    email = accounts[0]['email']
                    print(f"Using sender email account: {email}")
                    return account_id, email

            raise ValueError("No email account found in Close.io. Please configure email sending.")
        except Exception as e:
            raise ValueError(f"Error getting email account: {str(e)}")

    def _find_lead_by_email(self, email: str) -> Optional[str]:
        """
        Find a lead ID by email address.

        Args:
            email: Email address to search for

        Returns:
            Lead ID if found, None otherwise
        """
        try:
            self._rate_limit()
            # Search for leads with this email
            response = self.session.get(
                f"{self.base_url}/lead/",
                params={'query': f'email:"{email}"'}
            )

            if response.status_code == 200:
                data = response.json()
                leads = data.get('data', [])
                if leads:
                    return leads[0]['id']

            return None
        except Exception as e:
            print(f"Error searching for lead: {str(e)}")
            return None

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        lead_id: Optional[str] = None,
        retry_count: int = 3
    ) -> bool:
        """
        Send an email via Close.io with retry logic.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of email
            text_content: Plain text version (optional)
            lead_id: Close.io lead ID (optional, helps with tracking)
            retry_count: Number of retry attempts on failure

        Returns:
            True if email sent successfully, False otherwise
        """
        for attempt in range(retry_count):
            try:
                success = self._send_via_closeio(
                    to_email, subject, html_content, text_content, lead_id
                )

                if success:
                    print(f"Email sent successfully to {to_email}: {subject}")
                    return True

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    # Exponential backoff
                    sleep_time = 2 ** attempt
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

        # All retries failed - log it
        self._log_failed_email(to_email, subject, html_content, text_content, lead_id)
        return False

    def _send_via_closeio(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        lead_id: Optional[str]
    ) -> bool:
        """
        Send email via Close.io Email API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content
            lead_id: Lead ID (optional)

        Returns:
            True if successful
        """
        self._rate_limit()

        # Close.io requires either lead_id or contact_id
        # If no lead_id provided, try to find a lead/contact with this email
        if not lead_id:
            lead_id = self._find_lead_by_email(to_email)

        # Prepare email payload
        payload = {
            'to': [to_email],
            'subject': subject,
            'body_html': html_content,
            'sender': self.sender_email,  # Required: sender email address
            'status': 'outbox'  # Send immediately
        }

        # Add plain text if provided
        if text_content:
            payload['body_text'] = text_content

        # Add lead_id (required by Close.io)
        if lead_id:
            payload['lead_id'] = lead_id
        else:
            # If still no lead_id, this will fail - Close.io requires it
            raise Exception(f"No lead found for email {to_email}. Create a lead in Close.io first.")

        # Send email via Close.io API
        url = f"{self.base_url}/activity/email/"
        response = self.session.post(url, json=payload)

        if response.status_code >= 400:
            raise Exception(f"Close.io API error: {response.status_code} - {response.text}")

        return response.status_code in [200, 201]

    def _log_failed_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        lead_id: Optional[str]
    ):
        """Log failed email attempts."""
        failed_email = {
            'timestamp': datetime.utcnow().isoformat(),
            'to_email': to_email,
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content,
            'lead_id': lead_id
        }

        # Load existing failures
        failures = []
        if os.path.exists(self.failed_log_path):
            with open(self.failed_log_path, 'r') as f:
                failures = json.load(f)

        failures.append(failed_email)

        # Save updated failures
        with open(self.failed_log_path, 'w') as f:
            json.dump(failures, f, indent=2)

        print(f"Failed email logged to {self.failed_log_path}")

    def get_failed_emails(self) -> List[Dict]:
        """
        Get list of failed emails.

        Returns:
            List of failed email dictionaries
        """
        if not os.path.exists(self.failed_log_path):
            return []

        with open(self.failed_log_path, 'r') as f:
            return json.load(f)

    def retry_failed_emails(self) -> Dict[str, int]:
        """
        Retry all failed emails.

        Returns:
            Dictionary with success and failure counts
        """
        failed_emails = self.get_failed_emails()
        if not failed_emails:
            print("No failed emails to retry")
            return {'success': 0, 'failed': 0}

        success_count = 0
        still_failed = []

        for email_data in failed_emails:
            success = self.send_email(
                email_data['to_email'],
                email_data['subject'],
                email_data['html_content'],
                email_data.get('text_content'),
                email_data.get('lead_id')
            )

            if success:
                success_count += 1
            else:
                still_failed.append(email_data)

        # Update failed log with only emails that still failed
        with open(self.failed_log_path, 'w') as f:
            json.dump(still_failed, f, indent=2)

        return {
            'success': success_count,
            'failed': len(still_failed)
        }


def main():
    """Test email sending via Close.io."""
    try:
        sender = EmailSender()
        print("Email sender initialized with Close.io API")

        # Test email
        test_email = os.getenv('TEST_EMAIL')
        if not test_email:
            print("Set TEST_EMAIL in .env to send a test email")
            return

        html_content = """
        <html>
            <body>
                <h1>Test Email</h1>
                <p>This is a test email from the lead nurture system.</p>
                <p>Sent via Close.io Email API!</p>
            </body>
        </html>
        """

        text_content = "Test Email\n\nThis is a test email from the lead nurture system.\nSent via Close.io Email API!"

        success = sender.send_email(
            to_email=test_email,
            subject="Test Email - Lead Nurture System (Close.io)",
            html_content=html_content,
            text_content=text_content
        )

        if success:
            print("Test email sent successfully!")
        else:
            print("Test email failed to send")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
