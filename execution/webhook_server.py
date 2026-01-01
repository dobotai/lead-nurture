#!/usr/bin/env python3
"""
Webhook Server for Lead Nurture
Simple HTTP server that receives webhook calls from lead capture systems
and instantly enrolls leads into the nurture workflow.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from enroll_lead import LeadEnrollment


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

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8080):
    """Run the webhook server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"Lead Nurture Webhook Server running on port {port}")
    print(f"Endpoint: http://localhost:{port}/enroll")
    print(f"Health check: http://localhost:{port}/health")
    print("\nWaiting for webhook calls...")
    httpd.serve_forever()


if __name__ == '__main__':
    import sys
    import os
    # Railway provides PORT env var, fallback to command line arg or 8080
    port = int(os.getenv('PORT', sys.argv[1] if len(sys.argv) > 1 else 8080))
    run_server(port)
