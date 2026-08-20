"""
Salesforce API Data Sync
Replaces browser automation with direct API access
"""

import os
import pandas as pd
from datetime import datetime
from simple_salesforce import Salesforce
from dotenv import load_dotenv
import sqlite3
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SalesforceSync:
    """Sync Professional Services data from Salesforce using API"""

    def __init__(self):
        self.username = os.getenv('SALESFORCE_USERNAME')
        self.password = os.getenv('SALESFORCE_PASSWORD')
        self.security_token = os.getenv('SALESFORCE_TOKEN')
        self.domain = os.getenv('SALESFORCE_DOMAIN', 'login')
        self.sf = None

    def connect(self):
        """Connect to Salesforce"""
        try:
            logger.info("Connecting to Salesforce...")
            self.sf = Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                domain=self.domain
            )
            logger.info("✅ Connected to Salesforce successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Salesforce: {str(e)}")
            return False

    def fetch_opportunities(self):
        """Fetch opportunities with special terms from Salesforce"""
        if not self.sf:
            if not self.connect():
                return None

        try:
            logger.info("Fetching opportunities from Salesforce...")

            # SOQL query to fetch PSA projects with special terms
            query = """
                SELECT
                    Id,
                    Name,
                    Account.Name,
                    Amount,
                    CloseDate,
                    StageName,
                    Owner.Name,
                    Type,
                    CreatedDate,
                    LastModifiedDate,
                    pse__Region__c,
                    pse__Primary_Project_Manager__r.Name,
                    pse__Project_Manager__r.Name,
                    Special_Term__c,
                    Billing_Frequency__c,
                    Account.AccountNumber,
                    CurrencyIsoCode,
                    pse__Billings__c,
                    pse__Invoiced__c,
                    PO_Number__c,
                    Exclude_from_Billing__c
                FROM Opportunity
                WHERE pse__Is_Change_Request__c = false
                AND Special_Term__c != null
                AND StageName IN ('06 - Project Booked', 'Closed Won', 'Booked')
                ORDER BY CloseDate DESC
            """

            results = self.sf.query_all(query)
            logger.info(f"✅ Fetched {results['totalSize']} opportunities")

            # Convert to DataFrame
            records = results['records']

            # Process records
            data = []
            for rec in records:
                data.append({
                    'id': rec.get('Id'),
                    'name': rec.get('Name'),
                    'account_name': rec.get('Account', {}).get('Name') if rec.get('Account') else None,
                    'amount': rec.get('Amount'),
                    'close_date': rec.get('CloseDate'),
                    'stage_name': rec.get('StageName'),
                    'owner_name': rec.get('Owner', {}).get('Name') if rec.get('Owner') else None,
                    'opportunity_type': rec.get('Type'),
                    'created_date': rec.get('CreatedDate'),
                    'last_modified_date': rec.get('LastModifiedDate'),
                    'region': rec.get('pse__Region__c'),
                    'project_manager': rec.get('pse__Primary_Project_Manager__r', {}).get('Name') if rec.get('pse__Primary_Project_Manager__r') else None,
                    'project_manager_2': rec.get('pse__Project_Manager__r', {}).get('Name') if rec.get('pse__Project_Manager__r') else None,
                    'special_term': rec.get('Special_Term__c'),
                    'billing_frequency': rec.get('Billing_Frequency__c'),
                    'account_number': rec.get('Account', {}).get('AccountNumber') if rec.get('Account') else None,
                    'amount_currency': rec.get('CurrencyIsoCode'),
                    'billings': rec.get('pse__Billings__c'),
                    'invoiced': rec.get('pse__Invoiced__c'),
                    'po_number': rec.get('PO_Number__c'),
                    'exclude_from_billing': 1 if rec.get('Exclude_from_Billing__c') else 0
                })

            df = pd.DataFrame(data)
            logger.info(f"✅ Processed {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"❌ Error fetching opportunities: {str(e)}")
            return None

    def save_to_database(self, df):
        """Save opportunities to SQLite database"""
        if df is None or len(df) == 0:
            logger.warning("No data to save")
            return False

        try:
            logger.info("Saving to database...")
            conn = sqlite3.connect('data/opportunities.db')

            # Clear existing data
            conn.execute('DELETE FROM opportunities')

            # Insert new data
            df.to_sql('opportunities', conn, if_exists='append', index=False)

            # Update upload history
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO upload_history (filename, upload_date, records_count, status)
                VALUES (?, ?, ?, ?)
            ''', ('salesforce_api_sync', datetime.now().isoformat(), len(df), 'success'))

            conn.commit()
            conn.close()

            logger.info(f"✅ Saved {len(df)} records to database")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving to database: {str(e)}")
            return False

    def sync(self):
        """Full sync: fetch from Salesforce and save to database"""
        logger.info("🚀 Starting Salesforce sync...")

        df = self.fetch_opportunities()
        if df is not None:
            if self.save_to_database(df):
                logger.info("✅ Sync completed successfully")
                return True

        logger.error("❌ Sync failed")
        return False


def run_sync():
    """Main function to run sync"""
    sync = SalesforceSync()
    return sync.sync()


if __name__ == '__main__':
    # Run sync
    success = run_sync()
    exit(0 if success else 1)
