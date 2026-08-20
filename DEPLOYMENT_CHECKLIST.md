# Render.com Deployment Checklist

## Quick Reference Guide

Use this checklist to deploy your dashboard to Render.com step by step.

---

## Pre-Deployment (15 minutes)

### 1. Salesforce Credentials

- [ ] Log into Salesforce
- [ ] Go to Settings → My Personal Information → Reset My Security Token
- [ ] Check email for security token
- [ ] Save these credentials (you'll need them):
  ```
  Username: ________________@company.com
  Password: ________________
  Token: ________________
  ```

### 2. GitHub Setup

- [ ] Create GitHub account (if needed): https://github.com
- [ ] Note your GitHub username: ________________

### 3. Render Account

- [ ] Create Render account: https://render.com
- [ ] Sign up with GitHub (recommended)
- [ ] Connect GitHub to Render

---

## Deploy to GitHub (5 minutes)

### Commands to Run

```bash
# Go to project directory
cd ~/salesforce-opportunity-tool

# Initialize git
git init

# Add all files
git add .

# Create commit
git commit -m "Initial commit - Ready for Render deployment"

# Create GitHub repository (do this on GitHub website):
# 1. Go to https://github.com/new
# 2. Name: ps-special-deals-dashboard
# 3. Make it Private
# 4. Click "Create repository"

# Add remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/ps-special-deals-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Checklist:**
- [ ] Ran `git init`
- [ ] Ran `git add .`
- [ ] Ran `git commit -m "..."`
- [ ] Created GitHub repository
- [ ] Ran `git remote add origin ...`
- [ ] Ran `git push -u origin main`
- [ ] Verified code is on GitHub

---

## Deploy Web Service (10 minutes)

### On Render.com

- [ ] Click **"New +"** → **Web Service**
- [ ] Connect repository: `ps-special-deals-dashboard`
- [ ] Fill in settings:
  - Name: `ps-special-deals-dashboard`
  - Region: Oregon (or closest to you)
  - Branch: `main`
  - Runtime: `Python 3`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn app:app`
  - Instance Type: **Free**

### Add Environment Variables

- [ ] Click "Add Environment Variable" for each:

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.9.18` |
| `FLASK_ENV` | `production` |
| `SALESFORCE_USERNAME` | (your Salesforce email) |
| `SALESFORCE_PASSWORD` | (your Salesforce password) |
| `SALESFORCE_TOKEN` | (from email) |
| `SALESFORCE_DOMAIN` | `login` |

- [ ] Clicked **"Create Web Service"**
- [ ] Waited 3-5 minutes for deployment
- [ ] Saw "Your service is live" message
- [ ] Copied dashboard URL: ________________

---

## Deploy Background Worker (5 minutes)

### On Render.com

- [ ] Click **"New +"** → **Background Worker**
- [ ] Connect same repository: `ps-special-deals-dashboard`
- [ ] Fill in settings:
  - Name: `ps-special-deals-worker`
  - Region: Same as web service
  - Branch: `main`
  - Runtime: `Python 3`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python cloud_scheduler.py`
  - Instance Type: **Free**

### Add Same Environment Variables

- [ ] Added all 6 environment variables (same as web service)
- [ ] Clicked **"Create Background Worker"**
- [ ] Waited 2-3 minutes for deployment
- [ ] Worker is running

---

## Verify Deployment (5 minutes)

### Check Web Service

- [ ] Opened dashboard URL in browser
- [ ] Dashboard loads (not showing errors)
- [ ] Waiting for data to sync...

### Check Background Worker Logs

- [ ] Clicked on worker in Render dashboard
- [ ] Clicked "Logs" tab
- [ ] Saw these messages:
  - [ ] `🚀 Cloud Scheduler started`
  - [ ] `🔄 Running initial sync...`
  - [ ] `✅ Connected to Salesforce successfully`
  - [ ] `✅ Fetched XXX opportunities`
  - [ ] `✅ Saved XXX records to database`
  - [ ] `✅ Sync completed successfully`

### Check Dashboard Has Data

- [ ] Refreshed dashboard URL
- [ ] KPI cards show numbers (not 0 or -)
- [ ] Regional chart displays bars
- [ ] Donut chart shows data
- [ ] Top regions chart shows data
- [ ] Detail table shows projects

---

## Troubleshooting

### If dashboard shows no data:

1. Check background worker logs for errors
2. Verify Salesforce credentials in environment variables
3. Make sure `SALESFORCE_DOMAIN` is `login` (not `test`)
4. Try manual sync: Restart worker in Render dashboard

### If authentication fails:

1. Double-check Salesforce username (full email)
2. Verify password is correct
3. Reset security token if needed:
   - Salesforce → Settings → Reset My Security Token
   - Check email for new token
   - Update `SALESFORCE_TOKEN` in Render
4. Restart worker

### If build fails:

1. Check build logs for specific error
2. Verify `requirements.txt` exists in repository
3. Try "Clear build cache & deploy" in Render

---

## Post-Deployment

### Share Dashboard

- [ ] Bookmark dashboard URL
- [ ] Share URL with team members
- [ ] Test access from different devices

### Monitor

- [ ] Check worker logs daily (first few days)
- [ ] Verify data sync is happening every 4 hours
- [ ] Confirm dashboard is accessible

### Optional Enhancements

- [ ] Set up custom domain
- [ ] Configure uptime monitoring
- [ ] Upgrade to paid plan (if you want always-on)

---

## Your Deployment Info

Fill this in for future reference:

```
Dashboard URL: _________________________________

GitHub Repository: _________________________________

Render Web Service: _________________________________

Render Background Worker: _________________________________

Deployment Date: _________________________________

Last Data Sync: _________________________________
```

---

## Quick Commands for Updates

When you want to update the dashboard:

```bash
# Make changes to code
# Test locally: python app.py

# Commit and push
git add .
git commit -m "Description of change"
git push origin main

# Render will auto-deploy!
```

---

## Success Criteria

✅ Dashboard is accessible from any device  
✅ Dashboard shows current data  
✅ Data syncs automatically every 4 hours  
✅ No dependency on local Mac  
✅ Can shut down Mac and dashboard stays online  
✅ Team members can access dashboard  
✅ Free tier (no monthly cost)  

---

## Need Help?

1. Check RENDER_DEPLOYMENT_GUIDE.md for detailed instructions
2. Check Render logs for error messages
3. Verify environment variables are correct
4. Try clearing build cache and redeploying

---

**Congratulations! Your dashboard is now deployed and running independently! 🎉**
