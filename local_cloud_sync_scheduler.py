"""
Local Cloud Sync Scheduler
Runs on your Mac and syncs data to cloud every 4 hours
"""

import os
import schedule
import time
import logging
from datetime import datetime
from sync_to_cloud import sync_from_local_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cloud_sync_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def scheduled_sync():
    """Run scheduled sync to cloud"""
    logger.info("=" * 60)
    logger.info(f"⏰ Scheduled cloud sync starting at {datetime.now()}")
    logger.info("=" * 60)

    # Get DATABASE_URL from environment
    database_url = os.environ.get('CLOUD_DATABASE_URL')

    if not database_url:
        logger.error("❌ CLOUD_DATABASE_URL not set in environment!")
        logger.error("Please set it with:")
        logger.error("  export CLOUD_DATABASE_URL='your-postgres-url'")
        return

    try:
        # Check if local database exists
        local_db_path = 'data/opportunities.db'

        if not os.path.exists(local_db_path):
            logger.warning(f"⚠️ Local database not found at: {local_db_path}")
            logger.info("Waiting for browser automation to create data...")
            return

        # Sync to cloud
        success = sync_from_local_db(database_url, local_db_path)

        if success:
            logger.info("✅ Scheduled cloud sync completed successfully")
        else:
            logger.error("❌ Scheduled cloud sync failed")

    except Exception as e:
        logger.error(f"❌ Scheduled cloud sync error: {str(e)}")

    logger.info("=" * 60)


def main():
    """Main scheduler loop"""
    logger.info("🚀 Local Cloud Sync Scheduler started")
    logger.info("=" * 60)

    # Check for DATABASE_URL
    database_url = os.environ.get('CLOUD_DATABASE_URL')

    if not database_url:
        logger.error("❌ CLOUD_DATABASE_URL environment variable not set!")
        logger.error("")
        logger.error("To set it, run:")
        logger.error("  export CLOUD_DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        logger.error("")
        logger.error("Get the URL from Render.com:")
        logger.error("  1. Go to your PostgreSQL database in Render")
        logger.error("  2. Copy the 'Internal Database URL'")
        logger.error("  3. Set it as CLOUD_DATABASE_URL")
        logger.error("")
        return

    logger.info(f"✅ Cloud database URL configured")
    logger.info(f"📅 Schedule: Sync every 4 hours")
    logger.info("=" * 60)

    # Run immediately on startup
    logger.info("🔄 Running initial sync...")
    scheduled_sync()

    # Schedule every 4 hours
    schedule.every(4).hours.do(scheduled_sync)

    # Alternative schedules (uncomment to use):
    # schedule.every(1).hour.do(scheduled_sync)        # Every 1 hour
    # schedule.every(30).minutes.do(scheduled_sync)    # Every 30 minutes

    logger.info("✅ Scheduler is running. Press Ctrl+C to stop.")
    logger.info("=" * 60)

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
