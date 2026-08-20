#!/bin/bash
# Start Scheduled Salesforce Export Automation
# This runs the export every 4 hours automatically

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "🤖 Starting Scheduled Automation"
echo "========================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Stop existing scheduler if running
pkill -f "python.*scheduler.py" 2>/dev/null || true
sleep 2

# Start scheduler in background
echo "📅 Starting export scheduler (every 4 hours)..."
nohup python scheduler.py > /tmp/salesforce_scheduler.log 2>&1 &
SCHEDULER_PID=$!
sleep 3

# Check if scheduler started
if ps -p $SCHEDULER_PID > /dev/null 2>&1; then
    echo "   ✅ Scheduler running (PID: $SCHEDULER_PID)"
else
    echo "   ❌ Scheduler failed to start. Check /tmp/salesforce_scheduler.log"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ SCHEDULED AUTOMATION ACTIVE!"
echo "========================================"
echo ""
echo "📅 Export schedule: Every 4 hours"
echo "📁 Downloads to: ~/Downloads"
echo "📊 Dashboard: http://localhost:5001"
echo ""
echo "📝 Logs:"
echo "   Scheduler: /tmp/salesforce_scheduler.log"
echo "   Dashboard: /tmp/salesforce_dashboard.log"
echo "   Watcher:   /tmp/salesforce_watcher.log"
echo ""
echo "🛑 To stop scheduler:"
echo "   pkill -f scheduler.py"
echo ""
echo "✨ FULLY AUTOMATED PIPELINE:"
echo "   1. Scheduler runs export every 4 hours"
echo "   2. Browser automation exports from Salesforce"
echo "   3. File downloads to ~/Downloads"
echo "   4. Watcher detects and uploads (within 2s)"
echo "   5. Dashboard updates automatically"
echo "   6. File archived"
echo ""
echo "💡 First export starting now..."
echo "   Watch the browser window for the export process"
echo ""
