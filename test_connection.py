#!/usr/bin/env python3
"""
Salesforce Connection Test Script
Tests connection to Salesforce and retrieves booked opportunities
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed

# Load environment variables
load_dotenv()


def connect_to_salesforce():
    """
    Establish connection to Salesforce using credentials from .env file
    Returns Salesforce client object or None if connection fails
    """
    try:
        # Get credentials from environment
        username = os.getenv('SF_USERNAME')
        password = os.getenv('SF_PASSWORD')
        security_token = os.getenv('SF_SECURITY_TOKEN')
        domain = os.getenv('SF_DOMAIN', 'login')

        if not all([username, password, security_token]):
            print("❌ Error: Missing Salesforce credentials in .env file")
            print("Please copy .env.example to .env and fill in your credentials")
            return None

        print(f"🔄 Connecting to Salesforce as {username}...")

        # Create Salesforce connection
        sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            domain=domain
        )

        print(f"✅ Successfully connected to Salesforce!")
        print(f"   Instance URL: {sf.sf_instance}")
        print(f"   Session ID: {sf.session_id[:20]}...")

        return sf

    except SalesforceAuthenticationFailed as e:
        print(f"❌ Authentication failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your username and password are correct")
        print("2. Get your security token: Setup → My Personal Information → Reset Security Token")
        print("3. Make sure you're using the correct domain (login vs test)")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def get_booked_opportunities(sf, days_back=30, limit=10):
    """
    Query Salesforce for recently booked (Closed Won) opportunities

    Args:
        sf: Salesforce client object
        days_back: Number of days to look back for closed opportunities
        limit: Maximum number of records to retrieve
    """
    try:
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        print(f"\n🔍 Searching for booked opportunities (Closed Won) since {start_date}...")

        # SOQL query to fetch booked opportunities
        query = f"""
            SELECT
                Id,
                Name,
                AccountId,
                Account.Name,
                Amount,
                CloseDate,
                StageName,
                Owner.Name,
                Type,
                CreatedDate,
                LastModifiedDate
            FROM Opportunity
            WHERE StageName = 'Closed Won'
            AND CloseDate >= {start_date}
            ORDER BY CloseDate DESC
            LIMIT {limit}
        """

        # Execute query
        result = sf.query(query)

        # Display results
        total_records = result['totalSize']
        print(f"\n📊 Found {total_records} booked opportunities")

        if total_records == 0:
            print("\nNo booked opportunities found in the specified date range.")
            print("Try increasing the 'days_back' parameter or check your data in Salesforce.")
            return []

        print("\n" + "="*100)
        print(f"{'Name':<30} {'Account':<25} {'Amount':<15} {'Close Date':<12} {'Owner':<20}")
        print("="*100)

        opportunities = []
        for opp in result['records']:
            # Extract data with safe handling of None values
            name = opp['Name'][:28] if opp.get('Name') else 'N/A'
            account = opp['Account']['Name'][:23] if opp.get('Account') else 'N/A'
            amount = f"${opp['Amount']:,.2f}" if opp.get('Amount') else 'N/A'
            close_date = opp.get('CloseDate', 'N/A')
            owner = opp['Owner']['Name'][:18] if opp.get('Owner') else 'N/A'

            print(f"{name:<30} {account:<25} {amount:<15} {close_date:<12} {owner:<20}")

            opportunities.append({
                'id': opp['Id'],
                'name': opp['Name'],
                'account': opp['Account']['Name'] if opp.get('Account') else None,
                'amount': opp.get('Amount'),
                'close_date': opp.get('CloseDate'),
                'stage': opp.get('StageName'),
                'owner': opp['Owner']['Name'] if opp.get('Owner') else None,
                'type': opp.get('Type'),
                'created_date': opp.get('CreatedDate'),
                'last_modified_date': opp.get('LastModifiedDate')
            })

        print("="*100)

        return opportunities

    except Exception as e:
        print(f"❌ Error querying opportunities: {e}")
        return []


def get_opportunity_details(sf, opp_id):
    """
    Get detailed information for a specific opportunity

    Args:
        sf: Salesforce client object
        opp_id: Salesforce Opportunity ID
    """
    try:
        print(f"\n🔍 Fetching details for opportunity {opp_id}...")

        # Query specific opportunity
        opp = sf.Opportunity.get(opp_id)

        print("\n📋 Opportunity Details:")
        print(f"   ID: {opp['Id']}")
        print(f"   Name: {opp['Name']}")
        print(f"   Stage: {opp['StageName']}")
        print(f"   Amount: ${opp['Amount']:,.2f}" if opp.get('Amount') else "   Amount: N/A")
        print(f"   Close Date: {opp['CloseDate']}")
        print(f"   Created: {opp['CreatedDate']}")
        print(f"   Last Modified: {opp['LastModifiedDate']}")

        return opp

    except Exception as e:
        print(f"❌ Error fetching opportunity details: {e}")
        return None


def main():
    """Main execution function"""
    print("="*100)
    print("🚀 Salesforce Opportunity Tool - Connection Test")
    print("="*100)

    # Connect to Salesforce
    sf = connect_to_salesforce()

    if not sf:
        print("\n❌ Connection test failed. Please check your credentials and try again.")
        return

    # Get booked opportunities
    opportunities = get_booked_opportunities(sf, days_back=90, limit=20)

    if opportunities:
        print(f"\n✅ Successfully retrieved {len(opportunities)} opportunities!")

        # Optional: Get details for the first opportunity
        if len(opportunities) > 0:
            print("\n" + "-"*100)
            first_opp_id = opportunities[0]['id']
            get_opportunity_details(sf, first_opp_id)

    print("\n" + "="*100)
    print("✅ Connection test complete!")
    print("="*100)


if __name__ == "__main__":
    main()
