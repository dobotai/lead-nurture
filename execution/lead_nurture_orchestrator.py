#!/usr/bin/env python3
"""
Lead Nurture Orchestrator
Main workflow that monitors Close.io for booked calls and sends nurture emails.
"""

import os
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add execution directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from close_io_client import CloseIOClient
from send_email import EmailSender
from email_templates import EmailTemplates

load_dotenv()


class LeadNurtureOrchestrator:
    """Orchestrates the lead nurture workflow."""

    def __init__(self):
        """Initialize the orchestrator with necessary clients."""
        self.close_io = CloseIOClient()
        self.email_sender = EmailSender()
        self.templates = EmailTemplates()

        # State file tracking
        self.state_file = os.path.join('.tmp', 'lead_nurture_state.json')
        self.log_file = os.path.join('.tmp', 'nurture_log.json')

        # Ensure .tmp directory exists
        os.makedirs('.tmp', exist_ok=True)

        # Load state
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load nurture state from file."""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {'leads': {}}

    def _save_state(self):
        """Save nurture state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _log_activity(self, activity: Dict):
        """Log activity to log file."""
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                logs = json.load(f)

        activity['timestamp'] = datetime.utcnow().isoformat()
        logs.append(activity)

        # Keep only last 1000 entries
        logs = logs[-1000:]

        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def _format_call_time(self, iso_timestamp: str) -> str:
        """
        Format ISO timestamp to human-readable format.

        Args:
            iso_timestamp: ISO format timestamp

        Returns:
            Formatted string like "Monday, Jan 15 at 2:00 PM EST"
        """
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime("%A, %b %d at %I:%M %p %Z")

    def _calculate_email_times(self, call_time_str: str, booked_time: datetime) -> Dict[str, datetime]:
        """
        Calculate when each email should be sent.

        Args:
            call_time_str: ISO format call time string
            booked_time: When the call was booked

        Returns:
            Dictionary with email types and send times
        """
        call_time = datetime.fromisoformat(call_time_str.replace('Z', '+00:00'))
        now = datetime.utcnow().replace(tzinfo=call_time.tzinfo)

        # Calculate time until call
        time_until_call = call_time - now

        email_times = {}

        # Welcome: immediately (within 5 minutes of booking)
        email_times['welcome'] = booked_time + timedelta(minutes=5)

        # Hour before: 1 hour before call
        email_times['hour_before'] = call_time - timedelta(hours=1)

        # Day before: 24 hours before call
        email_times['day_before'] = call_time - timedelta(hours=24)

        # Midpoint: halfway between now and call (only if >48 hours away)
        if time_until_call > timedelta(hours=48):
            midpoint_time = now + (time_until_call / 2)
            email_times['midpoint'] = midpoint_time

        return email_times

    def _should_send_email(self, email_type: str, scheduled_time: datetime, sent_emails: List[str]) -> bool:
        """
        Determine if an email should be sent now.

        Args:
            email_type: Type of email (welcome, midpoint, etc.)
            scheduled_time: When email is scheduled to send
            sent_emails: List of email types already sent

        Returns:
            True if email should be sent now
        """
        if email_type in sent_emails:
            return False

        now = datetime.utcnow().replace(tzinfo=scheduled_time.tzinfo)
        return now >= scheduled_time

    def _send_nurture_email(
        self,
        lead_id: str,
        lead_email: str,
        lead_name: str,
        email_type: str,
        call_time: str,
        call_duration: int = 30,
        meeting_link: Optional[str] = None
    ) -> bool:
        """
        Send a specific nurture email.

        Args:
            lead_id: Close.io lead ID
            lead_email: Lead's email address
            lead_name: Lead's name
            email_type: Type of email to send
            call_time: Formatted call time string
            call_duration: Call duration in minutes
            meeting_link: Optional meeting link

        Returns:
            True if email sent successfully
        """
        # Get email template
        if email_type == 'welcome':
            email_data = self.templates.get_welcome_email(lead_name, call_time, call_duration)
        elif email_type == 'midpoint':
            email_data = self.templates.get_midpoint_email(lead_name, call_time)
        elif email_type == 'day_before':
            email_data = self.templates.get_day_before_email(lead_name, call_time, meeting_link)
        elif email_type == 'hour_before':
            email_data = self.templates.get_hour_before_email(lead_name, call_time, meeting_link)
        else:
            print(f"Unknown email type: {email_type}")
            return False

        # Send email (with lead_id for Close.io tracking)
        success = self.email_sender.send_email(
            to_email=lead_email,
            subject=email_data['subject'],
            html_content=email_data['html'],
            text_content=email_data['text'],
            lead_id=lead_id
        )

        if success:
            # Log to Close.io
            self.close_io.add_note_to_lead(
                lead_id,
                f"Lead nurture email sent: {email_type} - {email_data['subject']}"
            )

            # Log activity
            self._log_activity({
                'action': 'email_sent',
                'lead_id': lead_id,
                'email_type': email_type,
                'to_email': lead_email,
                'subject': email_data['subject']
            })

        return success

    def process_lead(self, lead: Dict) -> bool:
        """
        Process a single lead through the nurture workflow.

        Args:
            lead: Lead data from Close.io

        Returns:
            True if processing was successful
        """
        lead_id = lead['id']
        lead_email = self.close_io.get_lead_email(lead)
        lead_name = self.close_io.get_lead_name(lead)
        call_info = lead['call_info']
        call_time_iso = call_info['scheduled_time']
        call_status = call_info.get('status', 'scheduled')

        if not lead_email:
            print(f"No email found for lead {lead_id}, skipping")
            return False

        # Check if call is cancelled
        if call_status == 'cancelled':
            if lead_id in self.state['leads']:
                print(f"Call cancelled for lead {lead_id}, removing from nurture")
                del self.state['leads'][lead_id]
                self._save_state()
            return False

        # Initialize lead in state if new
        if lead_id not in self.state['leads']:
            now = datetime.utcnow()
            email_times = self._calculate_email_times(call_time_iso, now)

            self.state['leads'][lead_id] = {
                'email': lead_email,
                'name': lead_name,
                'call_time': call_time_iso,
                'call_duration': call_info.get('duration', 30),
                'meeting_link': None,  # TODO: Extract from Close.io if available
                'booked_at': now.isoformat(),
                'sent_emails': [],
                'email_schedule': {
                    k: v.isoformat() for k, v in email_times.items()
                }
            }
            self._save_state()

            print(f"New lead added to nurture: {lead_name} ({lead_email})")
            self._log_activity({
                'action': 'lead_added',
                'lead_id': lead_id,
                'lead_name': lead_name,
                'call_time': call_time_iso
            })

        # Get lead state
        lead_state = self.state['leads'][lead_id]

        # Check if call time changed (rescheduled)
        if lead_state['call_time'] != call_time_iso:
            print(f"Call rescheduled for lead {lead_id}, recalculating email times")
            booked_at = datetime.fromisoformat(lead_state['booked_at'])
            email_times = self._calculate_email_times(call_time_iso, booked_at)

            lead_state['call_time'] = call_time_iso
            lead_state['email_schedule'] = {
                k: v.isoformat() for k, v in email_times.items()
            }
            self._save_state()

            self._log_activity({
                'action': 'call_rescheduled',
                'lead_id': lead_id,
                'new_call_time': call_time_iso
            })

        # Check and send emails
        formatted_call_time = self._format_call_time(call_time_iso)

        for email_type, scheduled_time_str in lead_state['email_schedule'].items():
            scheduled_time = datetime.fromisoformat(scheduled_time_str)

            if self._should_send_email(email_type, scheduled_time, lead_state['sent_emails']):
                print(f"Sending {email_type} email to {lead_name} ({lead_email})")

                success = self._send_nurture_email(
                    lead_id=lead_id,
                    lead_email=lead_email,
                    lead_name=lead_name,
                    email_type=email_type,
                    call_time=formatted_call_time,
                    call_duration=lead_state['call_duration'],
                    meeting_link=lead_state.get('meeting_link')
                )

                if success:
                    lead_state['sent_emails'].append(email_type)
                    self._save_state()

        return True

    def run_once(self):
        """Run one iteration of the nurture workflow."""
        print(f"\n=== Running nurture workflow at {datetime.utcnow().isoformat()} ===")

        # Get leads with upcoming calls
        leads = self.close_io.get_leads_with_upcoming_calls(days_ahead=30)
        print(f"Found {len(leads)} leads with upcoming calls")

        # Process each lead
        for lead in leads:
            try:
                self.process_lead(lead)
            except Exception as e:
                print(f"Error processing lead {lead.get('id')}: {str(e)}")
                self._log_activity({
                    'action': 'error',
                    'lead_id': lead.get('id'),
                    'error': str(e)
                })

        # Clean up leads with past calls
        self._cleanup_past_calls()

        print(f"=== Workflow iteration complete ===\n")

    def _cleanup_past_calls(self):
        """Remove leads from state whose calls have already happened."""
        now = datetime.utcnow()
        to_remove = []

        for lead_id, lead_state in self.state['leads'].items():
            call_time = datetime.fromisoformat(lead_state['call_time'].replace('Z', '+00:00'))

            # Remove if call was more than 1 hour ago
            if call_time < now - timedelta(hours=1):
                to_remove.append(lead_id)

        for lead_id in to_remove:
            print(f"Removing completed call for lead {lead_id}")
            del self.state['leads'][lead_id]

        if to_remove:
            self._save_state()

    def run_continuous(self, check_interval_seconds: int = 300):
        """
        Run the nurture workflow continuously.

        Args:
            check_interval_seconds: How often to check for new leads (default 5 minutes)
        """
        print(f"Starting continuous nurture workflow (checking every {check_interval_seconds}s)")

        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                print("\nStopping nurture workflow...")
                break
            except Exception as e:
                print(f"Error in workflow: {str(e)}")
                self._log_activity({
                    'action': 'workflow_error',
                    'error': str(e)
                })

            # Wait before next iteration
            time.sleep(check_interval_seconds)


def main():
    """Main entry point."""
    import sys

    orchestrator = LeadNurtureOrchestrator()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Run continuously
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        orchestrator.run_continuous(check_interval_seconds=interval)
    else:
        # Run once
        orchestrator.run_once()


if __name__ == "__main__":
    main()
