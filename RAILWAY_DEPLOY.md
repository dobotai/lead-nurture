# Railway Deployment Guide

Deploy your lead nurture system to Railway for 24/7 operation with persistent storage.

## Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app)
- Close.io API key

## Quick Deploy (5 minutes)

### Step 1: Prepare Your Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Lead Nurture System"

# Create GitHub repository and push
# (Follow GitHub's instructions to create a new repo)
git remote add origin https://github.com/YOUR_USERNAME/lead-nurture.git
git branch -M main
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your `lead-nurture` repository

### Step 3: Configure Two Services

Railway will detect your `Procfile` and create services automatically. You need **two services**:

#### Service 1: Webhook Server (web)

1. In Railway dashboard, go to your project
2. Click **"+ New Service"**
3. Select **"GitHub Repo"** → Choose your repo
4. Railway will auto-detect the `Procfile`
5. Ensure it's running the **`web`** process

#### Service 2: Orchestrator (worker)

1. Click **"+ New Service"** again
2. Select **"GitHub Repo"** → Same repo
3. Go to **Settings** → **Deploy**
4. Change **"Start Command"** to:
   ```
   python execution/lead_nurture_orchestrator.py --continuous 300
   ```

### Step 4: Add Environment Variables

For **BOTH** services:

1. Click on the service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   ```
   CLOSE_IO_API_KEY=api_5eU3vaRHw57yk2P8IqpUOh.2kEZUzxL9ArkSrnd3mfkmw
   ```

Railway automatically provides `PORT` for the web service.

### Step 5: Configure Persistent Volume

To keep lead state across restarts:

#### For Both Services:

1. Click on the service
2. Go to **"Settings"** tab
3. Scroll to **"Volumes"**
4. Click **"+ New Volume"**
5. Set:
   - **Mount Path**: `/app/.tmp`
   - **Size**: 1 GB (minimum)
6. Click **"Add"**

This ensures `.tmp/lead_nurture_state.json` and logs persist across deploys.

### Step 6: Deploy!

Railway auto-deploys when you push to GitHub. Initial deployment happens immediately.

**Monitor deployment:**
1. Go to **"Deployments"** tab
2. Watch the build logs
3. Wait for "Success" status

### Step 7: Get Your Webhook URL

1. Click on your **web service**
2. Go to **"Settings"** tab
3. Click **"Generate Domain"**
4. Copy your public URL (e.g., `https://your-app.up.railway.app`)

**Your webhook endpoint is:**
```
https://your-app.up.railway.app/enroll
```

## Verify Deployment

### Test Health Check

```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{"status": "ok", "service": "lead-nurture-webhook"}
```

### Test Lead Enrollment

```bash
curl -X POST https://your-app.up.railway.app/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test Lead",
    "call_time": "2025-01-15T14:00:00Z"
  }'
```

### Check Logs

In Railway dashboard:
1. Click on a service
2. Go to **"Logs"** tab
3. Watch real-time logs

**What to look for:**
- Webhook server: "Lead Nurture Webhook Server running on port XXXX"
- Orchestrator: "Running nurture workflow at..."
- Email sends: "Email sent successfully to..."

## Architecture on Railway

```
GitHub Repo
    ↓
Railway Project
    ├── Web Service (Port: auto-assigned)
    │   ├── Runs: webhook_server.py
    │   ├── Handles: Instant lead enrollment
    │   ├── Volume: /app/.tmp (1GB)
    │   └── Public URL: https://your-app.up.railway.app
    │
    └── Worker Service (Background)
        ├── Runs: lead_nurture_orchestrator.py --continuous 300
        ├── Handles: Scheduled email delivery
        ├── Volume: /app/.tmp (1GB)
        └── Checks every 5 minutes
```

## Webhook Integration

Now that your system is live, integrate with your lead capture:

### Option 1: Calendly Webhook

1. Go to Calendly → Account → Webhooks
2. Add webhook URL: `https://your-app.up.railway.app/enroll`
3. Subscribe to: "invitee.created"

### Option 2: Direct API Call

From your lead capture system:
```python
import requests

response = requests.post(
    'https://your-app.up.railway.app/enroll',
    json={
        'email': 'newlead@example.com',
        'name': 'New Lead',
        'call_time': '2025-01-15T14:00:00Z'
    }
)
print(response.json())
```

### Option 3: Zapier

1. Trigger: (Your booking tool)
2. Action: Webhooks by Zapier → Custom Request
3. URL: `https://your-app.up.railway.app/enroll`
4. Method: POST
5. Data: JSON with email, name, call_time

## Monitoring

### View Service Health

