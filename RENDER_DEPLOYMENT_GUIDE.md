# Render.com Deployment Guide

## Overview

This guide will help you deploy your Professional Services Special Deals Dashboard to Render.com **for FREE**, making it accessible 24/7 without depending on your Mac.

---

## What We Changed

✅ **Replaced browser automation** with Salesforce API (faster, more reliable)  
✅ **Created deployment files** (requirements.txt, render.yaml)  
✅ **Added cloud scheduler** for automatic data sync every 4 hours  
✅ **Made app production-ready** with environment variables  

---

## Prerequisites

### 1. Create Render.com Account (FREE)

1. Go to: https://render.com
2. Click **"Get Started for Free"**
3. Sign up with:
   - GitHub (recommended)
   - GitLab
   - Email

**Free Tier Includes:**
- ✅ 750 hours/month (enough for 24/7)
- ✅ Custom domains
- ✅ Automatic SSL (HTTPS)
- ✅ No credit card required

### 2. Get Salesforce API Credentials

You need these credentials to connect to Salesforce API:

#### Step 2.1: Get Your Security Token

1. Log into Salesforce
2. Click your profile picture (top right)
3. Go to **Settings**
4. In left sidebar: **My Personal Information** → **Reset My Security Token**
5. Click **Reset Security Token**
6. Check your email for the new security token
7. **Save this token** - you'll need it later

#### Step 2.2: Create a Connected App (Optional but Recommended)

For better security, create a Connected App:

1. In Salesforce, go to **Setup**
2. Search for **"App Manager"**
3. Click **New Connected App**
4. Fill in:
   - **Connected App Name**: `PS Dashboard API`
   - **API Name**: `PS_Dashboard_API`
   - **Contact Email**: your-email@company.com
5. Check **Enable OAuth Settings**
6. **Callback URL**: `https://login.salesforce.com/services/oauth2/callback`
7. **Selected OAuth Scopes**: Add:
   - Full access (full)
   - Perform requests on your behalf at any time (refresh_token, offline_access)
8. Click **Save**
9. Wait 2-10 minutes for changes to take effect

**Note**: For now, we'll use username/password/token authentication. Connected App OAuth can be added later.

### 3. Push Code to GitHub

Your code needs to be in a GitHub repository for Render to deploy it.

#### Step 3.1: Initialize Git Repository

```bash
cd ~/salesforce-opportunity-tool

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Ready for Render deployment"
```

#### Step 3.2: Create GitHub Repository

1. Go to: https://github.com
2. Click **"+"** → **New repository**
3. Repository name: `ps-special-deals-dashboard`
4. Make it **Private** (recommended for business data)
5. **DO NOT** initialize with README (we already have code)
6. Click **Create repository**

#### Step 3.3: Push to GitHub

```bash
# Add GitHub remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/ps-special-deals-dashboard.git

# Push code
git branch -M main
git push -u origin main
```

**Example**:
```bash
git remote add origin https://github.com/johndoe/ps-special-deals-dashboard.git
git branch -M main
git push -u origin main
```

---

## Deployment Steps

### Step 1: Create Web Service on Render

1. Go to: https://dashboard.render.com
2. Click **"New +"** → **Web Service**
3. Click **"Connect to GitHub"** (if not already connected)
4. Find your repository: `ps-special-deals-dashboard`
5. Click **"Connect"**

### Step 2: Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `ps-special-deals-dashboard` (or any name you like)
- **Region**: Choose closest to you (e.g., Oregon for US West)
- **Branch**: `main`
- **Root Directory**: (leave blank)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- Select: **Free** (this is important!)

**Environment Variables:**
Click **"Add Environment Variable"** and add these:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.9.18` | Python version |
| `FLASK_ENV` | `production` | Production mode |
| `SALESFORCE_USERNAME` | `your-email@company.com` | Your Salesforce email |
| `SALESFORCE_PASSWORD` | `your-password` | Your Salesforce password |
| `SALESFORCE_TOKEN` | `your-security-token` | From email (Step 2.1) |
| `SALESFORCE_DOMAIN` | `login` | Use `test` for sandbox |

**Example Environment Variables:**
```
PYTHON_VERSION = 3.9.18
FLASK_ENV = production
SALESFORCE_USERNAME = john.doe@company.com
SALESFORCE_PASSWORD = MySecurePassword123
SALESFORCE_TOKEN = ABC123XYZ456DEF789
SALESFORCE_DOMAIN = login
```

### Step 3: Deploy

1. Scroll to bottom
2. Click **"Create Web Service"**
3. Wait 3-5 minutes for deployment

**You'll see**:
- ✅ Build logs (installing packages)
- ✅ Deploy logs (starting app)
- ✅ Your dashboard URL (e.g., `https://ps-special-deals-dashboard.onrender.com`)

