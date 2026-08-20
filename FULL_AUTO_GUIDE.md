# 🤖 Full Automation Guide - Dashboard Auto-Refresh

## ✅ What You Get

Your Salesforce dashboard now **refreshes automatically every 4 hours** with zero manual work!

### Fully Automated Pipeline:

```
Every 4 Hours:
1. ⏰ Scheduler triggers export
2. 🌐 Browser opens to Salesforce report
3. 🤖 Script attempts to click Export automatically
4. 📥 File downloads
5. 📝 File renamed to report*.csv
6. 👀 Watcher detects file (2 seconds)
7. 📤 Auto-uploads to dashboard
8. 📊 Dashboard refreshes with latest data
9. 📁 File archived
```

**You don't have to do anything!**

---

## 🚀 Quick Start

### Start Full Automation (One Command):

```bash
cd ~/salesforce-opportunity-tool
./start_full_automation.sh
```

This starts:
- ✅ Dashboard at http://localhost:5001
- ✅ Auto-upload watcher
- ✅ Export scheduler (runs every 4 hours)

### First Export:
- Browser window opens immediately
- **If you need to log in**: Do it once (session persists)
- **If automation doesn't click**: Just make the 5 clicks yourself
  1. Click dropdown next to Edit
  2. Click Export  
  3. Select "Details Only"
  4. Select "Comma Delimited .csv"
  5. Click Export button

**After that**: Exports run automatically every 4 hours!

---

## 📅 Schedule

**Default**: Every 4 hours  
**First Run**: Immediately when you start  
**Times**: 
- If started at 10:00 AM → Runs at 10 AM, 2 PM, 6 PM, 10 PM, etc.

### Change Schedule:

Edit `auto_scheduler.py` and change line:
```python
INTERVAL_HOURS = 4  # Change this number
```

**Alternative schedules** (uncomment in `auto_scheduler.py`):
```python
# Every 30 minutes:
schedule.every(30).minutes.do(run_export)

# Daily at 9 AM:
schedule.every().day.at("09:00").do(run_export)

# Every Monday at 9 AM:
schedule.every().monday.at("09:00").do(run_export)
```

---

## 🖥️ Browser Behavior

### What to Expect:

**First time**: 
- Browser opens
- You may need to log in
- Automation attempts to click Export
- If it can't, you click manually (5 clicks)
- File downloads automatically

**Subsequent runs**:
- Browser opens automatically
- Usually stays logged in
- Automation tries to export
- If successful: No interaction needed!
- If not: Just make the 5 clicks

### Headless Mode (Optional):

For background operation without browser window:
```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_export_aggressive.py --headless
```

**Note**: Headless mode only works if:
- You're already logged in
- Automation successfully finds Export button

---

## 📊 View Dashboard

**URL**: http://localhost:5001

Updates automatically when new data arrives:
- Total projects
- Regional breakdowns
- Special terms (Holdback, Framework, Umbrella)
- Billing status
- Charts and filters

---

## 🔍 Check Status

```bash
cd ~/salesforce-opportunity-tool
./status.sh
```

Shows:
- ✅ Dashboard running
- ✅ Watcher running
- ✅ Scheduler running (NEW!)
- Recent uploads
- Project counts

---

## 📝 View Logs

### Live monitoring:
```bash
# Scheduler activity
tail -f /tmp/salesforce_scheduler.log

# Dashboard activity
tail -f /tmp/salesforce_dashboard.log

# Watcher activity
tail -f /tmp/salesforce_watcher.log
```

### Check recent exports:
```bash
tail -100 /tmp/salesforce_scheduler.log
```

---

## 🛑 Stop Automation

```bash
cd ~/salesforce-opportunity-tool
./stop_full_automation.sh
```

Stops:
- Dashboard
- Watcher
- Scheduler

---

## ⚠️ Troubleshooting

### Scheduler not running exports?

Check logs:
```bash
tail -50 /tmp/salesforce_scheduler.log
```

Check if running:
```bash
ps aux | grep auto_scheduler | grep -v grep
```

### Exports failing?

**Common causes**:
1. **Login required** - Salesforce session expired
   - Solution: Run once manually, log in, then restart scheduler

2. **Automation can't click Export** - UI changed or elements not found
   - Solution: Browser stays open, just click manually

3. **Download blocked** - Browser permissions
   - Solution: Allow downloads in browser settings

### File not uploading?

Check watcher is running:
```bash
ps aux | grep auto_upload_watcher | grep -v grep
```

Check file name:
```bash
ls ~/Downloads/report*.csv
```

Must be named `report*.csv` for watcher to detect.

### Restart everything:

```bash
cd ~/salesforce-opportunity-tool
./stop_full_automation.sh
sleep 5
./start_full_automation.sh
```

---

## 🎯 Advanced Configuration

### Run export manually anytime:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_export_aggressive.py
```

### Skip automation (manual export):

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_export_aggressive.py --manual
```

Browser opens, you do everything manually, script just waits for download.

### Change how aggressive the automation is:

Edit `auto_export_aggressive.py`:
- Line with `time.sleep(15)` - change wait time for page loading
- JavaScript strategies - modify to match your Salesforce UI

---

## 📈 What Gets Tracked

Every 4 hours, your dashboard updates with:

### Summary:
- Total projects: 494
- Holdback: 134
- Framework: 149
- Umbrella: 59
- Excluded from billing: 64

### Regional Data:
- APAC ANZ, EMEA UKI, AMER, LATAM
- Breakdown by special terms
- Billing status per region

### Project Details:
- PM1, PM2, Opportunity Owner
- Close date, amount
- Billing frequency
- Special terms
- Exclude from billing status

---

## ✅ Success Criteria

**Your automation is working if:**

1. ✅ Dashboard accessible at http://localhost:5001
2. ✅ Scheduler log shows export runs every 4 hours
3. ✅ New `report*.csv` files appear in `~/Downloads/salesforce_archive/`
4. ✅ Dashboard "Last Updated" timestamp changes every 4 hours
5. ✅ Project count stays current (increases as projects are added)

---

## 🎉 You're Done!

Your dashboard is now **fully automated** with scheduled refreshes every 4 hours!

**Start it:**
```bash
cd ~/salesforce-opportunity-tool && ./start_full_automation.sh
```

**View it:**
http://localhost:5001

**Forget about it:**
Data refreshes automatically! 🚀

---

## 🔮 Future Enhancements (Optional)

Want even more automation?

1. **Slack notifications** - Alert when special terms projects arrive
2. **Slack channels** - Auto-create for PM1, PM2, Opportunity Owner
3. **Bi-weekly reminders** - 2nd week of month for billing verification
4. **Google Sheets sync** - Regional contacts integration
5. **Email reports** - Weekly summary emails

Let me know if you want any of these!
