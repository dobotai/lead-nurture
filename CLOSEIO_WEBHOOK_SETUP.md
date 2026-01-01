# Close.io Webhook Integration Setup

Connect your lead capture automation to the lead nurture workflow using Close.io webhooks.

## How It Works

```
Calendly booking
    ↓
Your automation creates lead in Close.io
    ↓
Close.io fires webhook → Your Railway app
    ↓
Lead Nurture enrolls lead → Sends welcome email
    ↓
Scheduled emails send automatically
```

## Setup (5 minutes)

### Step 1: Get Your Railway Webhook URL

Your Railway app URL is: `https://YOUR-APP.up.railway.app`

The Close.io webhook endpoint is: `/closeio-webhook`

**Full webhook URL:**
```
https://YOUR-APP.up.railway.app/closeio-webhook
```

### Step 2: Configure Close.io Webhook

1. **Go to Close.io** → Settings → Webhooks
   - URL: https://app.close.com/settings/webhooks

2. **Click "Add Webhook"**

3. **Configure:**
   - **URL**: `https://YOUR-APP.up.railway.app/closeio-webhook`
   - **Events**: Select **"lead.created"**
   - **Status**: Enable (toggle on)

4. **Click "Save"**

### Step 3: Test It

**Create a test lead in Close.io:**

1. Go to Close.io → Leads
2. Click "Add Lead"
3. Fill in:
   - Name: "Test Lead"
   - Email: your email address
4. Add a scheduled call/meeting
5. Save

**What should happen:**
- ✅ Close.io fires webhook to your Railway app
- ✅ Railway logs show: "New lead created in Close.io: lead_xxxxx"
- ✅ Welcome email sends immediately
- ✅ Email appears in Close.io timeline
- ✅ Remaining emails scheduled

### Step 4: Verify

**Check Railway Logs:**
1. Go to Railway dashboard
2. Click on web service
3. Go to "Logs" tab
4. Look for:
   ```
   New lead created in Close.io: lead_xxxxx
   Lead enrolled: test@example.com
   ```

**Check Email:**
- Welcome email in inbox
- Email in Close.io Sent folder
- Email in lead's activity timeline

## How Your Existing Automation Works With This

### Current Flow:
```
Calendly booking → Your automation → Creates lead in Close.io
```

### Updated Flow:
```
Calendly booking → Your automation → Creates lead in Close.io
                                             ↓ (webhook fires automatically)
                                    Railway app enrolls lead
                                             ↓
                                    Welcome email sends
```

**No changes needed** to your existing automation! Just add the webhook in Close.io and it works automatically.

## Alternative Integration Methods

If you prefer more control, you can also:

### Option A: Call Railway Directly from Your Automation

Add this step to your existing automation (after creating lead in Close.io):

```javascript
// After creating lead in Close.io
const response = await fetch('https://YOUR-APP.up.railway.app/enroll', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: calendly.email,
    name: calendly.name,
    call_time: calendly.scheduled_time
  })
});
```

### Option B: Add Step in Zapier/Make

If using Zapier or Make:

**Current:**
```
Calendly → Create lead in Close.io
```

**Updated:**
```
Calendly → Create lead in Close.io → HTTP Request to Railway
```

**HTTP Request config:**
- URL: `https://YOUR-APP.up.railway.app/enroll`
- Method: POST
- Body:
  ```json
  {
    "email": "{{calendly.email}}",
    "name": "{{calendly.name}}",
    "call_time": "{{calendly.scheduled_time}}"
  }
  ```

## Webhook Payload Reference

### What Close.io Sends

```json
{
  "event": "lead.created",
  "data": {
    "id": "lead_xxxxx",
    "name": "Lead Name",
    "contacts": [
      {
        "name": "Contact Name",
        "emails": [{"email": "lead@example.com"}]
      }
    ]
  }
}
```

### What Railway Returns

**Success:**
```json
{
  "success": true,
  "lead_id": "lead_xxxxx",
  "email": "lead@example.com",
  "name": "Lead",
  "call_time": "2025-01-15T14:00:00Z",
  "welcome_email_sent": true,
  "emails_scheduled": ["welcome", "midpoint", "day_before", "hour_before"]
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

## Monitoring

### Check Webhook Activity

**Railway Logs:**
```bash
# In Railway dashboard → Logs tab
# Look for:
"New lead created in Close.io: lead_xxxxx"
"Lead enrolled: email@example.com"
```

**Close.io Webhook Logs:**
1. Go to Close.io → Settings → Webhooks
2. Click on your webhook
3. View "Recent Deliveries"
4. Check status codes (200 = success)

### Common Issues

**Webhook not firing:**
- Check webhook is enabled in Close.io
- Verify URL is correct
- Check "Recent Deliveries" in Close.io webhook settings

**Lead not enrolling:**
- Check Railway logs for errors
- Verify lead has email address
- Check `.tmp/nurture_log.json` for activity

**No welcome email:**
- Verify Close.io email account configured
- Check Railway worker service is running
- Check `.tmp/failed_emails.json`

## Testing Checklist

- [ ] Webhook added in Close.io
- [ ] Webhook URL correct
- [ ] "lead.created" event selected
- [ ] Webhook enabled (toggled on)
- [ ] Test lead created
- [ ] Webhook fired (check Close.io logs)
- [ ] Lead enrolled (check Railway logs)
- [ ] Welcome email received
- [ ] Email in Close.io timeline

## Recommended Setup

**Best approach for your use case:**

1. ✅ **Use Close.io webhook** (automatic, no changes to existing automation)
2. Keep your Calendly → Close.io automation as-is
3. Close.io webhook triggers nurture automatically
4. Monitor Railway logs to verify

This is the cleanest integration - your existing automation doesn't need any changes!

## Next Steps

1. Add webhook in Close.io (Settings → Webhooks)
2. Test with one lead
3. Verify email sends
4. Monitor for 24 hours
5. You're done!

Your lead capture and lead nurture automations are now fully integrated! 🚀
