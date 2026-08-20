# Semi-Automatic Sync Guide

**The easiest way to auto-sync** - you just click "Export" once, everything else is automatic!

---

## 🎯 How It Works

```
1. Script opens browser     → Automatic ✅
2. Navigates to report      → Automatic ✅  
3. YOU CLICK EXPORT         → Manual (2 seconds) 👆
4. Detects download         → Automatic ✅
5. Uploads to dashboard     → Automatic ✅
```

**You do 1 simple action, the script does everything else!**

---

## 🚀 Quick Start

### First Time Setup:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_sync.py --login
```

**What happens:**
1. Browser opens automatically
2. You log into Salesforce (saves your session)
3. Report loads automatically
4. **BIG MESSAGE appears**: "👉 MANUAL STEP REQUIRED"
5. **You click**: Dropdown (⚙️) → Export → Export Details → CSV
6. Download starts automatically
7. Script detects download and uploads to dashboard
8. Done! ✅

---

## ⚡ Future Runs (Even Easier):

After first-time setup, run:

```bash
python auto_sync.py --headless
```

**What happens:**
1. Browser runs in background (you won't see it)
2. Uses your saved login session
3. Navigates to report
4. **Tries to click Export automatically**
5. If successful → downloads and uploads automatically
6. If not → opens visible browser and asks you to click Export

**Most of the time it will be 100% automatic after first run!**

---

## 🕐 Schedule It

Run every 4 hours automatically:

```bash
python scheduler.py
```

**Or all-in-one** (dashboard + scheduler):

```bash
./start_all.sh
```

---

## 💡 Tips

✅ **First run always requires manual export** - that's normal  
✅ **After that, it tries to be fully automatic** - may succeed or may ask for help  
✅ **The script watches for your download** - no rush, take your time  
✅ **90 second timeout** - plenty of time to click Export  
✅ **Browser stays open** - so you can see what's happening  

---

## 📊 What You'll See

### When Manual Export Needed:

```
⚠️  Could not find Export button automatically

================================================================================
👉 MANUAL STEP REQUIRED
================================================================================
Please click the Export button now:
   1. Look for the dropdown menu (⚙️ gear icon or ⋮ three dots)
   2. Click 'Export' or 'Export Details'
   3. Select 'CSV' or 'Formatted Report'
   4. The download will start automatically

⏳ Waiting 90 seconds for you to export...
   (Script will auto-detect the download)
================================================================================

⏳ Monitoring for CSV download (timeout: 90s)...
   Still waiting... (10/90s)
   Still waiting... (20/90s)
✅ Download detected: report.csv
📤 Uploading to dashboard...
✅ Upload successful!
   New records: 5
   Updated records: 487
✅ Sync completed successfully!
```

---

## 🎉 Success!

Once you complete the first run:
- ✅ Your login session is saved
- ✅ Future runs try to be fully automatic
- ✅ If automation fails, you just click one button
- ✅ Everything else is handled for you

**Much easier than manually downloading and uploading CSVs every time!**

---

## ❓ FAQ

**Q: Do I need to click Export every time?**  
A: First time yes. After that, the script tries to click it automatically. If it can't find the button (Salesforce UI changes), it will ask you.

**Q: Can I make it fully automatic?**  
A: Option 1 works for most Salesforce orgs. If not, we can set up email-based sync (100% automatic, no clicking).

**Q: What if I miss the 90 second window?**  
A: Just run the script again! No problem.

**Q: Will this work with the scheduler?**  
A: Yes! The scheduler runs it every 4 hours. If manual export is needed, you'll see a message, but usually after first setup it works automatically.

---

## 🚀 Ready to Try?

Run this now:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_sync.py --login
```

A browser will open. When you see "👉 MANUAL STEP REQUIRED", click Export!

That's it! 🎉
