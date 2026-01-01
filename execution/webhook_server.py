#!/usr/bin/env python3
"""
Webhook Server for Lead Nurture
Simple HTTP server that receives webhook calls from lead capture systems
and instantly enrolls leads into the nurture workflow.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone

# Add execution directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from enroll_lead import LeadEnrollment
from close_io_client import CloseIOClient
from send_email import EmailSender
from email_templates import EmailTemplates


class WebhookHandler(BaseHTTPRequestHandler):
    """Handles incoming webhook requests."""

    def do_POST(self):
        """Handle POST requests for lead enrollment."""
        if self.path == '/enroll':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Parse JSON payload
                data = json.loads(post_data.decode('utf-8'))

                # Extract lead info
                lead_id = data.get('lead_id')
                email = data.get('email')
                name = data.get('name')
                call_time = data.get('call_time')
                call_duration = data.get('call_duration', 30)

                # Enroll lead
                enrollment = LeadEnrollment()
                result = enrollment.enroll_lead(
                    lead_id=lead_id,
                    email=email,
                    name=name,
                    call_time=call_time,
                    call_duration=call_duration,
                    send_welcome_immediately=True
                )

                # Send response
                self.send_response(200 if result['success'] else 400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))

                print(f"\nWebhook processed: {result.get('email', 'unknown')}")

            except Exception as e:
                # Error response
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                print(f"\nWebhook error: {str(e)}")

        elif self.path == '/closeio-webhook':
            # Handle Close.io webhooks
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Parse Close.io webhook payload
                data = json.loads(post_data.decode('utf-8'))
                event = data.get('event')

                # Process opportunity.status_change events
                if event == 'opportunity.status_change':
                    opp_data = data.get('data', {})
                    lead_id = opp_data.get('lead_id')
                    new_status = opp_data.get('status_label', '').lower()
                    old_status = opp_data.get('old_status_label', '').lower()

                    print(f"\nOpportunity status changed for lead {lead_id}: {old_status} → {new_status}")

                    # Check if status changed TO "Call Booked"
                    if new_status == 'call booked':
                        print(f"Call booked! Enrolling lead {lead_id} in nurture workflow")

                        # Get call time from lead activities
                        call_time = self._extract_call_time(lead_id)

                        # Enroll lead in nurture workflow
                        enrollment = LeadEnrollment()
                        result = enrollment.enroll_lead(
                            lead_id=lead_id,
                            call_time=call_time,
                            send_welcome_immediately=True
                        )

                        # Send response
                        self.send_response(200 if result['success'] else 400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode('utf-8'))

                        print(f"Lead enrolled: {result.get('email', 'unknown')}")

                    # Check if status changed FROM "Call Booked" to anything else
                    elif old_status == 'call booked' and new_status != 'call booked':
                        print(f"Status changed from Call Booked! Cancelling nurture for lead {lead_id}")

                        # Cancel nurture workflow
                        result = self._cancel_nurture(lead_id)

                        # Send response
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode('utf-8'))

                        print(f"Nurture cancelled for lead: {lead_id}")

                    else:
                        # Status change not relevant to nurture workflow
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {'status': 'ignored', 'reason': 'status not relevant'}
                        self.wfile.write(json.dumps(response).encode('utf-8'))

                else:
                    # Ignore other events
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'status': 'ignored', 'event': event}
                    self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                # Error response
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                print(f"\nClose.io webhook error: {str(e)}")

        elif self.path == '/health':
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'ok', 'service': 'lead-nurture-webhook'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'ok', 'service': 'lead-nurture-webhook'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def _extract_call_time(self, lead_id: str):
        """
        Extract scheduled call time from lead activities.

        Args:
            lead_id: Close.io lead ID

        Returns:
            ISO format datetime string or None
        """
        try:
            client = CloseIOClient()

            # Get lead activities
            response = client.session.get(
                f'{client.base_url}/activity/',
                params={'lead_id': lead_id, '_type': 'Meeting'}
            )

            activities = response.json().get('data', [])

            # Find the first scheduled meeting
            for activity in activities:
                if activity.get('date_scheduled'):
                    return activity['date_scheduled']

            return None

        except Exception as e:
            print(f"Error extracting call time: {str(e)}")
            return None

    def _cancel_nurture(self, lead_id: str):
        """
        Cancel nurture workflow for a lead by removing them from state.

        Args:
            lead_id: Close.io lead ID

        Returns:
            dict with success status and message
        """
        try:
            state_file = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'lead_nurture_state.json')

            # Load current state
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
            else:
                return {'success': False, 'message': 'No active nurture workflows found'}

            # Check if lead exists in state
            if lead_id not in state.get('leads', {}):
                return {'success': False, 'message': f'Lead {lead_id} not found in nurture workflow'}

            # Get lead info before removing
            lead_info = state['leads'][lead_id]
            email = lead_info.get('email', 'unknown')

            # Remove lead from state
            del state['leads'][lead_id]

            # Save updated state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

            # Log the cancellation
            log_file = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'nurture_log.json')
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'cancel_nurture',
                'lead_id': lead_id,
                'email': email,
                'reason': 'opportunity_status_changed'
            }

            # Append to log
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)

            logs.append(log_entry)

            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

            print(f"Cancelled nurture for lead {lead_id} ({email})")

            return {
                'success': True,
                'message': f'Nurture cancelled for lead {lead_id}',
                'email': email
            }

        except Exception as e:
            print(f"Error cancelling nurture: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def send_scheduled_emails():
    """Background thread that sends scheduled emails."""
    print("Starting email scheduler thread...")

    email_sender = EmailSender()
    templates = EmailTemplates()
    close_io = CloseIOClient()

    state_file = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'lead_nurture_state.json')

    while True:
        try:
            # Load current state
            if not os.path.exists(state_file):
                time.sleep(30)
                continue

            with open(state_file, 'r') as f:
                state = json.load(f)

            now = datetime.now(timezone.utc)

            # Check each lead for scheduled emails
            for lead_id, lead_data in state.get('leads', {}).items():
                sent_emails = lead_data.get('sent_emails', [])
                email_schedule = lead_data.get('email_schedule', {})

                # Check each scheduled email
                for email_type, scheduled_time_str in email_schedule.items():
                    # Skip if already sent
                    if email_type in sent_emails:
                        continue

                    # Skip welcome (sent immediately on enrollment)
                    if email_type == 'welcome':
                        continue

                    # Parse scheduled time
                    scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))

                    # Check if it's time to send
                    if now >= scheduled_time:
                        print(f"\nSending {email_type} email to {lead_data.get('email')}")

                        # Format call time
                        call_time = datetime.fromisoformat(lead_data['call_time'].replace('Z', '+00:00'))
                        formatted_call_time = call_time.strftime("%A, %b %d at %I:%M %p %Z")

                        # Get template
                        if email_type == 'midpoint':
                            email_data = templates.get_midpoint_email(lead_data['name'], formatted_call_time)
                        elif email_type == 'day_before':
                            email_data = templates.get_day_before_email(lead_data['name'], formatted_call_time)
                        elif email_type == 'hour_before':
                            email_data = templates.get_hour_before_email(lead_data['name'], formatted_call_time)
                        else:
                            continue

                        # Send email
                        success = email_sender.send_email(
                            to_email=lead_data['email'],
                            subject=email_data['subject'],
                            html_content=email_data['html'],
                            text_content=email_data['text'],
                            lead_id=lead_id
                        )

                        if success:
                            # Mark as sent
                            sent_emails.append(email_type)
                            lead_data['sent_emails'] = sent_emails

                            # Save state
                            with open(state_file, 'w') as f:
                                json.dump(state, f, indent=2)

                            # Add note to Close.io
                            close_io.add_note_to_lead(
                                lead_id,
                                f"Lead nurture email sent: {email_type} - {email_data['subject']}"
                            )

                            print(f"✓ {email_type} email sent to {lead_data['email']}")

        except Exception as e:
            print(f"Error in email scheduler: {str(e)}")

        # Check every 30 seconds
        time.sleep(30)


def run_server(port=8080):
    """Run the webhook server with background email scheduler."""
    # Start background email scheduler thread
    scheduler_thread = threading.Thread(target=send_scheduled_emails, daemon=True)
    scheduler_thread.start()

    # Start webhook server
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"Lead Nurture Webhook Server running on port {port}")
    print(f"Endpoint: http://localhost:{port}/closeio-webhook")
    print(f"Health check: http://localhost:{port}/health")
    print("\nEmail scheduler running (checking every 30s)")
    print("Waiting for webhook calls...")
    httpd.serve_forever()


if __name__ == '__main__':
    import sys
    import os
    # Railway provides PORT env var, fallback to command line arg or 8080
    port = int(os.getenv('PORT', sys.argv[1] if len(sys.argv) > 1 else 8080))
    run_server(port)