---

## Step 4: Add Background Worker (For Scheduled Sync)

The web service runs your dashboard, but we need a separate worker to run the scheduled Salesforce sync.

### Create Background Worker

1. In Render dashboard, click **"New +"** → **Background Worker**
2. Select same repository: `ps-special-deals-dashboard`
3. Fill in settings:

**Basic Settings:**
- **Name**: `ps-special-deals-worker`
- **Region**: Same as web service
- **Branch**: `main`
- **Root Directory**: (leave blank)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python cloud_scheduler.py`

**Instance Type:**
- Select: **Free**

**Environment Variables:**
Copy the same environment variables from Step 2:
- `PYTHON_VERSION`
- `FLASK_ENV`
- `SALESFORCE_USERNAME`
- `SALESFORCE_PASSWORD`
- `SALESFORCE_TOKEN`
- `SALESFORCE_DOMAIN`

4. Click **"Create Background Worker"**

**This worker will**:
- ✅ Run immediately on startup (initial sync)
- ✅ Sync data from Salesforce every 4 hours
- ✅ Keep your dashboard data up-to-date

---

## Verify Deployment

### 1. Check Web Service

1. In Render dashboard, click on your web service
2. Look for **"Your service is live"** message
3. Click on the URL (e.g., `https://ps-special-deals-dashboard.onrender.com`)
4. You should see your dashboard!

### 2. Check Background Worker

1. In Render dashboard, click on your background worker
2. Click **"Logs"** tab
3. Look for:
   ```
   🚀 Cloud Scheduler started
   🔄 Running initial sync...
   ✅ Connected to Salesforce successfully
   ✅ Fetched XXX opportunities
   ✅ Saved XXX records to database
   ✅ Sync completed successfully
   ```

### 3. Check Dashboard Data

1. Open your dashboard URL
2. You should see:
   - ✅ KPI cards showing numbers (not zeros)
   - ✅ Regional chart with data
   - ✅ Donut chart with special terms
   - ✅ Project details table populated

---

## Troubleshooting

### Issue 1: "Application failed to start"

**Cause**: Missing or incorrect environment variables

**Solution**:
1. Go to web service in Render
2. Click **"Environment"** tab
3. Verify all environment variables are set correctly
4. Click **"Manual Deploy"** → **"Deploy latest commit"**

### Issue 2: "No data showing in dashboard"

**Cause**: Background worker not syncing data

**Solution**:
1. Check background worker logs
2. Look for error messages
3. Verify Salesforce credentials are correct
4. Make sure `SALESFORCE_DOMAIN` is `login` (not `test`) for production

### Issue 3: "Salesforce authentication failed"

**Cause**: Incorrect credentials or security token

**Solutions**:
- **Username**: Must be your full Salesforce email
- **Password**: Your Salesforce password (not Render password!)
- **Security Token**: From email (reset if needed)
- **Domain**: `login` for production, `test` for sandbox

**How to reset security token**:
1. Log into Salesforce
2. Settings → My Personal Information → Reset My Security Token
3. Check email for new token
4. Update `SALESFORCE_TOKEN` in Render environment variables
5. Restart worker: Click **"Manual Deploy"** → **"Clear build cache & deploy"**

### Issue 4: "Free instance spins down"

**Note**: Render free instances spin down after 15 minutes of inactivity.

**What happens**:
- First request after spin-down takes ~30 seconds (cold start)
- Subsequent requests are fast

**To avoid**:
- Upgrade to paid plan ($7/month) for always-on
- Or set up external uptime monitor (pings your site every 10 minutes)

---

## Updating Your Dashboard

When you want to make changes to the dashboard:

