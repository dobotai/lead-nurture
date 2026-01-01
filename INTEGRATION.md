# Lead Capture Integration Guide

This guide shows you how to trigger the lead nurture workflow **instantly** when a lead is captured, instead of waiting for the polling interval.

## Integration Options

### Option 1: Direct API Call (Recommended)

Call the enrollment script directly from your lead capture system.

**Python Example:**
```python
from execution.enroll_lead import LeadEnrollment

enrollment = LeadEnrollment()
result = enrollment.enroll_lead(
    email="newlead@example.com",
    name="John Doe",
    call_time="2025-01-15T14:00:00Z",  # ISO format
    call_duration=30
)

print(result)
```

**Command Line:**
```bash
# By email only (will look up lead in Close.io)
python execution/enroll_lead.py newlead@example.com

# With specific call time
python execution/enroll_lead.py newlead@example.com "2025-01-15T14:00:00Z"

# By Close.io lead ID
python execution/enroll_lead.py lead_xxxxx "2025-01-15T14:00:00Z"
```

---

### Option 2: Webhook Server

Run a local webhook server that your lead capture system can call.

**Start the server:**
```bash
python execution/webhook_server.py 8080
```

**Call the webhook:**
```bash
curl -X POST http://localhost:8080/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newlead@example.com",
    "name": "John Doe",
    "call_time": "2025-01-15T14:00:00Z",
    "call_duration": 30
  }'
```

**Response:**
```json
{
  "success": true,
  "lead_id": "lead_xxxxx",
  "email": "newlead@example.com",
  "name": "John",
  "call_time": "2025-01-15T14:00:00Z",
  "welcome_email_sent": true,
  "emails_scheduled": ["welcome", "midpoint", "day_before", "hour_before"]
}
```

---

### Option 3: Close.io Webhook (Native Integration)

Use Close.io's native webhooks to trigger enrollment when leads are created or updated.

**Setup:**

1. **In Close.io**, go to Settings → Webhooks
2. **Create webhook** for "Lead Created" event
3. **Set URL** to your webhook endpoint (use ngrok for local testing)
4. **Process webhook** in your handler:

```python
# webhook_handler.py
from flask import Flask, request, jsonify
from execution.enroll_lead import LeadEnrollment

app = Flask(__name__)

@app.route('/closeio-webhook', methods=['POST'])
def handle_closeio_webhook():
    data = request.json

    # Close.io sends lead data in webhook
    if data.get('event') == 'lead.created':
        lead_id = data['data']['id']

        # Enroll in nurture
        enrollment = LeadEnrollment()
        result = enrollment.enroll_lead(lead_id=lead_id)

        return jsonify(result)

    return jsonify({'status': 'ignored'})

if __name__ == '__main__':
    app.run(port=8080)
```

---

### Option 4: Zapier/Make Integration

**Zapier Flow:**
```
Trigger: New Lead in Close.io
  ↓
Action: Webhooks by Zapier → POST
  URL: http://your-server:8080/enroll
  Body: {"email": "{{email}}", "name": "{{name}}", "call_time": "{{scheduled_call}}"}
```

**Make.com Flow:**
```
1. Close.io: Watch Leads (Trigger)
2. HTTP: Make a Request (POST to your webhook)
3. Close.io: Update Lead (mark as enrolled - optional)
```

---

## Integration with Common Tools

### Calendly Integration

When someone books via Calendly:

**Option A: Calendly Webhook → Your Server**
```python
from flask import Flask, request
from execution.enroll_lead import LeadEnrollment
from datetime import datetime

app = Flask(__name__)

@app.route('/calendly-webhook', methods=['POST'])
def handle_calendly():
    data = request.json
    event = data['payload']

    # Extract info
    email = event['email']
    name = event['name']
    scheduled_time = event['scheduled_event']['start_time']

    # Enroll lead
    enrollment = LeadEnrollment()
    result = enrollment.enroll_lead(
        email=email,
        name=name,
        call_time=scheduled_time
    )

    return {'status': 'enrolled'}
```

**Option B: Calendly → Zapier → Webhook**
1. Trigger: Calendly - Invitee Created
2. Action: Create/Update Lead in Close.io
3. Action: POST to your webhook endpoint

### Cal.com Integration

Similar to Calendly, Cal.com has webhooks:

```javascript
// cal.com webhook payload
{
  "triggerEvent": "BOOKING_CREATED",
  "payload": {
    "email": "lead@example.com",
    "name": "Lead Name",
    "startTime": "2025-01-15T14:00:00Z"
  }
}
```

### Manual Form Integration

If you have a custom booking form:

```python
# In your form handler
from execution.enroll_lead import LeadEnrollment

@app.route('/submit-booking', methods=['POST'])
def submit_booking():
    email = request.form['email']
    name = request.form['name']
    call_time = request.form['call_time']

    # Create lead in Close.io first
    # ... (your Close.io lead creation code)

    # Enroll in nurture immediately
    enrollment = LeadEnrollment()
    result = enrollment.enroll_lead(
        email=email,
        name=name,
        call_time=call_time
    )

    if result['success']:
        return "Booking confirmed! Check your email."
    else:
        return "Error enrolling in nurture"
```

