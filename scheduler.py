#!/usr/bin/env python3
"""
Scheduler for Salesforce Report Auto-Sync
Runs the sync on a regular schedule
"""

import schedule
import time
import subprocess
import os
from datetime import datetime

# Configuration
SYNC_SCRIPT = os.path.join(os.path.dirname(__file__), "auto_export_final.py")
PYTHON_PATH = os.path.join(os.path.dirname(__file__), "venv/bin/python")

# Schedule configuration
SYNC_INTERVAL_HOURS = 4  # Run every 4 hours
# Or use these alternatives:
# SYNC_INTERVAL_MINUTES = 30  # Run every 30 minutes
# SYNC_TIME_DAILY = "09:00"   # Run daily at 9 AM


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_sync():
    """Run the sync script"""
    log("="*80)
    log("🔄 Starting scheduled sync...")
    log("="*80)

    try:
        # Run the sync script with headless mode
        result = subprocess.run(
            [PYTHON_PATH, SYNC_SCRIPT, '--headless'],
            capture_output=True,
            text=True
        )

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            log("✅ Scheduled sync completed successfully")
        else:
            log(f"❌ Scheduled sync failed with exit code {result.returncode}")
            if result.stderr:
                log(f"Error: {result.stderr}")

    except Exception as e:
        log(f"❌ Error running sync: {e}")


def main():
    """Main scheduler function"""
    log("="*80)
    log("🕐 Salesforce Report Scheduler Started")
    log("="*80)
    log(f"📊 Will sync every {SYNC_INTERVAL_HOURS} hours")
    log(f"📁 Script location: {SYNC_SCRIPT}")
    log(f"🐍 Python: {PYTHON_PATH}")
    log("="*80)
    log("💡 Press Ctrl+C to stop the scheduler")
    log("="*80)

    # Schedule the job
    schedule.every(SYNC_INTERVAL_HOURS).hours.do(run_sync)

    # Alternative scheduling options (uncomment to use):
    # schedule.every(30).minutes.do(run_sync)  # Every 30 minutes
    # schedule.every().day.at("09:00").do(run_sync)  # Daily at 9 AM
    # schedule.every().monday.at("09:00").do(run_sync)  # Weekly on Monday

    # Run once immediately on startup
    log("🚀 Running initial sync now...")
    run_sync()

    # Keep running scheduled jobs
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        log("\n⏹️  Scheduler stopped by user")


if __name__ == "__main__":
    main()
