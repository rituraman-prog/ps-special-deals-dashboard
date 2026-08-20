#!/bin/bash
# Start Full Automation - Dashboard + Watcher + Scheduled Exports
# Data refreshes automatically every 4 hours

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "🤖 STARTING FULL AUTOMATION"
echo "========================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Stop any existing processes
echo "🔄 Stopping existing services..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*auto_upload_watcher.py" 2>/dev/null || true
pkill -f "python.*auto_scheduler.py" 2>/dev/null || true
pkill -f "python.*scheduler.py" 2>/dev/null || true
sleep 3

# 1. Start Dashboard
echo "📊 Starting Dashboard..."
nohup python app.py > /tmp/salesforce_dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 3

if curl -s http://localhost:5001/api/stats > /dev/null 2>&1; then
    echo "   ✅ Dashboard running (PID: $DASHBOARD_PID)"
    echo "   🌐 http://localhost:5001"
else
    echo "   ❌ Dashboard failed to start"
    echo "   Check: /tmp/salesforce_dashboard.log"
    exit 1
fi

# 2. Start Auto-Upload Watcher
echo "👀 Starting Auto-Upload Watcher..."
nohup python auto_upload_watcher.py > /tmp/salesforce_watcher.log 2>&1 &
WATCHER_PID=$!
sleep 2

if ps -p $WATCHER_PID > /dev/null 2>&1; then
    echo "   ✅ Watcher running (PID: $WATCHER_PID)"
else
    echo "   ❌ Watcher failed to start"
    exit 1
fi

# 3. Start Auto Scheduler
echo "📅 Starting Export Scheduler..."
nohup python auto_scheduler.py > /tmp/salesforce_scheduler.log 2>&1 &
SCHEDULER_PID=$!
sleep 3

if ps -p $SCHEDULER_PID > /dev/null 2>&1; then
    echo "   ✅ Scheduler running (PID: $SCHEDULER_PID)"
else
    echo "   ❌ Scheduler failed to start"
    echo "   Check: /tmp/salesforce_scheduler.log"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ FULL AUTOMATION ACTIVE!"
echo "========================================"
echo ""
echo "📊 Dashboard: http://localhost:5001"
echo "📁 Monitoring: ~/Downloads"
echo "📅 Auto-export: Every 4 hours"
echo ""
echo "📝 Logs:"
echo "   Dashboard:  /tmp/salesforce_dashboard.log"
echo "   Watcher:    /tmp/salesforce_watcher.log"
echo "   Scheduler:  /tmp/salesforce_scheduler.log"
echo ""
echo "🛑 To stop all services:"
echo "   $SCRIPT_DIR/stop_full_automation.sh"
echo ""
echo "✨ YOUR DASHBOARD NOW AUTO-REFRESHES!"
echo ""
echo "How it works:"
echo "   1. Every 4 hours, browser opens automatically"
echo "   2. Export runs (may need occasional login)"
echo "   3. File downloads and uploads automatically"
echo "   4. Dashboard refreshes with latest data"
echo "   5. File archived"
echo ""
echo "📺 First export starting now..."
echo "   Watch for browser window to open"
echo ""
