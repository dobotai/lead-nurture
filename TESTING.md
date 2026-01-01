# End-to-End Testing Guide

This guide will walk you through testing the complete lead nurture workflow from start to finish.

## Quick Test (5 minutes)

### Option 1: Fast Test with Near-Future Call

This tests the entire workflow quickly by creating a call scheduled soon.

**1. Create a Test Lead in Close.io**

Go to Close.io and create a test lead:
- Name: "Test Lead"
- Email: Your email (e.g., doby@dobotai.com)
- Company: "Test Company"

**2. Schedule a Call 2 Hours from Now**

In Close.io:
- Go to the test lead
- Click "Add Activity" → "Meeting/Call"
- Schedule it for **2 hours from now**
- Save the call

**3. Run the Workflow Once**

```bash
python execution/lead_nurture_orchestrator.py
```

**4. Check What Happens**

The system should:
- ✅ Find the test lead with the upcoming call
- ✅ Add lead to nurture sequence
- ✅ Send the **Welcome email** immediately (within 5 minutes)
- ✅ Schedule **Hour-before email** for 1 hour before the call
- ✅ Skip mid-point and day-before (call is too soon)

**5. Verify the Welcome Email**

Check:
- Your inbox for the welcome email
- Close.io → Lead activity timeline (email should appear there)
- Close.io → Sent folder (email should be there)
- `.tmp/lead_nurture_state.json` (lead should be tracked)
- `.tmp/nurture_log.json` (activity should be logged)

**6. Wait and Check Hour-Before Email**

Run the workflow again 1 hour before the call:
```bash
python execution/lead_nurture_orchestrator.py
```

The **Hour-before email** should send.

---

## Complete Test (24+ hours)

### Option 2: Full Test with Call 3+ Days Away

This tests the complete email sequence.

**1. Create Test Lead in Close.io**

- Name: "Full Test Lead"
- Email: Your email
- Company: "Full Test Company"

**2. Schedule a Call 3 Days from Now**

- Go to the lead
- Add Meeting/Call activity
- Schedule for **3 days from now, at 2:00 PM**
- Save

**3. Run the Workflow**

```bash
python execution/lead_nurture_orchestrator.py --continuous 300
```

This runs every 5 minutes (300 seconds).

**4. Monitor the Email Sequence**

Over the next 3 days, you should receive:

| Time | Email | What to Check |
|------|-------|---------------|
| Within 5 min | **Welcome Email** | Check inbox, Close.io activity, state file |
| ~36 hours later | **Mid-point Email** | Halfway between booking and call |
| 24 hours before | **Day-before Email** | Includes meeting link, preparation checklist |
| 1 hour before | **Hour-before Email** | Final reminder with meeting link |

**5. Verify Each Email**

For each email received:
- ✅ Check your inbox
- ✅ Check Close.io lead timeline
- ✅ Check Close.io Sent folder
- ✅ Check `.tmp/nurture_log.json` for logged activity
- ✅ Check `.tmp/lead_nurture_state.json` - email should be in `sent_emails` array

---

## Testing Edge Cases

### Test 1: Call Rescheduled

**Scenario:** Lead reschedules their call

**Steps:**
1. Create test lead with call 3 days away
2. Run workflow → Welcome email sends
3. In Close.io, reschedule the call to 5 days away
4. Run workflow again
5. Check `.tmp/lead_nurture_state.json` - call time should update
6. Email schedule should recalculate (mid-point changes)
7. Should NOT send duplicate welcome email

**Expected:** Email timing adjusts, no duplicates sent

---

### Test 2: Call Cancelled

**Scenario:** Lead cancels their call

**Steps:**
1. Create test lead with upcoming call
2. Run workflow → Welcome email sends
3. In Close.io, cancel/delete the call
4. Run workflow again
5. Check `.tmp/lead_nurture_state.json` - lead should be removed
6. No more emails should send

**Expected:** Lead removed from nurture sequence

---

### Test 3: Multiple Leads

**Scenario:** Multiple leads with different call times

**Steps:**
1. Create 3 test leads:
   - Lead A: Call in 1 hour
   - Lead B: Call in 2 days
   - Lead C: Call in 5 days
2. Run workflow
3. Check that each gets appropriate emails:
   - Lead A: Only welcome + hour-before
   - Lead B: Welcome + day-before + hour-before
   - Lead C: Welcome + midpoint + day-before + hour-before

**Expected:** Each lead gets correct email sequence based on call timing

---

### Test 4: Email Send Failure Recovery

**Scenario:** Simulate email failure and retry

