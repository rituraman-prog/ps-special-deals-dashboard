# 🤖 How Full Automation Works - Simple Explanation

## ✅ What "Leave It Running" Means

### Right Now, You Have 3 Services Running in the Background:

1. **Dashboard** - Shows your data at http://localhost:5001
2. **Watcher** - Monitors ~/Downloads for new report files
3. **Scheduler** - Runs exports every 4 hours automatically

**These are "background processes"** - like having apps running on your computer:
- They work even when you close the terminal
- They keep running until you stop them or restart your computer
- You can use your computer normally - they don't interfere

### Think of it like:
- **Email app** - Always running, checks for new mail automatically
- **Dropbox** - Always running, syncs files in background
- **Your Dashboard** - Always running, refreshes data every 4 hours

---

## 🔄 How Data Gets Updated

### Current State:
- **Projects tracked**: 494
- **Last data**: From the last Salesforce export

### What Happens Every 4 Hours:

```
Hour 0 (Now):
- Dashboard shows: 494 projects ✅

Hour 4 (4 hours later):
1. ⏰ Scheduler wakes up
2. 🌐 Opens browser to Salesforce report
3. 🤖 Attempts to click Export automatically
4. 📥 Downloads LATEST data from Salesforce
5. 📝 File renamed to report*.csv
6. 👀 Watcher detects it (2 seconds)
7. 📤 Uploads to dashboard
8. 📊 Dashboard now shows: 500 projects ✅ (if 6 new ones added)
9. 📁 File archived

Hour 8 (8 hours later):
- Same process repeats
- Gets even newer data
```

### Example Timeline:

**Monday 10:00 AM** - You start automation
- Dashboard: 494 projects

**Monday 2:00 PM** - First auto-refresh (4 hours later)
- New export runs
- Dashboard: 498 projects (4 new projects added in Salesforce)

**Monday 6:00 PM** - Second auto-refresh
- Another export runs
- Dashboard: 503 projects (5 more added)

**Tuesday 10:00 AM** - Continues...
- Dashboard: 515 projects (keeps growing as projects are added)

---

## 🎯 To Answer Your Questions:

### 1. "What does 'leave it running' mean?"

**Answer**: The services are already running in the background. You don't need to:
- Keep a terminal window open
- Run any commands again
- Do anything manually

**Just like how:**
- Your WiFi stays connected in the background
- Your clock keeps updating automatically
- Your antivirus keeps scanning

**Your dashboard keeps refreshing automatically!**

### 2. "How do I leave it running?"

**Answer**: **It's already running!** You don't need to do anything.

The services will keep running until:
- You stop them: `./stop_full_automation.sh`
- You restart your computer (then run `./start_full_automation.sh` again)
- Your computer goes to sleep for a long time

### 3. "Will report numbers update with new entries?"

**Answer**: **YES! Absolutely!**

Every 4 hours:
- Scheduler downloads **FRESH DATA** from Salesforce
- If Salesforce report has 500 projects, dashboard will show 500
- If Salesforce report has 600 projects next time, dashboard will show 600
- Numbers automatically increase/decrease based on Salesforce

**Old data is replaced with new data each time!**

---

## 🔍 How to Check if It's Running

### Easy Way (Run this anytime):

```bash
cd ~/salesforce-opportunity-tool
./check_automation.sh
```

**You'll see:**
```
✅ FULL AUTOMATION ACTIVE!

Your dashboard will auto-refresh every 4 hours.
You can close this terminal - services keep running.
```

---

## 📋 What Happens After You Close This Terminal?

### When you close terminal:
- ✅ Dashboard keeps running (http://localhost:5001)
- ✅ Watcher keeps monitoring ~/Downloads
- ✅ Scheduler keeps running exports every 4 hours

### You can:
- ✅ Close all terminal windows
- ✅ Use your computer normally
- ✅ Open browser anytime to view dashboard
- ✅ Come back tomorrow - still running!

### Services stop only if:
- ❌ You run `./stop_full_automation.sh`
- ❌ Computer restarts
- ❌ Computer sleeps for very long time (some systems)

---

## 🖥️ When Browser Opens (Every 4 Hours)

### First Time:
- Browser opens
- You may need to log in to Salesforce
- Automation tries to click Export
- If it works: File downloads automatically ✅
- If it doesn't: Just make 5 clicks (dropdown → Export → Details → CSV → Export)

### After First Time:
- Usually stays logged in
- Automation works better
- Less likely to need manual clicks
- Happens in background

**You might see browser window open briefly every 4 hours** - that's normal! It's the scheduler working.

---

## 📊 Example: Watching Your Dashboard Grow

### Day 1 - Monday 10:00 AM:
Start automation:
```bash
./start_full_automation.sh
```
Dashboard shows: **494 projects**

### Day 1 - Monday 2:00 PM:
Auto-refresh happens (you might see browser flash)
Dashboard now shows: **498 projects** (4 new)

### Day 1 - Monday 6:00 PM:
Auto-refresh happens again
Dashboard now shows: **502 projects** (4 more new)

### Day 2 - Tuesday 10:00 AM:
You check dashboard
Dashboard now shows: **515 projects** (kept refreshing overnight!)

### Day 7 - Next Monday:
Dashboard shows: **580 projects** (grew all week automatically!)

---

## 🎯 Quick Reference

### Check if running:
```bash
cd ~/salesforce-opportunity-tool
./check_automation.sh
```

### View dashboard:
```
Open in browser: http://localhost:5001
```

### Stop automation:
```bash
cd ~/salesforce-opportunity-tool
./stop_full_automation.sh
```

### Start automation again:
```bash
cd ~/salesforce-opportunity-tool
./start_full_automation.sh
```

### After computer restart:
```bash
cd ~/salesforce-opportunity-tool
./start_full_automation.sh
```

---

## ✅ Summary

**Yes, your dashboard automatically updates with new data from Salesforce!**

✅ **Runs in background** - No need to keep terminal open
✅ **Updates every 4 hours** - Gets fresh data from Salesforce  
✅ **Project count grows** - As new projects added in Salesforce  
✅ **Fully automatic** - You don't need to do anything  
✅ **Close terminal** - Services keep running  
✅ **Check anytime** - `./check_automation.sh`  

**Your dashboard is now self-updating! 🎉**
