# 🚀 Quick Start - Fully Automated Salesforce Dashboard

## What You Get

✅ **100% Automated** - No manual exports needed  
✅ **Exports every 4 hours** from Salesforce automatically  
✅ **Real-time dashboard** with charts and regional breakdowns  
✅ **Hands-free operation** - Set it and forget it  

---

## Start Everything (One Command)

```bash
cd ~/salesforce-opportunity-tool
./start_scheduled_automation.sh
```

This starts:
- 📅 Export scheduler (runs every 4 hours)
- 📊 Dashboard at http://localhost:5001
- 👀 Auto-upload watcher

---

## First Time Setup

### On First Run:
1. Browser window opens automatically
2. You'll need to log into Salesforce **once**
3. After that, automation runs forever (no more logins)

### What Happens Next:
- Export runs immediately
- Then again every 4 hours
- Dashboard updates automatically
- You don't have to do anything!

---

## View Your Dashboard

Open: **http://localhost:5001**

You'll see:
- Total projects count
- Regional breakdowns
- Special terms (Holdback, Framework, Umbrella)
- Billing status (Excluded/Included)
- Charts and filters

---

## Check Status

```bash
cd ~/salesforce-opportunity-tool
./status.sh
```

---

## Stop Everything

```bash
cd ~/salesforce-opportunity-tool
./stop_all.sh
pkill -f scheduler.py
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `start_scheduled_automation.sh` | Start full automation |
| `start_all.sh` | Start dashboard + watcher only |
| `stop_all.sh` | Stop all services |
| `status.sh` | Check what's running |
| `FULL_AUTOMATION.md` | Complete documentation |
| `auto_export_improved.py` | Browser automation script |
| `scheduler.py` | Runs exports every 4 hours |

---

## Logs Location

- Scheduler: `/tmp/salesforce_scheduler.log`
- Dashboard: `/tmp/salesforce_dashboard.log`
- Watcher: `/tmp/salesforce_watcher.log`

---

## Need Help?

See **[FULL_AUTOMATION.md](FULL_AUTOMATION.md)** for:
- Detailed troubleshooting
- How browser automation works
- Changing export schedule
- Advanced configuration

---

**That's it! Your dashboard is now fully automated! 🎉**
