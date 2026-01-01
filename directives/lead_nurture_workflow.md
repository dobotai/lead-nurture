# Lead Nurture Workflow - Close.io Integration

## Goal
Automatically nurture leads who have booked a call by sending a series of emails from the time they book until their scheduled call date. This keeps leads engaged and reduces no-shows.

## Inputs
- **Close.io API Key**: Authentication for Close.io CRM
- **Email Service Credentials**: For sending emails (Gmail, SendGrid, or SMTP)
- **Lead Filter**: Criteria to identify leads who have booked calls
- **Email Templates**: Pre-written email content for different stages
- **Timing Rules**: When to send each email (e.g., immediately after booking, 1 day before call, 1 hour before call)

## Tools/Scripts

### Core Scripts
- `execution/close_io_client.py`: Close.io API integration
  - Fetch leads with booked calls
  - Get lead details (name, email, call time)
  - Update lead status/notes
  - Check for call status changes

- `execution/send_email.py`: Email sending functionality
  - Send individual emails
  - Support for HTML templates
  - Track email sent status
  - Handle email failures

- `execution/lead_nurture_orchestrator.py`: Main workflow orchestrator
  - Monitor Close.io for new booked calls
  - Calculate email send times based on call date
  - Queue emails at appropriate times
  - Track which emails have been sent to each lead
  - Handle edge cases (call rescheduled, cancelled)

- `execution/email_templates.py`: Email template management
  - Store email templates
  - Personalize with lead data
  - Different templates for different stages

## Workflow Logic

### Email Sequence
1. **Immediate**: Welcome email after booking (within 5 minutes)
   - Thank them for booking
   - Confirm call details (date, time, duration)
   - What to prepare for the call
   - Add to calendar link

2. **Mid-Point**: Follow-up email (sent at 50% mark between booking and call)
   - Reminder about the upcoming call
   - Share relevant resources/case studies
   - Address common questions

3. **Day Before**: Pre-call reminder (24 hours before)
   - Confirm they're still available
   - Final preparation checklist
   - Zoom/meeting link

4. **Hour Before**: Last reminder (1 hour before)
   - Quick reminder with meeting link
   - "See you soon" message

### State Tracking
Use `.tmp/lead_nurture_state.json` to track:
- Which leads are in the nurture sequence
- Which emails have been sent to each lead
- When each email was sent
- Call booking date and time
- Next scheduled email

## Outputs

### Deliverables
- Emails sent to leads at appropriate times
- Close.io lead notes updated with email activity
- Log file in `.tmp/nurture_log.json` with all activities

### Intermediates (in `.tmp/`)
- `lead_nurture_state.json`: Current state of all leads in nurture
- `nurture_log.json`: Activity log
- `failed_emails.json`: Emails that failed to send

## Edge Cases

### Call Rescheduled
- **Detection**: Check Close.io for call time changes
- **Action**: Recalculate email timing, don't send duplicate welcome email, adjust remaining emails

### Call Cancelled
- **Detection**: Call status changed to cancelled in Close.io
- **Action**: Remove from nurture sequence, optionally send cancellation follow-up

### Lead Already Contacted
- **Detection**: Check Close.io notes for previous email activity
- **Action**: Don't restart sequence, continue from where left off

### Email Send Failure
- **Detection**: Email service returns error
- **Action**: Log to `failed_emails.json`, retry up to 3 times with exponential backoff

### Call Time Too Soon
- **Detection**: Call booked less than 24 hours away
- **Action**: Skip mid-point email, adjust sequence (welcome → day before → hour before)

### Call Time Very Soon
- **Detection**: Call booked less than 2 hours away
- **Action**: Send only welcome email with call details

### Multiple Calls Booked
- **Detection**: Lead has multiple calls scheduled
- **Action**: Nurture for the earliest upcoming call only

## Scheduling/Execution

### Option 1: Continuous Monitor (Recommended for immediate response)
Run `lead_nurture_orchestrator.py` as a background process that:
- Checks Close.io every 5 minutes for new bookings
- Checks state every minute for emails that need to be sent
- Sends emails when timing threshold is reached

### Option 2: Cron/Scheduled Task
Run `lead_nurture_orchestrator.py` on a schedule (e.g., every 5 minutes):
- Check for new bookings
- Check for emails to send
- Update state and exit

### Option 3: Webhook (if Close.io supports webhooks)
Set up webhook endpoint that triggers when call is booked:
- Immediate response to bookings
- More efficient than polling
- See `directives/add_webhook.md` for setup

## Close.io API Notes

### Required API Calls
- **List Leads**: `GET /lead/` with filters for leads with booked calls
- **Get Lead Details**: `GET /lead/{lead_id}/`
- **Get Activities**: `GET /activity/` to find call activities
- **Update Lead**: `POST /activity/note/` to log email activity

### Rate Limits
- Close.io: 600 requests per minute
- Implement rate limiting in `close_io_client.py`
- Cache lead data to minimize API calls

### Authentication
- API Key in headers: `Authorization: Basic {api_key}`

## Email Service Notes

### Close.io Email API (Implemented)
The system uses Close.io's native Email API to send all nurture emails.

**Benefits:**
- No additional email service needed
- Emails automatically tracked in Close.io
- Emails appear in lead's activity timeline
- Email threading works automatically
- No extra costs or setup

**API Endpoint:**
- **Send Email**: `POST /activity/email/` with lead_id, to, subject, body_html
- Emails are associated with the lead when lead_id is provided
- Status 'outbox' sends immediately

**Important:**
- Make sure your Close.io account has email sending configured
- Emails will be sent from your Close.io email address
- All sent emails appear in Close.io's Sent folder

## Testing Strategy

1. **Test with test lead**: Create a test lead in Close.io with a call booked 1 hour from now
2. **Verify email sequence**: Check all 4 emails are queued correctly
3. **Test rescheduling**: Change call time, verify emails adjust
4. **Test cancellation**: Cancel call, verify sequence stops
5. **Test failure recovery**: Simulate email failure, verify retry logic

## Initial Setup Checklist

- [ ] Close.io API key added to `.env`
- [ ] Close.io email sending configured in your account
- [ ] Email templates customized for your brand
- [ ] Test lead created in Close.io
- [ ] Scripts tested with test lead
- [ ] Monitoring/scheduling method chosen
- [ ] Error notifications configured (Slack webhook - optional)

## Improvements for Later

- A/B test different email templates
- Track email open rates (if using service that supports it)
- Personalize email content based on lead source/industry
- Add SMS reminders as backup
- Create dashboard to view nurture campaign performance
- Integrate with calendar to avoid sending emails outside business hours