**Steps:**
1. Temporarily break something (e.g., invalid lead_id)
2. Run workflow
3. Check `.tmp/failed_emails.json` - failed email should be logged
4. Fix the issue
5. Run retry:
```python
from execution.send_email import EmailSender
sender = EmailSender()
results = sender.retry_failed_emails()
print(results)
```

**Expected:** Failed emails are logged and can be retried

---

### Test 5: Lead Without Email

**Scenario:** Lead in Close.io has no email address

**Steps:**
1. Create lead in Close.io without an email contact
2. Schedule a call for this lead
3. Run workflow
4. Check logs

**Expected:** System skips this lead with message "No email found for lead {id}"

---

## Monitoring & Debugging

### Check Current State

```bash
# View current leads in nurture
cat .tmp/lead_nurture_state.json

# View recent activity
cat .tmp/nurture_log.json

# View failed emails
cat .tmp/failed_emails.json
```

### Manual Test Individual Components

**Test Close.io Connection:**
```bash
cd execution
python close_io_client.py
```

**Test Email Sending:**
```bash
python send_email.py
```

**Test Email Templates:**
```bash
python email_templates.py
```

**Run Full System Test:**
```bash
cd ..
python test_system.py
```

---

## Production Readiness Checklist

Before going to production, verify:

### Configuration
- [ ] Close.io API key is correct in `.env`
- [ ] Test email successfully received
- [ ] Email templates customized for your brand
- [ ] Company name updated in templates

### Functionality
- [ ] Welcome email sends within 5 minutes
- [ ] Mid-point email calculates correctly
- [ ] Day-before email sends at right time
- [ ] Hour-before email sends at right time
- [ ] Emails appear in Close.io timeline
- [ ] Emails appear in Close.io Sent folder
- [ ] State file tracks leads correctly
- [ ] Activity log records all actions

### Edge Cases
- [ ] Rescheduled calls update timing
- [ ] Cancelled calls remove from sequence
- [ ] No duplicate emails sent
- [ ] Leads without emails are skipped
- [ ] Failed emails are logged and retryable

### Performance
- [ ] System runs without errors for 24+ hours
- [ ] Rate limiting prevents API throttling
- [ ] Memory usage stays stable
- [ ] Log files don't grow too large

---

## Recommended Testing Sequence

**Day 1: Quick Test**
1. Create test lead with call in 2 hours
2. Run workflow once
3. Verify welcome email received
4. Verify email in Close.io
5. Wait for hour-before email

**Day 2-4: Full Test**
1. Create test lead with call in 3 days
2. Run workflow continuously
3. Monitor all 4 emails over 3 days
4. Verify timing is correct
5. Check Close.io integration

**Day 5: Edge Cases**
1. Test call rescheduling
2. Test call cancellation
3. Test multiple leads
4. Test email failure recovery

**Day 6: Production Deploy**
1. Customize email templates
2. Set up monitoring
3. Deploy to production
4. Monitor first few real leads carefully

---

## Troubleshooting

### Problem: Welcome email not sending

**Check:**
- Is lead in `.tmp/lead_nurture_state.json`?
- Run workflow with `python execution/lead_nurture_orchestrator.py` to see output
- Check `.tmp/failed_emails.json` for errors
- Verify lead has email in Close.io

### Problem: Wrong email timing

**Check:**
- Call time in Close.io vs `.tmp/lead_nurture_state.json`
- Email schedule in state file
- System time/timezone settings

### Problem: Emails not appearing in Close.io

**Check:**
- lead_id is being passed to email sender
- Email sender using correct sender account
- Close.io activity timeline filters

### Problem: Duplicate emails

**Check:**
- `.tmp/lead_nurture_state.json` - is lead tracked?
- sent_emails array - are emails marked as sent?
- Did you delete state file? (Don't do this in production)

---

## Quick Commands Reference

```bash
# Run workflow once (test mode)
python execution/lead_nurture_orchestrator.py

# Run continuously (production mode)
python execution/lead_nurture_orchestrator.py --continuous 300

# Check current state
cat .tmp/lead_nurture_state.json

# Check activity log
cat .tmp/nurture_log.json

# Test email sending
cd execution && python send_email.py

# Test Close.io connection
cd execution && python close_io_client.py

# Run full system test
python test_system.py

# Monitor logs in real-time (if running continuously)
tail -f .tmp/nurture_log.json
```

---

## What Success Looks Like

✅ **Emails send at the right times**
✅ **All emails appear in Close.io**
✅ **No duplicate emails**
✅ **Rescheduling works correctly**
✅ **Cancellations stop the sequence**
✅ **System runs reliably for days**
✅ **Logs show all activity**
✅ **No errors in production**

Once all tests pass, you're ready for production! 🚀
