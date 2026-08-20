# Salesforce Report Auto-Sync Guide

Automatically download Salesforce reports and update your dashboard using browser automation.

## 🎯 How It Works

1. Opens a browser (Chrome) using your saved login session
2. Navigates to your Salesforce report
3. Downloads the report as CSV
4. Uploads it to your dashboard automatically
5. Runs on a schedule (every 4 hours by default)

**No API credentials or email access needed!** Uses your browser's saved login.

---

## 🚀 First Time Setup (One-Time)

### Step 1: Login to Salesforce

Run this command to setup your browser session:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_sync.py --login
```

**What happens:**
1. A browser window opens
2. You'll see the Salesforce login page
3. **Log in manually** with your credentials
4. The script saves your session for future use
5. The report will download automatically

**First time may require manual export:**
- If the script can't find the Export button, manually click:
  - Report dropdown (⚙️ or ⋮)
  - "Export" → "Export Details"
  - Choose "CSV" format

The browser will close after download completes.

---

## ✅ Testing the Automation

After first-time setup, test that it works automatically:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_sync.py --headless
```

This runs in the background without opening a visible browser window.

**Expected output:**
```
🚀 Starting Salesforce Report Auto-Sync
🌐 Launching browser...
📊 Navigating to Salesforce report...
✅ Page loaded successfully
✅ Report downloaded: report.csv
📤 Uploading to dashboard...
✅ Upload successful!
✅ Sync completed successfully!
```

---

## 🕐 Setting Up Automatic Schedule

### Option 1: Run Scheduler (Recommended)

Keeps running in the background and syncs every 4 hours:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python scheduler.py
```

**To customize the schedule, edit `scheduler.py`:**

```python
# Every 4 hours (default)
SYNC_INTERVAL_HOURS = 4

# Or every 30 minutes
# SYNC_INTERVAL_MINUTES = 30

# Or daily at 9 AM
# schedule.every().day.at("09:00").do(run_sync)

# Or every Monday at 9 AM
# schedule.every().monday.at("09:00").do(run_sync)
```

**To stop the scheduler:**
Press `Ctrl+C` in the terminal

---

### Option 2: Run on Demand

Manually run sync whenever you want:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_sync.py --headless
```

---

### Option 3: macOS LaunchAgent (Always Running)

To keep the scheduler running even after reboot:

1. Create a launch agent file:

```bash
nano ~/Library/LaunchAgents/com.salesforce.autosync.plist
```

2. Paste this content (update YOUR_USERNAME):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.salesforce.autosync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/salesforce-opportunity-tool/venv/bin/python</string>
        <string>/Users/YOUR_USERNAME/salesforce-opportunity-tool/scheduler.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/salesforce-opportunity-tool/sync.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/salesforce-opportunity-tool/sync.error.log</string>
</dict>
</plist>
```

3. Load the launch agent:

```bash
launchctl load ~/Library/LaunchAgents/com.salesforce.autosync.plist
```

4. To stop it:

```bash
launchctl unload ~/Library/LaunchAgents/com.salesforce.autosync.plist
```

---

## 🔧 Configuration

### Change Report URL

Edit `auto_sync.py` and update:

```python
SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/YOUR_REPORT_ID/view"
```

### Change Sync Frequency

Edit `scheduler.py`:

```python
# Options:
SYNC_INTERVAL_HOURS = 6          # Every 6 hours
schedule.every(30).minutes.do()  # Every 30 minutes
schedule.every().day.at("08:00") # Daily at 8 AM
```

---

## 🐛 Troubleshooting

### Session Expired Error

If you see "Session expired" message:

```bash
python auto_sync.py --login
```

Login again to refresh your session.

---

### Export Button Not Found

The script tries multiple methods to find the Export button. If it fails:

1. Run with `--login` flag to see the browser
2. Manually click Export when prompted
3. The download will still work

Or update the button selector in `auto_sync.py`:

```python
export_button_selectors = [
    "your-custom-selector-here",
    # existing selectors...
]
```

---

### Download Not Detected

Check the downloads folder:

```bash
ls -la ~/salesforce-opportunity-tool/downloads/
```

If files are there but not uploading, check dashboard is running:

```bash
curl http://localhost:5001/api/stats
```

---

### Browser Not Closing

If browser stays open, manually close it or kill the process:

```bash
pkill -f playwright
```

---

## 📊 Monitoring

### Check Scheduler Logs

If running as background service:

```bash
tail -f ~/salesforce-opportunity-tool/sync.log
```

### Check Last Sync

Dashboard shows last upload time in the "Upload History" tab.

---

## 🔒 Security Notes

- ✅ Your session is saved locally in `browser_data/` folder
- ✅ No passwords stored in code
- ✅ All data stays on your computer
- ✅ Uses your existing browser session (like staying logged in)
- ⚠️ Keep your computer secure (session = access to Salesforce)

---

## 📁 Files Created

```
salesforce-opportunity-tool/
├── auto_sync.py           # Main automation script
├── scheduler.py           # Scheduling script
├── browser_data/          # Saved browser session (DO NOT DELETE)
├── downloads/             # Downloaded CSV files
└── AUTO_SYNC_GUIDE.md     # This file
```

---

## 🎉 Quick Reference

```bash
# First time setup
python auto_sync.py --login

# Test automation
python auto_sync.py --headless

# Start scheduler (every 4 hours)
python scheduler.py

# Manual sync anytime
python auto_sync.py --headless
```

---

## 💡 Tips

- **Keep dashboard running:** The auto-sync uploads to `http://localhost:5001`
- **Monitor regularly:** Check Upload History tab to ensure syncs are working
- **Re-login monthly:** Sessions expire after ~30 days, re-run `--login`
- **Customize timing:** Edit `scheduler.py` to match your workflow
- **Multiple reports:** Create separate config files for different reports

---

## ⏭️ Next Steps

Once auto-sync is working:

1. Add Slack notifications for new opportunities
2. Set up email alerts for billing exceptions
3. Create custom reports and analytics
4. Add data validation rules

Let me know if you'd like help with any of these enhancements!
