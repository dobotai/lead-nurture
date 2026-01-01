# Lead Nurture Workflow - Setup Guide

This guide will help you set up and run the lead nurture workflow that automatically sends emails to leads who book calls in Close.io.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r execution/requirements.txt
```

### 2. Configure API Keys

Edit [.env](.env) and add your credentials:

```bash
# Close.io API Key (used for both CRM access and sending emails)
# Get from: https://app.close.com/settings/api/
CLOSE_IO_API_KEY=your_actual_api_key_here

# Test email for testing the system
TEST_EMAIL=your_email@example.com
```

### 3. Test the Setup

#### Test Close.io Connection
```bash
cd execution
python close_io_client.py
```

This should display leads with upcoming calls from your Close.io account.

#### Test Email Sending
```bash
python send_email.py
```

This will send a test email to the address specified in `TEST_EMAIL`.

#### Test Email Templates
```bash
python email_templates.py
```

This shows previews of all email templates.

### 4. Run the Workflow

#### One-time run (for testing)
```bash
python lead_nurture_orchestrator.py
```

This will:
- Check Close.io for leads with upcoming calls
- Enroll new leads in the nurture sequence
- Send any emails that are due
- Exit

#### Continuous monitoring (production)
```bash
python lead_nurture_orchestrator.py --continuous 300
```

This runs continuously and checks every 300 seconds (5 minutes).

## How It Works

### Email Sequence

When a lead books a call, they receive:

1. **Welcome Email** - Within 5 minutes of booking
   - Confirms call details
   - Sets expectations
   - Provides preparation tips

2. **Mid-point Email** - Halfway to the call (if >48 hours away)
   - Keeps engagement warm
   - Shares relevant resources
   - Addresses common questions

3. **Day-before Reminder** - 24 hours before the call
   - Confirms availability
   - Preparation checklist
   - Meeting link

4. **Hour-before Reminder** - 1 hour before the call
   - Quick reminder
   - Meeting link
   - "See you soon" message

### State Management

The system maintains state in `.tmp/lead_nurture_state.json`:
- Tracks which leads are in the nurture sequence
- Records which emails have been sent
- Handles call rescheduling
- Removes leads after calls complete

### Activity Logging

All activity is logged to `.tmp/nurture_log.json`:
- Emails sent
- Calls rescheduled
- Errors encountered
- Leads added/removed

## Email Service

This system uses **Close.io's Email API** to send all nurture emails.

**Benefits:**
- No additional email service needed
- Emails are automatically tracked in Close.io
- Emails appear in the lead's activity timeline
- Uses your existing Close.io email configuration
- No extra setup or costs

**Important Notes:**
- Make sure your Close.io account has email sending configured
- Emails will be sent from the email address configured in your Close.io account
- All sent emails appear in Close.io's Sent folder
- Email tracking and threading work automatically

## Production Deployment

### Option 1: Run as Background Process

**Linux/Mac:**
```bash
nohup python execution/lead_nurture_orchestrator.py --continuous 300 > nurture.log 2>&1 &
```

**Windows:**
```bash
start /B python execution\lead_nurture_orchestrator.py --continuous 300
```

### Option 2: Run as System Service

Create a systemd service (Linux) or Windows Service to ensure it runs on startup and restarts on failure.

### Option 3: Run on a Server/VPS

Deploy to a cloud server (AWS EC2, DigitalOcean, etc.) and run continuously.

### Option 4: Use Task Scheduler/Cron

Run every 5 minutes via cron (Linux) or Task Scheduler (Windows):

**Cron:**
```bash
*/5 * * * * cd /path/to/Lead\ Nurture && python execution/lead_nurture_orchestrator.py
```

**Windows Task Scheduler:**
- Create task that runs `lead_nurture_orchestrator.py`
- Set to run every 5 minutes
- Run whether user is logged in or not

## Monitoring

### Check State
```bash
cat .tmp/lead_nurture_state.json
```

Shows current leads in nurture and their status.

### Check Logs
```bash
cat .tmp/nurture_log.json
```

Shows all activity.

### Check Failed Emails
```bash
cat .tmp/failed_emails.json
```

Shows emails that failed to send.

### Retry Failed Emails
```python
from send_email import EmailSender
sender = EmailSender()
results = sender.retry_failed_emails()
print(f"Success: {results['success']}, Failed: {results['failed']}")
```

## Customization

### Edit Email Templates

Edit [execution/email_templates.py](execution/email_templates.py) to customize:
- Email content
- Subject lines
- HTML styling
- Personalization

### Adjust Timing

Edit `_calculate_email_times()` in [execution/lead_nurture_orchestrator.py](execution/lead_nurture_orchestrator.py) to change when emails are sent.

### Add More Emails

1. Create new template method in `email_templates.py`
2. Add to email schedule in `_calculate_email_times()`
3. Add send logic in `_send_nurture_email()`

## Troubleshooting

### "Close.io API error: 401"
- Check your `CLOSE_IO_API_KEY` in `.env`
- Verify the key is active in Close.io settings

### "No email service configured"
- Add either `SENDGRID_API_KEY` or SMTP credentials to `.env`
- Make sure `FROM_EMAIL` is set

### "No email found for lead"
- Lead in Close.io doesn't have an email address
- Add email to the lead's contact info

### Emails not sending
- Check `.tmp/failed_emails.json` for errors
- Verify email service credentials
- Check spam folder
- Review `.tmp/nurture_log.json` for details

### Duplicate emails
- State file prevents duplicates
- If you delete `.tmp/lead_nurture_state.json`, leads will re-enter sequence
- Don't delete state file in production

## Best Practices

1. **Test thoroughly** before going to production
2. **Monitor logs** regularly for the first few days
3. **Start with one test lead** before enabling for all
4. **Customize templates** to match your brand voice
5. **Check deliverability** - make sure emails aren't going to spam
6. **Backup state file** periodically if running in production
7. **Set up monitoring alerts** for errors

## Next Steps

- Add meeting links from Close.io calendar integrations
- Track email open rates (if using service that supports it)
- A/B test email templates
- Add SMS reminders
- Integrate with Slack for notifications
- Create dashboard for campaign metrics

## Support

For issues or questions:
1. Check the logs in `.tmp/`
2. Review the directive: [directives/lead_nurture_workflow.md](directives/lead_nurture_workflow.md)
3. Test individual components (close_io_client.py, send_email.py)

## File Reference

- **Directive**: [directives/lead_nurture_workflow.md](directives/lead_nurture_workflow.md)
- **Close.io Client**: [execution/close_io_client.py](execution/close_io_client.py)
- **Email Sender**: [execution/send_email.py](execution/send_email.py)
- **Templates**: [execution/email_templates.py](execution/email_templates.py)
- **Orchestrator**: [execution/lead_nurture_orchestrator.py](execution/lead_nurture_orchestrator.py)
- **Config**: [.env](.env)
