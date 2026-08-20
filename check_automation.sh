#!/bin/bash
# Check Automation Status - Easy way to see if everything is running

echo "========================================"
echo "🔍 AUTOMATION STATUS CHECK"
echo "========================================"
echo ""

# Check Dashboard
echo "1️⃣  DASHBOARD:"
if curl -s http://localhost:5001/api/stats > /dev/null 2>&1; then
    STATS=$(curl -s http://localhost:5001/api/stats)
    TOTAL=$(echo $STATS | python3 -c "import sys, json; print(json.load(sys.stdin)['total_opportunities'])" 2>/dev/null)
    echo "   ✅ RUNNING"
    echo "   🌐 http://localhost:5001"
    echo "   📊 Tracking: $TOTAL projects"
else
    echo "   ❌ NOT RUNNING"
fi

echo ""

# Check Watcher
echo "2️⃣  AUTO-UPLOAD WATCHER:"
if pgrep -f "auto_upload_watcher.py" > /dev/null 2>&1; then
    PID=$(pgrep -f "auto_upload_watcher.py" | head -1)
    echo "   ✅ RUNNING (PID: $PID)"
    echo "   📁 Monitoring: ~/Downloads for report*.csv files"
else
    echo "   ❌ NOT RUNNING"
fi

echo ""

# Check Scheduler
echo "3️⃣  EXPORT SCHEDULER:"
if pgrep -f "auto_scheduler.py" > /dev/null 2>&1; then
    PID=$(pgrep -f "auto_scheduler.py" | head -1)
    echo "   ✅ RUNNING (PID: $PID)"
    echo "   📅 Auto-exports every 4 hours"

    # Check when last export ran
    if [ -f /tmp/salesforce_scheduler.log ]; then
        LAST_EXPORT=$(tail -50 /tmp/salesforce_scheduler.log | grep "EXPORT COMPLETED\|EXPORT STARTING" | tail -1)
        if [ -n "$LAST_EXPORT" ]; then
            echo "   📝 Last activity: $(echo $LAST_EXPORT | cut -d']' -f1 | cut -d'[' -f2)"
        fi
    fi
else
    echo "   ❌ NOT RUNNING"
fi

echo ""
echo "========================================"
echo ""

# Summary
DASH_OK=$(curl -s http://localhost:5001/api/stats > /dev/null 2>&1 && echo "YES" || echo "NO")
WATCH_OK=$(pgrep -f "auto_upload_watcher.py" > /dev/null 2>&1 && echo "YES" || echo "NO")
SCHED_OK=$(pgrep -f "auto_scheduler.py" > /dev/null 2>&1 && echo "YES" || echo "NO")

if [ "$DASH_OK" = "YES" ] && [ "$WATCH_OK" = "YES" ] && [ "$SCHED_OK" = "YES" ]; then
    echo "✅ FULL AUTOMATION ACTIVE!"
    echo ""
    echo "Your dashboard will auto-refresh every 4 hours."
    echo "You can close this terminal - services keep running."
    echo ""
elif [ "$DASH_OK" = "YES" ] && [ "$WATCH_OK" = "YES" ]; then
    echo "⚠️  PARTIAL AUTOMATION"
    echo ""
    echo "Dashboard and watcher are running, but scheduler is not."
    echo "Data won't auto-refresh. Start scheduler:"
    echo "   cd ~/salesforce-opportunity-tool && ./start_full_automation.sh"
    echo ""
else
    echo "❌ AUTOMATION NOT RUNNING"
    echo ""
    echo "Start full automation:"
    echo "   cd ~/salesforce-opportunity-tool && ./start_full_automation.sh"
    echo ""
fi

echo "📝 View logs:"
echo "   Dashboard:  tail -f /tmp/salesforce_dashboard.log"
echo "   Watcher:    tail -f /tmp/salesforce_watcher.log"
echo "   Scheduler:  tail -f /tmp/salesforce_scheduler.log"
echo ""
