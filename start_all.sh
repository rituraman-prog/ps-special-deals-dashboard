#!/bin/bash
# Salesforce Dashboard - Auto-Start Script
# This script starts both the dashboard and auto-upload watcher

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "🚀 Starting Salesforce Dashboard Services"
echo "========================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes
echo "🔄 Stopping existing services..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*auto_upload_watcher.py" 2>/dev/null || true
sleep 2

# Start dashboard
echo "📊 Starting Dashboard on http://localhost:5001..."
nohup python app.py > /tmp/salesforce_dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 3

# Check if dashboard started successfully
if curl -s http://localhost:5001/api/stats > /dev/null 2>&1; then
    echo "   ✅ Dashboard running (PID: $DASHBOARD_PID)"
else
    echo "   ❌ Dashboard failed to start. Check /tmp/salesforce_dashboard.log"
    exit 1
fi

# Start auto-upload watcher
echo "👀 Starting Auto-Upload Watcher..."
nohup python auto_upload_watcher.py > /tmp/salesforce_watcher.log 2>&1 &
WATCHER_PID=$!
sleep 2

# Check if watcher started successfully
if ps -p $WATCHER_PID > /dev/null 2>&1; then
    echo "   ✅ Watcher running (PID: $WATCHER_PID)"
else
    echo "   ❌ Watcher failed to start. Check /tmp/salesforce_watcher.log"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ All Services Started Successfully!"
echo "========================================"
echo ""
echo "📊 Dashboard: http://localhost:5001"
echo "📁 Monitoring: ~/Downloads for report*.csv files"
echo ""
echo "📝 Logs:"
echo "   Dashboard: /tmp/salesforce_dashboard.log"
echo "   Watcher:   /tmp/salesforce_watcher.log"
echo ""
echo "🛑 To stop all services:"
echo "   $SCRIPT_DIR/stop_all.sh"
echo ""
echo "✨ AUTOMATION ACTIVE:"
echo "   1. Export report from Salesforce as CSV"
echo "   2. File downloads to ~/Downloads"
echo "   3. Watcher detects it automatically"
echo "   4. Uploads to dashboard (within 2 seconds)"
echo "   5. Dashboard updates in real-time"
echo "   6. File archived to ~/Downloads/salesforce_archive/"
echo ""
