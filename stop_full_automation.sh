#!/bin/bash
# Stop Full Automation - All services

echo "🛑 Stopping Full Automation..."
echo ""

# Stop all processes
if pkill -f "python.*app.py" 2>/dev/null; then
    echo "   ✅ Dashboard stopped"
else
    echo "   ℹ️  Dashboard was not running"
fi

if pkill -f "python.*auto_upload_watcher.py" 2>/dev/null; then
    echo "   ✅ Watcher stopped"
else
    echo "   ℹ️  Watcher was not running"
fi

if pkill -f "python.*auto_scheduler.py" 2>/dev/null; then
    echo "   ✅ Scheduler stopped"
else
    echo "   ℹ️  Scheduler was not running"
fi

if pkill -f "python.*scheduler.py" 2>/dev/null; then
    echo "   ✅ Old scheduler stopped"
else
    echo "   ℹ️  Old scheduler was not running"
fi

echo ""
echo "✅ All services stopped"
