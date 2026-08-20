"""
Cloud Scheduler - Runs Salesforce sync periodically
Works on Render.com and other cloud platforms
"""

import schedule
import time
import logging
from datetime import datetime
from salesforce_sync import run_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scheduled_sync():
    """Run scheduled sync"""
    logger.info("=" * 60)
    logger.info(f"⏰ Scheduled sync starting at {datetime.now()}")
    logger.info("=" * 60)

    try:
        success = run_sync()
        if success:
            logger.info("✅ Scheduled sync completed successfully")
        else:
            logger.error("❌ Scheduled sync failed")
    except Exception as e:
        logger.error(f"❌ Scheduled sync error: {str(e)}")

    logger.info("=" * 60)


def main():
    """Main scheduler loop"""
    logger.info("🚀 Cloud Scheduler started")
    logger.info("📅 Schedule: Every 4 hours")

    # Run immediately on startup
    logger.info("🔄 Running initial sync...")
    scheduled_sync()

    # Schedule every 4 hours
    schedule.every(4).hours.do(scheduled_sync)

    # Alternative schedules (uncomment to use):
    # schedule.every(1).hour.do(scheduled_sync)        # Every 1 hour
    # schedule.every(30).minutes.do(scheduled_sync)    # Every 30 minutes
    # schedule.every().day.at("09:00").do(scheduled_sync)  # Daily at 9 AM

    logger.info("✅ Scheduler is running. Press Ctrl+C to stop.")

    # Keep running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}")
            time.sleep(60)


if __name__ == '__main__':
    main()