### Local Changes

1. Make changes to your code locally
2. Test locally: `python app.py`
3. Commit changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
4. Render will **automatically deploy** your changes!

### Environment Variable Changes

1. Go to Render dashboard
2. Click on web service (or worker)
3. Click **"Environment"** tab
4. Update variables
5. Service will automatically restart

---

## What You Get

### Dashboard URL

Your dashboard will be available at:
```
https://ps-special-deals-dashboard.onrender.com
```

**Custom Domain** (optional):
- You can add your own domain (e.g., `dashboard.yourcompany.com`)
- Go to **Settings** → **Custom Domains**
- Follow Render's instructions

### Features

✅ **24/7 Availability** - Runs even when your Mac is off  
✅ **Auto Data Sync** - Salesforce data syncs every 4 hours  
✅ **Dashboard Auto-Refresh** - UI refreshes every 30 seconds  
✅ **Remote Access** - Access from anywhere (home, office, mobile)  
✅ **Team Access** - Share URL with your team  
✅ **Secure** - HTTPS enabled automatically  
✅ **Free** - No monthly cost on free tier  

---

## Monitoring

### Check Sync Status

1. Go to Render dashboard
2. Click on background worker
3. Click **"Logs"** tab
4. You'll see sync activity every 4 hours

### Check Dashboard Health

1. Simply visit your dashboard URL
2. Check if data is current
3. Look for KPI numbers and charts

---

## Advanced: Change Sync Frequency

To sync more or less frequently:

1. Edit `cloud_scheduler.py` in your code
2. Find line: `schedule.every(4).hours.do(scheduled_sync)`
3. Change to:
   - **Every 1 hour**: `schedule.every(1).hour.do(scheduled_sync)`
   - **Every 30 minutes**: `schedule.every(30).minutes.do(scheduled_sync)`
   - **Daily at 9 AM**: `schedule.every().day.at("09:00").do(scheduled_sync)`
4. Commit and push:
   ```bash
   git add cloud_scheduler.py
   git commit -m "Update sync frequency"
   git push origin main
   ```
5. Render will auto-deploy the change

---

## Costs

### Free Tier (What You're Using)

- ✅ **Cost**: $0/month
- ✅ **Hours**: 750 hours/month per service
- ⚠️ **Note**: Free instances spin down after 15 minutes of inactivity
- ✅ **Your setup**: 2 services (web + worker) = 1500 total hours (plenty!)

### If You Want Always-On (No Spin-Down)

**Starter Plan**: $7/month per service
- ✅ Always on (no spin-down)
- ✅ Faster performance
- ✅ More memory

**Your cost if upgraded**: $14/month (web + worker)

---

## Security Best Practices

1. ✅ **Never commit `.env` files** - Gitignore is already set up
2. ✅ **Use environment variables** - Already configured
3. ✅ **Make repository private** - Recommended for business data
4. ✅ **Rotate Salesforce token** - Every 90 days (Salesforce policy)
5. ✅ **Monitor logs** - Check for unusual activity

---

## Support

### Render Support

- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### Dashboard Issues

If you encounter issues:
1. Check Render logs (most helpful)
2. Verify environment variables
3. Test Salesforce credentials
4. Check this deployment guide

---

## Summary Checklist

Before you start:
- [ ] Created Render.com account
- [ ] Got Salesforce security token
- [ ] Created GitHub repository
- [ ] Pushed code to GitHub

Deployment:
- [ ] Created web service on Render
- [ ] Added all environment variables
- [ ] Created background worker
- [ ] Added same environment variables to worker

Verification:
- [ ] Web service shows "Your service is live"
- [ ] Background worker logs show successful sync
- [ ] Dashboard URL loads and shows data
- [ ] KPIs display correct numbers
- [ ] Charts show regional data

---

## Next Steps After Deployment

1. **Bookmark your dashboard URL**
2. **Share URL with your team**
3. **Set up uptime monitoring** (optional)
4. **Configure custom domain** (optional)
5. **Enjoy your Mac-independent dashboard!** 🎉

---

**Your dashboard is now running independently on Render.com!**

No more dependency on your Mac. Access it from anywhere, anytime.

If you need help with any step, let me know!
