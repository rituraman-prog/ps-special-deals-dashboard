"""
Sync Local Data to Cloud Database
This script runs on your Mac and syncs data to Render PostgreSQL
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import time
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CloudSync:
    """Sync local data to cloud PostgreSQL database"""

    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = None

    def connect(self):
        """Connect to cloud PostgreSQL database"""
        try:
            result = urlparse(self.database_url)

            self.conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )

            logger.info("✅ Connected to cloud database")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to cloud database: {str(e)}")
            return False

    def sync_csv_file(self, csv_path):
        """Sync a CSV file to cloud database"""
        try:
            logger.info(f"📤 Syncing file: {csv_path}")

            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"📊 Read {len(df)} records from CSV")

            if len(df) == 0:
                logger.warning("⚠️ CSV file is empty, skipping")
                return False

            # Process the data (same as app.py process_csv)
            df = self.process_dataframe(df)

            # Clear existing data
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM opportunities')
            logger.info("🗑️ Cleared existing data")

            # Prepare data for bulk insert
            columns = list(df.columns)
            values = [tuple(row) for row in df.values]

            # Bulk insert
            query = f"""
                INSERT INTO opportunities ({', '.join(columns)})
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])}
            """

            execute_values(cursor, query, values)

            # Add to upload history
            cursor.execute('''
                INSERT INTO upload_history (filename, upload_date, records_count, status)
                VALUES (%s, %s, %s, %s)
            ''', (os.path.basename(csv_path), datetime.now().isoformat(), len(df), 'success'))

            self.conn.commit()
            logger.info(f"✅ Successfully synced {len(df)} records to cloud")

            return True

        except Exception as e:
            logger.error(f"❌ Error syncing file: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False

    def process_dataframe(self, df):
        """Process DataFrame (same logic as app.py)"""
        # Rename columns to match database schema
        column_mapping = {
            'Opportunity ID': 'id',
            'Opportunity Name': 'name',
            'Account Name': 'account_name',
            'Amount': 'amount',
            'Close Date': 'close_date',
            'Stage': 'stage_name',
            'Opportunity Owner': 'owner_name',
            'Type': 'opportunity_type',
            'Created Date': 'created_date',
            'Last Modified Date': 'last_modified_date',
            'Project Manager (Primary)': 'project_manager',
            'Project Manager': 'project_manager_2',
            'Opportunity Owner Full Name': 'opportunity_owner',
            'Region': 'region',
            'Sub-Region': 'subregion',
            'Special Term': 'special_term',
            'Billing Frequency': 'billing_frequency',
            'Account Number': 'account_number',
            'Amount Currency': 'amount_currency',
            'Opportunity Stage': 'opportunity_stage',
            'Billings (Currency)': 'billings_currency',
            'Billings': 'billings',
            'Actual Remaining (Currency)': 'actual_remaining_currency',
            'Actual Remaining': 'actual_remaining',
            'Invoiced (Currency)': 'invoiced_currency',
            'Invoiced': 'invoiced',
            'PO Number': 'po_number',
            'Exclude from Billing': 'exclude_from_billing'
        }

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Add upload metadata
        df['upload_date'] = datetime.now().isoformat()
        df['upload_filename'] = 'cloud_sync'

        # Convert exclude_from_billing to integer
        if 'exclude_from_billing' in df.columns:
            df['exclude_from_billing'] = df['exclude_from_billing'].fillna(False).astype(int)

        # Fill NaN values
        df = df.fillna('')

        # Ensure we have all required columns
        required_columns = [
            'id', 'name', 'account_name', 'amount', 'close_date', 'stage_name',
            'owner_name', 'opportunity_type', 'created_date', 'last_modified_date',
            'upload_date', 'upload_filename', 'project_manager', 'project_manager_2',
            'opportunity_owner', 'region', 'subregion', 'special_term',
            'billing_frequency', 'account_number', 'amount_currency',
            'opportunity_stage', 'billings_currency', 'billings',
            'actual_remaining_currency', 'actual_remaining', 'invoiced_currency',
            'invoiced', 'po_number', 'exclude_from_billing'
        ]

        for col in required_columns:
            if col not in df.columns:
                df[col] = ''

        return df[required_columns]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Disconnected from cloud database")


def sync_from_local_db(database_url, local_db_path='data/opportunities.db'):
    """Sync from local SQLite database to cloud PostgreSQL"""
    import sqlite3

    logger.info("🔄 Starting sync from local database to cloud...")

    sync = CloudSync(database_url)

    if not sync.connect():
        logger.error("❌ Cannot connect to cloud database")
        return False

    try:
        # Read from local SQLite
        local_conn = sqlite3.connect(local_db_path)
        local_conn.row_factory = sqlite3.Row

        cursor = local_conn.cursor()
        cursor.execute('SELECT * FROM opportunities')
        rows = cursor.fetchall()

        if len(rows) == 0:
            logger.warning("⚠️ No data in local database")
            local_conn.close()
            sync.close()
            return False

        logger.info(f"📊 Found {len(rows)} records in local database")

        # Convert to DataFrame
        df = pd.DataFrame([dict(row) for row in rows])

        # Clear cloud database
        cloud_cursor = sync.conn.cursor()
        cloud_cursor.execute('DELETE FROM opportunities')

        # Prepare data for bulk insert
        columns = list(df.columns)
        values = [tuple(row) for row in df.values]

        # Bulk insert to cloud
        query = f"""
            INSERT INTO opportunities ({', '.join(columns)})
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
            {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])}
        """

        execute_values(cloud_cursor, query, values)

        # Add to upload history
        cloud_cursor.execute('''
            INSERT INTO upload_history (filename, upload_date, records_count, status)
            VALUES (%s, %s, %s, %s)
        ''', ('local_sync', datetime.now().isoformat(), len(df), 'success'))

        sync.conn.commit()

        logger.info(f"✅ Successfully synced {len(df)} records to cloud")

        local_conn.close()
        sync.close()

        return True

    except Exception as e:
        logger.error(f"❌ Error during sync: {str(e)}")
        if sync.conn:
            sync.conn.rollback()
        sync.close()
        return False


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("❌ Usage: python sync_to_cloud.py <DATABASE_URL>")
        print("")
        print("Example:")
        print("  python sync_to_cloud.py 'postgresql://user:pass@host:5432/dbname'")
        sys.exit(1)

    database_url = sys.argv[1]

    # Sync from local database
    success = sync_from_local_db(database_url)

    if success:
        logger.info("🎉 Sync completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Sync failed")
        sys.exit(1)
