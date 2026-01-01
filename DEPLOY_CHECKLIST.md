# Railway Deployment Checklist

Use this checklist to deploy your lead nurture system to Railway.

## Pre-Deployment

- [ ] Close.io API key ready: `api_5eU3vaRHw57yk2P8IqpUOh.2kEZUzxL9ArkSrnd3mfkmw`
- [ ] GitHub account ready
- [ ] Railway account created (https://railway.app)
- [ ] Tested system locally

## Step 1: Push to GitHub (5 min)

```bash
# In your project directory
cd "c:\Users\arnel\OneDrive\Desktop\DobotAI\Agents\Lead Nurture"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Lead Nurture System"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/lead-nurture.git
git branch -M main
git push -u origin main
```

- [ ] Repository created on GitHub
- [ ] Code pushed to main branch

## Step 2: Create Railway Project (2 min)

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway + GitHub
5. Select your `lead-nurture` repository

- [ ] Railway project created
- [ ] Connected to GitHub repo

## Step 3: Configure Web Service (3 min)

Railway should auto-detect your Procfile and create a web service.

1. Click on the web service
2. Go to "Variables" tab
3. Add variable:
   ```
   CLOSE_IO_API_KEY=api_5eU3vaRHw57yk2P8IqpUOh.2kEZUzxL9ArkSrnd3mfkmw
   ```
4. Go to "Settings" → "Volumes"
5. Click "+ New Volume"
   - Mount Path: `/app/.tmp`
   - Size: 1 GB
6. Click "Add"
7. Go to "Settings" → "Networking"
8. Click "Generate Domain"

- [ ] CLOSE_IO_API_KEY added
- [ ] Volume mounted at /app/.tmp
- [ ] Public domain generated
- [ ] Web service deployed

**Your webhook URL:** `https://________.up.railway.app/enroll`

## Step 4: Configure Worker Service (3 min)

1. Click "+ New Service"
2. Select "GitHub Repo" → Same repo
3. Go to "Settings" → "Deploy"
4. Set "Start Command":
   ```
   python execution/lead_nurture_orchestrator.py --continuous 300
   ```
5. Go to "Variables" tab
6. Add same variable:
   ```
   CLOSE_IO_API_KEY=api_5eU3vaRHw57yk2P8IqpUOh.2kEZUzxL9ArkSrnd3mfkmw
   ```
7. Go to "Settings" → "Volumes"
8. Click "+ New Volume"
   - Mount Path: `/app/.tmp`
   - Size: 1 GB

- [ ] Worker service created
- [ ] Start command configured
- [ ] CLOSE_IO_API_KEY added
- [ ] Volume mounted at /app/.tmp
- [ ] Worker deployed

## Step 5: Verify Deployment (2 min)

### Check Web Service

```bash
# Health check
curl https://YOUR-APP.up.railway.app/health

# Expected: {"status": "ok", "service": "lead-nurture-webhook"}
```

- [ ] Health check returns OK

### Check Logs

1. Click on web service → "Logs" tab
   - Should see: "Lead Nurture Webhook Server running on port..."

2. Click on worker service → "Logs" tab
   - Should see: "Running nurture workflow at..."

- [ ] Web service logs show server running
- [ ] Worker logs show orchestrator running

### Test Enrollment

```bash
curl -X POST https://YOUR-APP.up.railway.app/enroll \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "call_time": "2025-01-15T14:00:00Z"
  }'
```

- [ ] Enrollment test successful
- [ ] Email received at test@example.com
- [ ] Email appears in Close.io

## Step 6: Production Setup (5 min)

### Update Lead Capture Integration

Add your Railway webhook URL to your lead capture system:

**Webhook URL:**
```
https://YOUR-APP.up.railway.app/enroll
```

**Calendly:**
- Account → Webhooks → Add webhook
- URL: Your Railway URL
- Event: invitee.created

**Zapier:**
- Action: Webhooks by Zapier
- URL: Your Railway URL
- Method: POST

- [ ] Lead capture system configured
- [ ] Webhook URL added

### Monitor First 24 Hours

Check Railway dashboard regularly:
- [ ] Both services running (green status)
- [ ] No error logs
- [ ] Emails sending successfully
- [ ] Lead state persisting

## Troubleshooting

### If web service fails:
1. Check logs for errors
2. Verify PORT env var (auto-set by Railway)
3. Check Procfile syntax

### If worker fails:
1. Check logs for errors
2. Verify CLOSE_IO_API_KEY
3. Verify start command

### If emails not sending:
1. Check Close.io email configuration
2. Review worker logs
3. Check `.tmp/failed_emails.json` in volume

## Complete! 🎉

Your lead nurture system is now:
- ✅ Running 24/7 on Railway
- ✅ Accepting webhook calls
- ✅ Sending emails automatically
- ✅ Persisting state across restarts

**Next:**
- Monitor for 24-48 hours
- Customize email templates if needed
- Set up monitoring alerts (Railway Pro)

---

## Quick Reference

**Railway Dashboard:** https://railway.app/dashboard

**Web Service URL:** https://________.up.railway.app

**Webhook Endpoint:** https://________.up.railway.app/enroll

**View Logs:**
```bash
railway logs --service web
railway logs --service worker
```

**Update Deployment:**
```bash
git add .
git commit -m "Update message"
git push
```
(Railway auto-deploys)

**Need Help?**
- See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for detailed guide
- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app
