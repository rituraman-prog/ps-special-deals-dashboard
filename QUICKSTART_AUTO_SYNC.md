# Quick Start: Auto-Sync Setup

Get your dashboard automatically syncing with Salesforce in 3 steps!

---

## Step 1: First-Time Setup (5 minutes)

Run this command and follow the prompts:

```bash
cd ~/salesforce-opportunity-tool
source venv/bin/activate
python auto_sync.py --login
```

**What will happen:**
1. ✅ Browser window opens
2. ✅ You log into Salesforce (just once!)
3. ✅ Report downloads automatically
4. ✅ Dashboard updates
5. ✅ Session saved for future runs

**First run tips:**
- The browser will stay open - this is normal!
- Log in with your regular Salesforce credentials
- If Export button isn't clicked automatically, click it manually:
  - Click dropdown (⚙️) → Export → Export Details → CSV
- Wait for "✅ Sync completed successfully!" message

---

## Step 2: Test Automatic Mode

Make sure it works without you watching:

```bash
python auto_sync.py --headless
```

This should complete in 30-60 seconds. You'll see:
```
✅ Report downloaded
✅ Upload successful!
✅ Sync completed successfully!
```

---

## Step 3: Start Automatic Schedule

Keep this running to sync every 4 hours:

```bash
python scheduler.py
```

**Or use the all-in-one launcher:**
```bash
./start_all.sh
```

This starts both:
- Dashboard (http://localhost:5001)
- Auto-sync scheduler (every 4 hours)

Press `Ctrl+C` to stop both.

---

## ✅ You're Done!

Your dashboard will now:
- 🔄 Auto-refresh every 4 hours
- 📊 Show latest Salesforce data
- 🤖 Run in the background
- 💾 Keep historical data

---

## Quick Commands Reference

```bash
# First time: Setup login
python auto_sync.py --login

# Test: Run sync once
python auto_sync.py --headless

# Schedule: Run every 4 hours
python scheduler.py

# All-in-one: Dashboard + Scheduler
./start_all.sh
```

---

## What's Next?

- [ ] Check Upload History tab to see sync activity
- [ ] Customize sync frequency in `scheduler.py`
- [ ] Set up Slack/email notifications
- [ ] Add billing exception tracking

See **AUTO_SYNC_GUIDE.md** for advanced configuration options.

---

## Need Help?

**Session expired?**
```bash
python auto_sync.py --login
```

**Dashboard not running?**
```bash
python app.py
```

**Check what's happening:**
```bash
tail -f sync.log
```

---

## 🎉 Success Checklist

- [x] Browser automation installed
- [ ] First login completed (`--login`)
- [ ] Test sync works (`--headless`)
- [ ] Scheduler running (`scheduler.py`)
- [ ] Dashboard showing data (http://localhost:5001)
- [ ] Auto-sync working every 4 hours

Complete all items and you're fully automated! 🚀
