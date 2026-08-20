#!/bin/bash
# Stop all Salesforce Dashboard services

echo "🛑 Stopping Salesforce Dashboard Services..."
echo ""

# Stop dashboard
if pkill -f "python.*app.py" 2>/dev/null; then
    echo "   ✅ Dashboard stopped"
else
    echo "   ℹ️  Dashboard was not running"
fi

# Stop watcher
if pkill -f "python.*auto_upload_watcher.py" 2>/dev/null; then
    echo "   ✅ Watcher stopped"
else
    echo "   ℹ️  Watcher was not running"
fi

echo ""
echo "✅ All services stopped"
