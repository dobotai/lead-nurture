#!/usr/bin/env python3
"""
Lead Enrollment Script
Instantly enrolls a lead into the nurture workflow when called.
Can be triggered by webhook, API call, or lead capture system.
"""

import os
import json
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

# Add execution directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from close_io_client import CloseIOClient
from send_email import EmailSender
from email_templates import EmailTemplates

load_dotenv()


class LeadEnrollment:
    """Handles instant enrollment of leads into nurture workflow."""

    def __init__(self):
        """Initialize enrollment handler."""
        self.close_io = CloseIOClient()
        self.email_sender = EmailSender()
        self.templates = EmailTemplates()
        self.state_file = os.path.join('.tmp', 'lead_nurture_state.json')
        self.log_file = os.path.join('.tmp', 'nurture_log.json')

        os.makedirs('.tmp', exist_ok=True)

    def _load_state(self) -> Dict:
        """Load nurture state from file."""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {'leads': {}}

    def _save_state(self, state: Dict):
        """Save nurture state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _log_activity(self, activity: Dict):
        """Log activity to log file."""
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

        activity['timestamp'] = datetime.now(timezone.utc).isoformat()
        logs.append(activity)

        # Keep only last 1000 entries
        logs = logs[-1000:]

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def _calculate_email_times(self, call_time: datetime, booked_time: datetime) -> Dict[str, datetime]:
        """Calculate when each email should be sent - TEST MODE: 1 email per minute."""
        now = datetime.now(timezone.utc)

        email_times = {}

        # TEST SCHEDULE: Send emails every minute for testing
        # Welcome: immediately
        email_times['welcome'] = booked_time + timedelta(seconds=10)

        # Minute 1: First follow-up
        email_times['midpoint'] = now + timedelta(minutes=1)

        # Minute 2: Second follow-up
        email_times['day_before'] = now + timedelta(minutes=2)

        # Minute 3: Final reminder
        email_times['hour_before'] = now + timedelta(minutes=3)

        return email_times

    def _format_call_time(self, call_time: datetime) -> str:
        """Format datetime to human-readable string."""
        return call_time.strftime("%A, %b %d at %I:%M %p %Z")

    def enroll_lead(
        self,
        lead_id: str = None,
        email: str = None,
        name: str = None,
        call_time: str = None,
        call_duration: int = 30,
        send_welcome_immediately: bool = True
    ) -> Dict:
        """
        Enroll a lead into the nurture workflow.

        Args:
            lead_id: Close.io lead ID (optional, will search by email if not provided)
            email: Lead's email address
            name: Lead's name (optional, will fetch from Close.io if not provided)
            call_time: ISO format datetime of scheduled call (optional)
            call_duration: Call duration in minutes (default 30)
            send_welcome_immediately: Send welcome email immediately (default True)

        Returns:
            Dictionary with enrollment status and details
        """
        # Find lead if only email provided
        if not lead_id and email:
            lead_id = self.email_sender._find_lead_by_email(email)
            if not lead_id:
                return {
                    'success': False,
                    'error': f'No lead found with email {email}. Create lead in Close.io first.'
                }

        if not lead_id:
            return {
                'success': False,
                'error': 'Either lead_id or email must be provided'
            }

        # Get lead details from Close.io
        lead = self.close_io.get_lead(lead_id)

        if not email:
            email = self.close_io.get_lead_email(lead)

        if not name:
            name = self.close_io.get_lead_name(lead)

        if not email:
            return {
                'success': False,
                'error': f'Lead {lead_id} has no email address'
            }

        # Parse or set call time
        if call_time:
            # Parse ISO format call time
            call_time_dt = datetime.fromisoformat(call_time.replace('Z', '+00:00'))
        else:
            # Default: schedule call 3 days from now if not provided
            call_time_dt = datetime.now(timezone.utc) + timedelta(days=3)

        # Calculate email schedule
        booked_time = datetime.now(timezone.utc)
        email_times = self._calculate_email_times(call_time_dt, booked_time)

        # Load current state
        state = self._load_state()

        # Add lead to state
        state['leads'][lead_id] = {
            'email': email,
            'name': name,
            'call_time': call_time_dt.isoformat(),
            'call_duration': call_duration,
            'meeting_link': None,
            'booked_at': booked_time.isoformat(),
            'sent_emails': [],
            'email_schedule': {
                k: v.isoformat() for k, v in email_times.items()
            }
        }

        # Save state
        self._save_state(state)

        # Log enrollment
        self._log_activity({
            'action': 'lead_enrolled',
            'lead_id': lead_id,
            'email': email,
            'name': name,
            'call_time': call_time_dt.isoformat(),
            'enrollment_method': 'instant_webhook'
        })

        print(f"Lead enrolled: {name} ({email})")
        print(f"Call scheduled: {call_time_dt.isoformat()}")
        print(f"Email schedule calculated")

        # Send welcome email immediately if requested
        if send_welcome_immediately:
            formatted_call_time = self._format_call_time(call_time_dt)

            email_data = self.templates.get_welcome_email(
                name=name,
                call_time=formatted_call_time,
                call_duration=call_duration
            )

            success = self.email_sender.send_email(
                to_email=email,
                subject=email_data['subject'],
                html_content=email_data['html'],
                text_content=email_data['text'],
                lead_id=lead_id
            )

            if success:
                # Mark welcome as sent
                state['leads'][lead_id]['sent_emails'].append('welcome')
                self._save_state(state)

                # Log to Close.io
                self.close_io.add_note_to_lead(
                    lead_id,
                    f"Lead nurture email sent: welcome - {email_data['subject']}"
                )

                print(f"Welcome email sent to {email}")

                return {
                    'success': True,
                    'lead_id': lead_id,
                    'email': email,
                    'name': name,
                    'call_time': call_time_dt.isoformat(),
                    'welcome_email_sent': True,
                    'emails_scheduled': list(email_times.keys())
                }
            else:
                return {
                    'success': True,
                    'lead_id': lead_id,
                    'email': email,
                    'name': name,
                    'call_time': call_time_dt.isoformat(),
                    'welcome_email_sent': False,
                    'error': 'Enrollment succeeded but welcome email failed',
                    'emails_scheduled': list(email_times.keys())
                }

        return {
            'success': True,
            'lead_id': lead_id,
            'email': email,
            'name': name,
            'call_time': call_time_dt.isoformat(),
            'welcome_email_sent': False,
            'emails_scheduled': list(email_times.keys())
        }


def main():
    """Command line interface for lead enrollment."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  By email:    python enroll_lead.py email@example.com")
        print("  By lead ID:  python enroll_lead.py lead_xxxxx")
        print("  With call:   python enroll_lead.py email@example.com '2025-01-15T14:00:00Z'")
        print("")
        print("Examples:")
        print("  python enroll_lead.py justin@dobotai.com")
        print("  python enroll_lead.py lead_abc123")
        print("  python enroll_lead.py doby@dobotai.com '2025-01-15T14:00:00Z'")
        return

    enrollment = LeadEnrollment()

    # Parse arguments
    arg1 = sys.argv[1]
    call_time = sys.argv[2] if len(sys.argv) > 2 else None

    # Determine if arg1 is email or lead_id
    if arg1.startswith('lead_'):
        result = enrollment.enroll_lead(lead_id=arg1, call_time=call_time)
    else:
        result = enrollment.enroll_lead(email=arg1, call_time=call_time)

    # Print result
    print("\n" + "="*60)
    if result['success']:
        print("SUCCESS! Lead enrolled in nurture workflow")
        print(f"Lead ID: {result['lead_id']}")
        print(f"Email: {result['email']}")
        print(f"Name: {result['name']}")
        print(f"Call Time: {result['call_time']}")
        print(f"Welcome Email Sent: {result.get('welcome_email_sent', False)}")
        print(f"Emails Scheduled: {', '.join(result['emails_scheduled'])}")
    else:
        print("FAILED!")
        print(f"Error: {result['error']}")
    print("="*60)


if __name__ == "__main__":
    main()
