#!/usr/bin/env python3
"""
Close.io Webhook Handler
Handles webhooks from Close.io when leads are created or updated.
Automatically enrolls new leads into the nurture workflow.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# Add execution directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from enroll_lead import LeadEnrollment
from close_io_client import CloseIOClient


class CloseIOWebhookHandler(BaseHTTPRequestHandler):
    """Handles incoming webhooks from Close.io."""

    def do_POST(self):
        """Handle POST requests from Close.io webhooks."""
        if self.path == '/closeio-webhook':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Parse Close.io webhook payload
                data = json.loads(post_data.decode('utf-8'))

                event = data.get('event')

                # Only process lead.created events
                if event == 'lead.created':
                    lead_data = data.get('data', {})
                    lead_id = lead_data.get('id')

                    print(f"New lead created in Close.io: {lead_id}")

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
                print(f"Webhook error: {str(e)}")

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

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8080):
    """Run the Close.io webhook server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CloseIOWebhookHandler)
    print(f"Close.io Webhook Handler running on port {port}")
    print(f"Endpoint: http://localhost:{port}/closeio-webhook")
    print("\nWaiting for Close.io webhooks...")
    httpd.serve_forever()


if __name__ == '__main__':
    import sys
    import os
    # Railway provides PORT env var, fallback to command line arg or 8080
    port = int(os.getenv('PORT', sys.argv[1] if len(sys.argv) > 1 else 8080))
    run_server(port)
