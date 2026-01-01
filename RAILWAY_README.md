# Railway Deployment - Ready to Deploy! 🚀

Your lead nurture system is **ready for Railway deployment**. All configuration files are in place.

## What's Been Set Up

✅ **Railway Configuration**
- [Procfile](Procfile) - Defines web + worker services
- [railway.json](railway.json) - Railway build settings
- [runtime.txt](runtime.txt) - Python 3.11
- [.gitignore](.gitignore) - Excludes sensitive files

✅ **Code Updates**
- [execution/webhook_server.py](execution/webhook_server.py) - Reads Railway's PORT env var
- All scripts tested and working locally

✅ **Documentation**
- [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) - Complete deployment guide
- [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) - Step-by-step checklist
- [INTEGRATION.md](INTEGRATION.md) - Webhook integration guide

## Quick Deploy (15 minutes)

Follow the [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) - it has everything step-by-step.

**TL;DR:**

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/lead-nurture.git
git push -u origin main

# 2. Deploy on Railway
# - Go to railway.app
# - "New Project" → "Deploy from GitHub repo"
# - Select your repo
# - Add CLOSE_IO_API_KEY env var to both services
# - Mount volume at /app/.tmp for both services
# - Generate domain for web service

# 3. Done!
```

## What Railway Will Run

**Service 1: Web (Webhook Server)**
- Handles instant lead enrollment
- Public URL: `https://your-app.up.railway.app`
- Endpoint: `/enroll`

**Service 2: Worker (Orchestrator)**
- Sends scheduled emails
- Runs continuously in background
- Checks every 5 minutes

## Architecture

```
Lead Capture System
    ↓ (webhook)
Railway Web Service → Enrolls lead instantly
    ↓
Sends welcome email
    ↓
Saves to persistent volume (.tmp/)
    ↓
Railway Worker Service → Sends scheduled emails
    ↓
Close.io (all emails tracked)
```

## Files Overview

| File | Purpose |
|------|---------|
| `Procfile` | Tells Railway what processes to run |
| `railway.json` | Railway configuration |
| `runtime.txt` | Python version (3.11) |
| `execution/requirements.txt` | Python dependencies |
| `.env` | Local env vars (NOT deployed) |
| `.gitignore` | Files to exclude from git |

## Environment Variables (Railway)

Add these in Railway dashboard for **BOTH services**:

```
CLOSE_IO_API_KEY=api_5eU3vaRHw57yk2P8IqpUOh.2kEZUzxL9ArkSrnd3mfkmw
```

Railway auto-provides `PORT` for web service.

## Persistent Storage

Mount a volume at `/app/.tmp` for **BOTH services**:
- Stores lead state (`lead_nurture_state.json`)
- Stores activity logs (`nurture_log.json`)
- Persists across deploys and restarts

## Test Locally Before Deploy

**Windows:**
```bash
start_local.bat
```

**Or manually:**
```bash
# Terminal 1
python execution/webhook_server.py 8080

# Terminal 2
python execution/lead_nurture_orchestrator.py --continuous 300
```

Test webhook:
```bash
curl -X POST http://localhost:8080/enroll \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "call_time": "2025-01-15T14:00:00Z"}'
```

## Costs

**Railway Pricing:**
- Free tier: $5 credit/month
- Hobby: $5/month (recommended)
- Pro: $20/month

**Your usage:** ~$5-10/month (2 services, 24/7)

## Deployment Checklist

Follow [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) for complete steps.

**Quick checklist:**
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Web service deployed
- [ ] Worker service deployed
- [ ] Env vars added to both
- [ ] Volumes mounted to both
- [ ] Domain generated for web
- [ ] Tested webhook endpoint
- [ ] Lead capture integrated

## After Deployment

1. **Test the webhook:**
   ```bash
   curl https://your-app.up.railway.app/health
   ```

2. **Monitor logs** in Railway dashboard

3. **Integrate with lead capture:**
   - Add webhook URL to Calendly/booking tool
   - Or call directly from your system

4. **Monitor for 24 hours:**
   - Check both services are running
   - Verify emails sending
   - Confirm state persisting

## Support

**Documentation:**
- [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) - Detailed deployment guide
- [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) - Step-by-step checklist
- [TESTING.md](TESTING.md) - Testing guide
- [INTEGRATION.md](INTEGRATION.md) - Integration options

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

## Updates

To update your deployment:

```bash
# Make changes locally
# Test
git add .
git commit -m "Update: description"
git push
```

Railway auto-deploys on push to main.

## Ready?

Follow [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) to deploy!

Your lead nurture system will be running 24/7 in about 15 minutes. 🚀
