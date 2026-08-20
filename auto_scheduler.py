#!/usr/bin/env python3
"""
Auto Scheduler - Runs Salesforce exports automatically every X hours
Fully automated data refresh
"""

import schedule
import time
import subprocess
import os
from datetime import datetime

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_SCRIPT = os.path.join(SCRIPT_DIR, "auto_export_aggressive.py")
PYTHON_PATH = os.path.join(SCRIPT_DIR, "venv/bin/python")

# Schedule: Run every 4 hours (change as needed)
INTERVAL_HOURS = 4

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_export():
    """Run the export script"""
    log("="*80)
    log("🔄 SCHEDULED EXPORT STARTING")
    log("="*80)

    try:
        # Run export script
        result = subprocess.run(
            [PYTHON_PATH, EXPORT_SCRIPT],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        # Log output
        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            log("="*80)
            log("✅ SCHEDULED EXPORT COMPLETED")
            log("="*80)
            return True
        else:
            log("="*80)
            log(f"⚠️  EXPORT FAILED (exit code: {result.returncode})")
            log("="*80)
            if result.stderr:
                log(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        log("❌ Export timed out after 10 minutes")
        return False
    except Exception as e:
        log(f"❌ Error running export: {e}")
        return False


def main():
    log("="*80)
    log("🤖 SALESFORCE AUTO SCHEDULER")
    log("="*80)
    log(f"📅 Schedule: Every {INTERVAL_HOURS} hours")
    log(f"📁 Script: {EXPORT_SCRIPT}")
    log(f"🐍 Python: {PYTHON_PATH}")
    log("")
    log("📊 Dashboard auto-refreshes with latest data")
    log("💡 Press Ctrl+C to stop scheduler")
    log("="*80)
    log("")

    # Schedule the export
    schedule.every(INTERVAL_HOURS).hours.do(run_export)

    # Alternative schedules (uncomment to use):
    # schedule.every(30).minutes.do(run_export)  # Every 30 minutes
    # schedule.every().day.at("09:00").do(run_export)  # Daily at 9 AM
    # schedule.every().monday.at("09:00").do(run_export)  # Weekly on Monday

    # Run immediately on startup
    log("🚀 Running initial export now...")
    log("")
    run_export()

    log("")
    log(f"⏰ Next export scheduled in {INTERVAL_HOURS} hours")
    log("")

    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        log("")
        log("🛑 Scheduler stopped by user")
        log("="*80)


if __name__ == "__main__":
    main()
