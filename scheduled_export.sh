#!/bin/bash
# Scheduled Export - Runs export and logs results
# This script is designed to be called by scheduler or cron

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="/tmp/salesforce_scheduled_export.log"

echo "========================================" >> "$LOG_FILE"
echo "$(date): Starting scheduled export" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Activate virtual environment
source venv/bin/activate

# Run export with aggressive automation
python auto_export_aggressive.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date): ✅ Export completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ❌ Export failed with code $EXIT_CODE" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

exit $EXIT_CODE