**Railway Dashboard:**
- CPU usage
- Memory usage
- Deployment status
- Error logs

**Key Metrics to Watch:**
- Webhook requests per minute
- Email send success rate
- Orchestrator uptime
- Volume storage usage

### Check Lead State

SSH into Railway (optional):
```bash
railway login
railway link
railway run bash
cat .tmp/lead_nurture_state.json
```

Or check logs for state information.

## Updating Your Deployment

### Make Changes Locally

```bash
# Edit files
# Test locally
python execution/webhook_server.py 8080
python execution/lead_nurture_orchestrator.py
```

### Deploy Updates

```bash
git add .
git commit -m "Update: description of changes"
git push
```

Railway auto-deploys on push to main branch.

### Rollback if Needed

In Railway dashboard:
1. Go to **"Deployments"**
2. Click on a previous successful deployment
3. Click **"Redeploy"**

## Troubleshooting

### Webhook Server Not Responding

**Check:**
1. Service is running (Railway dashboard)
2. Domain is generated (Settings → Networking)
3. PORT env var is set (auto-provided by Railway)
4. Logs show "server running on port..."

**Fix:**
- Restart service in Railway dashboard
- Check logs for errors
- Verify Procfile syntax

### Orchestrator Not Sending Emails

**Check:**
1. Worker service is running
2. CLOSE_IO_API_KEY is set correctly
3. Logs show "Running nurture workflow"
4. Check `.tmp/failed_emails.json` in volume

**Fix:**
- Verify Close.io API key
- Check Close.io email account configuration
- Review orchestrator logs
- Ensure volume is mounted

### State Not Persisting

**Check:**
1. Volume is created (Settings → Volumes)
2. Mount path is `/app/.tmp`
3. Volume size is adequate (1GB+)

**Fix:**
- Re-create volume
- Verify mount path
- Check volume usage in dashboard

### Out of Memory

**Symptoms:**
- Service crashes
- "Out of memory" in logs

**Fix:**
- Upgrade Railway plan (if needed)
- Check for memory leaks in logs
- Optimize state file size

### Rate Limiting from Close.io

**Symptoms:**
- "Rate limit exceeded" in logs
- Emails not sending

**Fix:**
- Increase orchestrator interval (from 300s to 600s)
- Check rate limiting in `close_io_client.py`
- Verify you're not hitting Close.io limits

## Costs

**Railway Pricing:**
- **Free Tier**: $5 credit/month (500 hours)
- **Hobby Plan**: $5/month (more resources)
- **Pro Plan**: $20/month (production)

**Estimated Usage:**
- 2 services running 24/7
- ~1400 hours/month total
- **Fits in Hobby plan** (~$5-10/month)

**Free tier is fine for:**
- Testing and development
- Low-volume production (<100 leads/month)

## Security Best Practices

1. **Never commit .env** - Already in .gitignore ✓
2. **Use Railway secrets** - For CLOSE_IO_API_KEY
3. **Enable HTTPS** - Railway provides automatically ✓
4. **Add webhook authentication** (optional):
   ```python
   # Add to webhook_server.py
   if request.headers.get('X-Auth-Token') != os.getenv('WEBHOOK_SECRET'):
       return 401
   ```

## Performance Optimization

### Reduce Orchestrator Frequency

If you don't need instant scheduling:
```bash
# Change from 300 (5 min) to 600 (10 min)
python execution/lead_nurture_orchestrator.py --continuous 600
```

### Enable Railway Metrics

Railway Pro plan includes:
- Custom metrics
- Performance insights
- Advanced monitoring

## Backup and Recovery

### Backup State File

Periodically download state:
```bash
railway run cat .tmp/lead_nurture_state.json > backup.json
```

### Restore from Backup

```bash
railway run bash
cat > .tmp/lead_nurture_state.json << 'EOF'
{paste backup here}
EOF
```

## Support

**Railway Support:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Help: help@railway.app

**Lead Nurture System:**
- Check logs in Railway dashboard
- Review [TESTING.md](TESTING.md)
- Check [INTEGRATION.md](INTEGRATION.md)

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Test webhook endpoint
3. ✅ Integrate with lead capture
4. ✅ Monitor logs for 24 hours
5. ✅ Customize email templates
6. ✅ Set up monitoring alerts (Railway Pro)

Your lead nurture system is now running 24/7 on Railway! 🚀

## Quick Reference

**Webhook URL:**
```
https://your-app.up.railway.app/enroll
```

**Health Check:**
```
https://your-app.up.railway.app/health
```

**Deploy Command:**
```bash
git push
```

**View Logs:**
```bash
railway logs
```

**SSH into Service:**
```bash
railway run bash
```
