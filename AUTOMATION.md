# 🤖 Salesforce Dashboard - Full Automation Guide

## ✅ What's Automated

Your PSA Projects Dashboard is now **fully automated** with real-time data updates!

### How It Works:

```
1. You export report from Salesforce → Downloads to ~/Downloads
2. Auto-Watcher detects new file → Within 2 seconds
3. Automatically uploads to Dashboard → Instant processing
4. Dashboard updates in real-time → 494 projects tracked
5. File archived automatically → ~/Downloads/salesforce_archive/
```

---

## 🚀 Quick Start

### Start All Services:
```bash
cd ~/salesforce-opportunity-tool
./start_all.sh
```

### Check Status:
```bash
cd ~/salesforce-opportunity-tool
./status.sh
```

### Stop All Services:
```bash
cd ~/salesforce-opportunity-tool
./stop_all.sh
```

---

## 📊 Access Your Dashboard

**URL**: http://localhost:5001

**Tabs Available:**
1. **Dashboard** - Overview with charts & stats
2. **Regional Analysis** - Breakdown by region
3. **Upload Data** - Manual upload (if needed)
4. **All Projects** - Filterable table
5. **Upload History** - Track uploads

---

## ✨ How to Use (No Manual Upload Needed!)

### Step 1: Export from Salesforce
1. Go to: https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view
2. Click **Export** → **Export Details** → **CSV**
3. File downloads to `~/Downloads/report*.csv`

### Step 2: Wait 2 Seconds
- Watcher detects new file automatically
- Uploads to dashboard
- Processes all 494+ projects
- Updates all statistics

### Step 3: View Updated Dashboard
- Refresh http://localhost:5001
- See new data immediately
- Regional breakdowns updated
- Charts refreshed

**That's it! No manual upload needed!**

---

## 📈 What Data is Tracked

### Summary Statistics:
- **Total Projects**: 494
- **Holdback**: 134 projects
- **Framework**: 149 projects
- **Umbrella**: 59 projects
- **⚠️ Excluded from Billing**: 64 projects

### By Region:
- APAC ANZ: 76 projects
- EMEA UKI: 71 projects  
- AMER FINS & CAN: 38 projects
- LATAM Brazil: 35 projects
- LATAM Mexico: 10 projects
- + more regions

### Billing Status:
- 🔴 **Excluded** (64): Require manual review
- ✅ **Included** (430): Ready for invoicing

---

## 🔍 Filters Available

1. **By Region**: Select specific region
2. **By Special Term**: Holdback, Framework, Umbrella, etc.
3. **By Billing Status**: Included / Excluded
4. **Search**: By project name, PM, account

---

## 📝 Logs & Debugging

### Check Logs:
```bash
# Dashboard logs
tail -f /tmp/salesforce_dashboard.log

# Watcher logs
tail -f /tmp/salesforce_watcher.log
```

### Test Upload Manually:
```bash
curl -X POST -F "file=@/path/to/report.csv" http://localhost:5001/api/upload
```

---

## ⚠️ Troubleshooting

### Services Not Running?
```bash
cd ~/salesforce-opportunity-tool
./start_all.sh
```

### Dashboard Not Accessible?
```bash
# Check if port 5001 is in use
lsof -i:5001

# Kill conflicting process
kill -9 <PID>

# Restart
./start_all.sh
```

### Watcher Not Detecting Files?
```bash
# Check watcher is running
ps aux | grep auto_upload_watcher

# Check watcher logs
tail -f /tmp/salesforce_watcher.log

# File must be named: report*.csv
# File must be in: ~/Downloads/
```

---

## 🎯 Next Steps (Optional)

### Phase 2: Slack Notifications
- Auto-create Slack channels for new special term projects
- Notify regional contacts from Google Sheet
- Bi-weekly reminders (2nd week of month)
- Billing exception alerts

### Phase 3: Scheduled Exports
- Browser automation every 4 hours
- Fully hands-free data updates
- No manual exports needed

---

## 📊 Data Fields Tracked

| Field | Description |
|-------|-------------|
| Project Name | PSA Project name |
| Region | Geographic region |
| Subregion | Specific subregion |
| Special Term | Holdback, Framework, Umbrella, etc. |
| Billing Frequency | Monthly, Quarterly, etc. |
| PM 1 | Project Manager 1 |
| PM 2 | Project Manager 2 |
| Opportunity Owner | Salesforce opportunity owner |
| Close Date | Opportunity close date |
| Amount | Contract value |
| Exclude From Billing | 0=Included, 1=Excluded |
| PO Number | Purchase order number |
| Account Number | Customer account number |
| Billings | Amount billed |
| Invoiced | Amount invoiced |

---

## ✅ Automation is ACTIVE!

Your dashboard is now monitoring for new Salesforce exports 24/7. Simply export from Salesforce whenever you need updated data, and the dashboard will update automatically within 2 seconds!

**Dashboard**: http://localhost:5001
**Status**: `./status.sh`
**Support**: Check logs in `/tmp/salesforce_*.log`
