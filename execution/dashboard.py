#!/usr/bin/env python3
"""
Lead Nurture Dashboard
Simple web interface to view leads in the nurture workflow.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DashboardHandler(BaseHTTPRequestHandler):
    """Handles dashboard requests."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/dashboard':
            self.serve_dashboard()
        elif self.path == '/api/leads':
            self.serve_leads_api()
        else:
            self.send_response(404)
            self.end_headers()

    def serve_dashboard(self):
        """Serve the dashboard HTML page."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lead Nurture Dashboard - DobotAI</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }

                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }

                .header {
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }

                .header h1 {
                    color: #2d3748;
                    font-size: 28px;
                    margin-bottom: 8px;
                }

                .header p {
                    color: #718096;
                    font-size: 14px;
                }

                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }

                .stat-card h3 {
                    color: #718096;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 8px;
                }

                .stat-card .number {
                    color: #2d3748;
                    font-size: 32px;
                    font-weight: bold;
                }

                .leads-container {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }

                .leads-header {
                    background: #f7fafc;
                    padding: 20px;
                    border-bottom: 1px solid #e2e8f0;
                }

                .leads-header h2 {
                    color: #2d3748;
                    font-size: 20px;
                }

                .lead-card {
                    padding: 20px;
                    border-bottom: 1px solid #e2e8f0;
                    transition: background 0.2s;
                }

                .lead-card:hover {
                    background: #f7fafc;
                }

                .lead-card:last-child {
                    border-bottom: none;
                }

                .lead-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 12px;
                }

                .lead-info h3 {
                    color: #2d3748;
                    font-size: 18px;
                    margin-bottom: 4px;
                }

                .lead-info p {
                    color: #718096;
                    font-size: 14px;
                }

                .lead-badge {
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    background: #48bb78;
                    color: white;
                }

                .email-progress {
                    display: flex;
                    gap: 8px;
                    margin-top: 12px;
                }

                .email-step {
                    flex: 1;
                    height: 8px;
                    background: #e2e8f0;
                    border-radius: 4px;
                    position: relative;
                    overflow: hidden;
                }

                .email-step.sent {
                    background: #48bb78;
                }

                .email-step.scheduled {
                    background: #ecc94b;
                }

                .email-details {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 12px;
                    margin-top: 12px;
                    padding-top: 12px;
                    border-top: 1px solid #e2e8f0;
                }

                .email-detail {
                    font-size: 12px;
                }

                .email-detail .label {
                    color: #718096;
                    margin-bottom: 2px;
                }

                .email-detail .value {
                    color: #2d3748;
                    font-weight: 500;
                }

                .empty-state {
                    padding: 60px 20px;
                    text-align: center;
                    color: #718096;
                }

                .empty-state h3 {
                    font-size: 20px;
                    margin-bottom: 8px;
                }

                .refresh-btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .refresh-btn:hover {
                    background: #5a67d8;
                }

                .loading {
                    text-align: center;
                    padding: 40px;
                    color: #718096;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Lead Nurture Dashboard</h1>
                    <p>Monitor active leads in the email nurture workflow</p>
                </div>

                <div class="stats" id="stats">
                    <div class="stat-card">
                        <h3>Active Leads</h3>
                        <div class="number" id="active-count">-</div>
                    </div>
                    <div class="stat-card">
                        <h3>Emails Sent Today</h3>
                        <div class="number" id="emails-sent">-</div>
                    </div>
                    <div class="stat-card">
                        <h3>Emails Scheduled</h3>
                        <div class="number" id="emails-scheduled">-</div>
                    </div>
                </div>

                <div class="leads-container">
                    <div class="leads-header">
                        <h2>Active Leads</h2>
                    </div>
                    <div id="leads-list" class="loading">
                        Loading leads...
                    </div>
                </div>
            </div>

            <script>
                function formatDate(dateStr) {
                    const date = new Date(dateStr);
                    return date.toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true
                    });
                }

                function formatRelativeTime(dateStr) {
                    const date = new Date(dateStr);
                    const now = new Date();
                    const diffMs = date - now;
                    const diffMins = Math.floor(diffMs / 60000);
                    const diffHours = Math.floor(diffMs / 3600000);
                    const diffDays = Math.floor(diffMs / 86400000);

                    if (diffMs < 0) {
                        return 'Past due';
                    } else if (diffMins < 60) {
                        return `in ${diffMins}m`;
                    } else if (diffHours < 24) {
                        return `in ${diffHours}h`;
                    } else {
                        return `in ${diffDays}d`;
                    }
                }

                function renderLeads(data) {
                    const leads = data.leads;
                    const leadsList = document.getElementById('leads-list');

                    // Update stats
                    document.getElementById('active-count').textContent = data.total_leads;
                    document.getElementById('emails-sent').textContent = data.total_emails_sent;
                    document.getElementById('emails-scheduled').textContent = data.total_emails_scheduled;

                    if (leads.length === 0) {
                        leadsList.innerHTML = `
                            <div class="empty-state">
                                <h3>No active leads</h3>
                                <p>Leads will appear here when they are enrolled in the nurture workflow</p>
                            </div>
                        `;
                        return;
                    }

                    leadsList.innerHTML = leads.map(lead => `
                        <div class="lead-card">
                            <div class="lead-header">
                                <div class="lead-info">
                                    <h3>${lead.name}</h3>
                                    <p>${lead.email}</p>
                                </div>
                                <span class="lead-badge">${lead.emails_sent_count}/5 sent</span>
                            </div>

                            <div class="email-progress">
                                ${[1,2,3,4,5].map(num => `
                                    <div class="email-step ${lead.emails_sent.includes('email_' + num) ? 'sent' : 'scheduled'}"
                                         title="Email ${num}: ${lead.emails_sent.includes('email_' + num) ? 'Sent' : 'Scheduled'}">
                                    </div>
                                `).join('')}
                            </div>

                            <div class="email-details">
                                <div class="email-detail">
                                    <div class="label">Enrolled</div>
                                    <div class="value">${formatDate(lead.booked_at)}</div>
                                </div>
                                <div class="email-detail">
                                    <div class="label">Call Time</div>
                                    <div class="value">${formatDate(lead.call_time)}</div>
                                </div>
                                <div class="email-detail">
                                    <div class="label">Next Email</div>
                                    <div class="value">${lead.next_email ? formatRelativeTime(lead.next_email.time) : 'None'}</div>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }

                function loadLeads() {
                    fetch('/api/leads')
                        .then(response => response.json())
                        .then(data => renderLeads(data))
                        .catch(error => {
                            document.getElementById('leads-list').innerHTML = `
                                <div class="empty-state">
                                    <h3>Error loading leads</h3>
                                    <p>${error.message}</p>
                                </div>
                            `;
                        });
                }

                // Load leads on page load
                loadLeads();

                // Refresh every 30 seconds
                setInterval(loadLeads, 30000);
            </script>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_leads_api(self):
        """Serve leads data as JSON API."""
        try:
            # Load state file
            state_file = os.path.join(os.path.dirname(__file__), '..', '.tmp', 'lead_nurture_state.json')

            if not os.path.exists(state_file):
                data = {
                    'total_leads': 0,
                    'total_emails_sent': 0,
                    'total_emails_scheduled': 0,
                    'leads': []
                }
            else:
                with open(state_file, 'r') as f:
                    state = json.load(f)

                leads_data = []
                total_emails_sent = 0
                total_emails_scheduled = 0
                now = datetime.utcnow()

                for lead_id, lead_info in state.get('leads', {}).items():
                    sent_emails = lead_info.get('sent_emails', [])
                    email_schedule = lead_info.get('email_schedule', {})

                    # Find next scheduled email
                    next_email = None
                    for email_type, scheduled_time in email_schedule.items():
                        if email_type not in sent_emails:
                            scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                            if next_email is None or scheduled_dt < datetime.fromisoformat(next_email['time'].replace('Z', '+00:00')):
                                next_email = {
                                    'type': email_type,
                                    'time': scheduled_time
                                }

                    total_emails_sent += len(sent_emails)
                    total_emails_scheduled += len(email_schedule) - len(sent_emails)

                    leads_data.append({
                        'lead_id': lead_id,
                        'name': lead_info.get('name', 'Unknown'),
                        'email': lead_info.get('email', ''),
                        'call_time': lead_info.get('call_time', ''),
                        'booked_at': lead_info.get('booked_at', ''),
                        'emails_sent': sent_emails,
                        'emails_sent_count': len(sent_emails),
                        'total_emails': len(email_schedule),
                        'next_email': next_email
                    })

                # Sort by booked_at (most recent first)
                leads_data.sort(key=lambda x: x['booked_at'], reverse=True)

                data = {
                    'total_leads': len(leads_data),
                    'total_emails_sent': total_emails_sent,
                    'total_emails_scheduled': total_emails_scheduled,
                    'leads': leads_data,
                    'last_updated': datetime.utcnow().isoformat()
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def log_message(self, format, *args):
        """Suppress HTTP request logs."""
        pass


def run_dashboard(port=8081):
    """Run the dashboard server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"\n{'='*60}")
    print(f"Lead Nurture Dashboard running at:")
    print(f"http://localhost:{port}/dashboard")
    print(f"{'='*60}\n")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down dashboard...")
        httpd.shutdown()


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    run_dashboard(port)