---

## Deployment Options

### Local Development
```bash
python execution/webhook_server.py 8080
```

### Production with ngrok (for testing)
```bash
# Terminal 1: Start webhook server
python execution/webhook_server.py 8080

# Terminal 2: Expose via ngrok
ngrok http 8080

# Use the ngrok URL in your webhooks
# https://abc123.ngrok.io/enroll
```

### Production on Server
```bash
# Using gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 execution.webhook_server:app

# Using systemd service
sudo nano /etc/systemd/system/lead-nurture-webhook.service
```

### Cloud Functions (Serverless)

**AWS Lambda:**
```python
import json
from execution.enroll_lead import LeadEnrollment

def lambda_handler(event, context):
    body = json.loads(event['body'])

    enrollment = LeadEnrollment()
    result = enrollment.enroll_lead(**body)

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

**Google Cloud Functions:**
```python
from flask import jsonify
from execution.enroll_lead import LeadEnrollment

def enroll_lead_http(request):
    data = request.get_json()

    enrollment = LeadEnrollment()
    result = enrollment.enroll_lead(**data)

    return jsonify(result)
```

---

## API Reference

### POST /enroll

Enroll a lead into the nurture workflow.

**Request Body:**
```json
{
  "email": "lead@example.com",      // Required if no lead_id
  "lead_id": "lead_xxxxx",          // Required if no email
  "name": "John Doe",               // Optional, fetched from Close.io if not provided
  "call_time": "2025-01-15T14:00:00Z",  // Optional, defaults to 3 days from now
  "call_duration": 30               // Optional, defaults to 30 minutes
}
```

**Response (Success):**
```json
{
  "success": true,
  "lead_id": "lead_xxxxx",
  "email": "lead@example.com",
  "name": "John",
  "call_time": "2025-01-15T14:00:00Z",
  "welcome_email_sent": true,
  "emails_scheduled": ["welcome", "midpoint", "day_before", "hour_before"]
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "No lead found with email lead@example.com"
}
```

---

## Testing the Integration

### 1. Test Command Line
```bash
python execution/enroll_lead.py justin@dobotai.com
```

### 2. Test Webhook Server
```bash
# Terminal 1: Start server
python execution/webhook_server.py 8080

# Terminal 2: Test with curl
curl -X POST http://localhost:8080/enroll \
  -H "Content-Type: application/json" \
  -d '{"email": "justin@dobotai.com"}'
```

### 3. Test from Python
```python
from execution.enroll_lead import LeadEnrollment

enrollment = LeadEnrollment()
result = enrollment.enroll_lead(email="justin@dobotai.com")
print(result)
```

### 4. Check Results
- Check email inbox
- Check Close.io lead timeline
- Check `.tmp/lead_nurture_state.json`
- Check `.tmp/nurture_log.json`

---

## Workflow After Enrollment

Once a lead is enrolled:

1. **Welcome email** sends immediately
2. **State file** tracks the lead
3. **Background orchestrator** sends remaining emails on schedule
4. Run orchestrator to handle scheduled emails:
   ```bash
   python execution/lead_nurture_orchestrator.py --continuous 300
   ```

---

## Recommended Setup

**For instant enrollment + scheduled follow-ups:**

```bash
# Terminal 1: Run webhook server (handles instant enrollment)
python execution/webhook_server.py 8080

# Terminal 2: Run orchestrator (handles scheduled emails)
python execution/lead_nurture_orchestrator.py --continuous 300
```

This setup:
- ✅ Enrolls leads instantly when captured
- ✅ Sends welcome email immediately
- ✅ Sends remaining emails on schedule
- ✅ Handles rescheduling and cancellations

---

## Troubleshooting

**Webhook not receiving calls:**
- Check firewall settings
- Use ngrok for local testing
- Verify webhook URL is accessible

**Lead not enrolling:**
- Check if lead exists in Close.io
- Verify email address is correct
- Check `.tmp/nurture_log.json` for errors

**Welcome email not sending:**
- Check Close.io email configuration
- Verify API key permissions
- Check `.tmp/failed_emails.json`

**Emails not sending on schedule:**
- Make sure orchestrator is running
- Check `.tmp/lead_nurture_state.json`
- Verify email times are in the future

---

## Security Considerations

1. **API Key Security**: Never expose your Close.io API key in webhooks
2. **Webhook Authentication**: Add authentication to your webhook endpoint
3. **Rate Limiting**: Implement rate limiting on webhook endpoint
4. **HTTPS**: Always use HTTPS in production
5. **Validation**: Validate all incoming webhook data

---

## Next Steps

1. Choose your integration method
2. Test with a single lead
3. Deploy webhook server (if using webhooks)
4. Configure your lead capture system to call the endpoint
5. Run the orchestrator for scheduled emails
6. Monitor logs and verify emails are sending

Your lead nurture workflow will now start **instantly** when leads are captured! 🚀
