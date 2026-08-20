# ✅ Working Solution - Salesforce Dashboard Automation

## 🎯 What Works Right Now

Your dashboard is **90% automated** with a simple manual step:

### Complete Flow:

```
1. Run export script                    [ONE COMMAND]
2. Browser opens to report page         [AUTOMATIC]
3. Log in if needed                     [ONE-TIME]
4. Click: Dropdown → Export             [2 CLICKS]
5. Select: Details Only + CSV format    [2 SELECTIONS]
6. Click: Export button                 [1 CLICK]
7. File downloads                       [AUTOMATIC]
8. File renamed to report*.csv          [AUTOMATIC]
9. Watcher detects & uploads            [AUTOMATIC - 2 seconds]
10. Dashboard updates                   [AUTOMATIC]
11. File archived                       [AUTOMATIC]
```

**Manual work**: 5 clicks (steps 4-6)  
**Automation**: Everything else  
**Time saved**: ~2 minutes per export

---

## 🚀 How to Use

### Start Services (Once):
```bash
cd ~/salesforce-opportunity-tool
./start_all.sh
```

This starts:
- ✅ Dashboard at http://localhost:5001
- ✅ Auto-upload watcher

### Run Export (When you need fresh data):
```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_export_final.py
```

**What to do when browser opens:**
1. Log in if prompted (usually only first time)
2. Wait for report page to load
3. Click the dropdown (▼) next to "Edit"
4. Click "Export" in the menu
5. In dialog: Select "Details Only"
6. In dialog: Select "Comma Delimited .csv" format
7. Click blue "Export" button

**Then sit back** - the script:
- Detects the download
- Renames it to `report*.csv`
- Watcher uploads it (within 2 seconds)
- Dashboard updates automatically
- File gets archived

---

## 📊 View Your Dashboard

Open: **http://localhost:5001**

You'll see:
- Total projects: 494
- Excluded from billing: 64
- Holdback projects: 134
- Framework projects: 149
- Umbrella projects: 59
- Regional breakdowns
- Charts and filters

---

## 🔍 Check Status

```bash
cd ~/salesforce-opportunity-tool
./status.sh
```

Shows:
- Dashboard status
- Watcher status
- Recent uploads
- Project counts

---

## 🛑 Stop Services

```bash
cd ~/salesforce-opportunity-tool
./stop_all.sh
```

---

## ⚙️ Files Reference

| File | Purpose |
|------|---------|
| `start_all.sh` | Start dashboard + watcher |
| `stop_all.sh` | Stop all services |
| `status.sh` | Check what's running |
| `auto_export_final.py` | Export automation script |
| `app.py` | Dashboard backend |
| `auto_upload_watcher.py` | File monitoring service |

---

## 📝 Logs

- Dashboard: `/tmp/salesforce_dashboard.log`
- Watcher: `/tmp/salesforce_watcher.log`

---

## ⚠️ Troubleshooting

### Watcher not uploading?

Check if running:
```bash
ps aux | grep auto_upload_watcher | grep -v grep
```

If multiple instances:
```bash
cd ~/salesforce-opportunity-tool
./stop_all.sh
./start_all.sh
```

### Dashboard not accessible?

```bash
curl -s http://localhost:5001/api/stats
```

If no response, restart:
```bash
cd ~/salesforce-opportunity-tool
./stop_all.sh
./start_all.sh
```

### File not auto-uploading?

Check file name:
```bash
ls ~/Downloads/report*.csv
```

Must be named `report*.csv` for watcher to detect.

### Manual upload:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
curl -X POST -F "file=@/path/to/report.csv" http://localhost:5001/api/upload
```

---

## 🎯 Why This Works

### What We Automated:
✅ Browser launching  
✅ Navigation to report  
✅ Download detection  
✅ File renaming  
✅ Upload to dashboard  
✅ Data processing  
✅ File archiving  

### What's Manual (Because Salesforce is Complex):
❌ Clicking dropdown/Export (Salesforce Lightning UI is difficult to automate)  
❌ Selecting format (Dynamic dialog elements)  

**But these are just 5 clicks - much better than the full manual process!**

---

## 📈 Time Comparison

### Before Automation:
1. Navigate to Salesforce ➔ 30s
2. Find report ➔ 20s
3. Click Export ➔ 10s
4. Select format ➔ 10s
5. Download ➔ 20s
6. Find file ➔ 10s
7. Upload to tool ➔ 30s
8. Wait for processing ➔ 20s
**Total: ~2.5 minutes**

### With Automation:
1. Run script ➔ 5s
2. Make 5 clicks ➔ 20s
3. Everything else automatic ➔ 0s
**Total: ~25 seconds**

**Time saved: 2+ minutes per export!**

---

## ✅ You're Ready!

Your dashboard is now operational with minimal manual work.

**To export fresh data:**
```bash
cd ~/salesforce-opportunity-tool && source venv/bin/activate && python auto_export_final.py
```

Then make your 5 clicks and you're done!

**Dashboard**: http://localhost:5001
