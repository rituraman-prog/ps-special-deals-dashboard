#!/bin/bash
# Check status of Salesforce Dashboard services

echo "========================================"
echo "📊 Salesforce Dashboard - Service Status"
echo "========================================"
echo ""

# Check dashboard
DASHBOARD_PID=$(pgrep -f "python.*app.py")
if [ -n "$DASHBOARD_PID" ]; then
    echo "Dashboard:  ✅ RUNNING (PID: $DASHBOARD_PID)"

    # Try to get stats
    if STATS=$(curl -s http://localhost:5001/api/stats 2>/dev/null); then
        TOTAL=$(echo $STATS | python3 -c "import sys, json; print(json.load(sys.stdin)['total_opportunities'])" 2>/dev/null)
        EXCLUDED=$(echo $STATS | python3 -c "import sys, json; print(json.load(sys.stdin)['excluded_count'])" 2>/dev/null)
        echo "            📊 http://localhost:5001"
        echo "            Projects: $TOTAL"
        echo "            Excluded: $EXCLUDED"
    fi
else
    echo "Dashboard:  ❌ NOT RUNNING"
fi

echo ""

# Check watcher
WATCHER_PID=$(pgrep -f "python.*auto_upload_watcher")
if [ -n "$WATCHER_PID" ]; then
    echo "Watcher:    ✅ RUNNING (PID: $WATCHER_PID)"
    echo "            📁 Monitoring ~/Downloads"
else
    echo "Watcher:    ❌ NOT RUNNING"
fi

echo ""
echo "========================================"
echo ""

# Show recent uploads
if [ -n "$DASHBOARD_PID" ]; then
    echo "Recent uploads:"
    curl -s http://localhost:5001/api/upload-history 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data[:3]:
        print(f\"  • {item['filename']} - {item['records_count']} records\")
except:
    print('  (Unable to fetch history)')
" 2>/dev/null
    echo ""
fi

# Check if services need to be started
if [ -z "$DASHBOARD_PID" ] || [ -z "$WATCHER_PID" ]; then
    echo "💡 To start services, run:"
    echo "   cd ~/salesforce-opportunity-tool && ./start_all.sh"
    echo ""
fi
