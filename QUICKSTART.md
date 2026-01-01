# Quick Start - Lead Nurture Workflow

Get up and running in 5 minutes.

## 1. Install Dependencies (1 min)

```bash
pip install -r execution/requirements.txt
```

## 2. Add Your API Keys (2 min)

Edit [.env](.env) and replace these values:

```bash
# Required - Close.io API Key (used for both CRM and email)
CLOSE_IO_API_KEY=your_close_io_api_key

# Test email
TEST_EMAIL=your_email@example.com
```

**Get API Key:**
- Close.io: https://app.close.com/settings/api/

## 3. Test It (2 min)

```bash
cd execution

# Test Close.io connection
python close_io_client.py

# Test email sending
python send_email.py

# Run workflow once (test mode)
python lead_nurture_orchestrator.py
```

## 4. Run It

### For Testing
```bash
python execution/lead_nurture_orchestrator.py
```

### For Production (runs continuously)
```bash
python execution/lead_nurture_orchestrator.py --continuous 300
```

This checks every 5 minutes (300 seconds) for new bookings and sends emails.

## What Happens Now?

1. **System monitors Close.io** for leads with booked calls
2. **When a call is booked**, lead enters nurture sequence
3. **Emails sent automatically**:
   - Welcome (within 5 min)
   - Mid-point (if >48hrs away)
   - Day before (24hrs before)
   - Hour before (1hr before)
4. **Activity logged** to Close.io and `.tmp/nurture_log.json`

## Files Created

- `.tmp/lead_nurture_state.json` - Tracks leads in nurture
- `.tmp/nurture_log.json` - Activity log
- `.tmp/failed_emails.json` - Failed email attempts

## Customize

Edit email templates in [execution/email_templates.py](execution/email_templates.py)

## Need Help?

See [SETUP.md](SETUP.md) for detailed documentation.

## Production Checklist

- [ ] API keys added to `.env`
- [ ] Test emails received successfully
- [ ] Email templates customized for your brand
- [ ] Tested with one real lead from Close.io
- [ ] Running in continuous mode
- [ ] Monitoring logs for errors

Done! Your lead nurture workflow is live.
