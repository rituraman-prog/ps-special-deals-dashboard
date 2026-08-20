#!/usr/bin/env python3
"""
Salesforce Report Auto-Sync
Automatically downloads Salesforce reports using browser automation
"""

import os
import time
import glob
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view?queryScope=userFolders"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")  # Use system Downloads folder
DASHBOARD_API_URL = "http://localhost:5001/api/upload"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(BROWSER_DATA_DIR, exist_ok=True)


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def cleanup_old_report_csvs():
    """Move old report*.csv files to archive folder"""
    archive_dir = os.path.expanduser("~/Downloads/salesforce_archive")
    os.makedirs(archive_dir, exist_ok=True)

    old_reports = glob.glob(os.path.join(DOWNLOAD_DIR, "report*.csv"))

    if old_reports:
        log(f"📁 Archiving {len(old_reports)} old report CSV(s)...")
        for report in old_reports:
            try:
                archive_path = os.path.join(archive_dir, os.path.basename(report))
                os.rename(report, archive_path)
            except Exception as e:
                log(f"   Warning: Could not archive {os.path.basename(report)}: {e}")
        log(f"   ✅ Old reports moved to: {archive_dir}")


def get_latest_csv(min_age_seconds=120):
    """
    Get the most recently downloaded CSV file

    Args:
        min_age_seconds: Only return files created in the last N seconds (default 120s)
    """
    # Look for CSV files, prefer "report*.csv" pattern from Salesforce
    all_csv_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.csv"))
    report_csv_files = glob.glob(os.path.join(DOWNLOAD_DIR, "report*.csv"))

    # Prefer Salesforce report files if available
    csv_files = report_csv_files if report_csv_files else all_csv_files

    if not csv_files:
        return None

    # Get the most recent file
    latest_file = max(csv_files, key=os.path.getctime)

    # Check if it was created recently (within last min_age_seconds)
    file_age = time.time() - os.path.getctime(latest_file)
    if file_age > min_age_seconds:
        return None

    return latest_file


def wait_for_csv_download(timeout_seconds=90, check_interval=2):
    """
    Wait for a CSV file to be downloaded

    Args:
        timeout_seconds: Maximum time to wait
        check_interval: How often to check (seconds)

    Returns:
        Path to downloaded CSV file or None
    """
    log(f"⏳ Monitoring Downloads folder: {DOWNLOAD_DIR}")
    log(f"⏳ Waiting for CSV download (timeout: {timeout_seconds}s)...")

    start_time = time.time()
    last_elapsed_log = 0

    while (time.time() - start_time) < timeout_seconds:
        # Check for new CSV files
        csv_file = get_latest_csv(min_age_seconds=timeout_seconds + 30)

        if csv_file:
            # Wait a bit to ensure file is completely downloaded
            time.sleep(2)
            log(f"✅ Download detected: {os.path.basename(csv_file)}")
            log(f"   Location: {csv_file}")
            return csv_file

        # Show progress dots every 10 seconds
        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 10 == 0 and elapsed != last_elapsed_log:
            log(f"   Still waiting... ({elapsed}/{timeout_seconds}s)")
            last_elapsed_log = elapsed

        time.sleep(check_interval)

    log(f"⏰ Timeout reached ({timeout_seconds}s)")
    log(f"💡 Tip: Check if the file downloaded to: {DOWNLOAD_DIR}")
    return None


def upload_to_dashboard(csv_file):
    """Upload CSV file to dashboard API"""
    try:
        log(f"📤 Uploading {os.path.basename(csv_file)} to dashboard...")

        with open(csv_file, 'rb') as f:
            files = {'file': (os.path.basename(csv_file), f, 'text/csv')}
            response = requests.post(DASHBOARD_API_URL, files=files)

        if response.status_code == 200:
            result = response.json()
            log(f"✅ Upload successful!")
            log(f"   New records: {result.get('new', 0)}")
            log(f"   Updated records: {result.get('updated', 0)}")
            return True
        else:
            log(f"❌ Upload failed: {response.text}")
            return False

    except Exception as e:
        log(f"❌ Error uploading to dashboard: {e}")
        return False


def download_salesforce_report(headless=False, first_run=False):
    """
    Download Salesforce report using browser automation

    Args:
        headless: Run browser in headless mode (no visible window)
        first_run: If True, keeps browser open for manual login
    """
    log("="*80)
    log("🚀 Starting Salesforce Report Auto-Sync")
    log("="*80)

    # Archive old report CSVs to avoid confusion
    cleanup_old_report_csvs()

    with sync_playwright() as p:
        try:
            log("🌐 Launching browser...")

            # Launch browser with persistent context (saves login session)
            browser = p.chromium.launch_persistent_context(
                user_data_dir=BROWSER_DATA_DIR,
                headless=headless,
                accept_downloads=True,
                viewport={'width': 1280, 'height': 800}
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            log(f"📊 Navigating to Salesforce report...")
            page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)

            # Wait a bit for page to load
            time.sleep(3)

            # Check if we're on a login page
            if 'login' in page.url.lower() or 'auth' in page.url.lower():
                log("🔐 Login required!")

                if first_run:
                    log("="*80)
                    log("⚠️  FIRST TIME SETUP - Please login to Salesforce")
                    log("="*80)
                    log("1. The browser window should be open")
                    log("2. Please log in to Salesforce manually")
                    log("3. Once logged in, the script will continue automatically")
                    log("4. Your session will be saved for future runs")
                    log("="*80)

                    # Wait for successful login (check for URL change)
                    log("⏳ Waiting for login... (timeout: 5 minutes)")
                    try:
                        page.wait_for_url("**/lightning/**", timeout=300000)  # 5 min timeout
                        log("✅ Login successful!")
                        time.sleep(2)
                    except PlaywrightTimeout:
                        log("❌ Login timeout. Please try again.")
                        browser.close()
                        return False
                else:
                    log("❌ Session expired. Please run with --login flag to login again.")
                    browser.close()
                    return False

            log("✅ Page loaded successfully")

            # Wait for the report to render
            log("⏳ Waiting for report to load...")
            time.sleep(5)

            # Try multiple selectors for the Export button
            export_button_selectors = [
                "button[title='Export']",
                "button:has-text('Export')",
                "a[title='Export']",
                "[data-action='export']",
                "lightning-button-menu button:has-text('Export')",
                "button.slds-button:has-text('Export')"
            ]

            export_clicked = False
            for selector in export_button_selectors:
                try:
                    log(f"🔍 Looking for export button: {selector}")
                    page.wait_for_selector(selector, timeout=5000)
                    page.click(selector)
                    log("✅ Clicked Export button")
                    export_clicked = True
                    break
                except:
                    continue

            if not export_clicked:
                log("⚠️  Could not find Export button automatically")
                log("")
                log("="*80)
                log("👉 MANUAL STEP REQUIRED")
                log("="*80)
                log("Please click the Export button now:")
                log("   1. Look for the dropdown menu (⚙️ gear icon or ⋮ three dots)")
                log("   2. Click 'Export' or 'Export Details'")
                log("   3. Select 'CSV' or 'Formatted Report'")
                log("   4. The download will start automatically")
                log("")
                log("⏳ Waiting 90 seconds for you to export...")
                log("   (Script will auto-detect the download)")
                log("="*80)

            else:
                # Wait for export dialog and click CSV/Details option
                time.sleep(2)

                # Try to click "Export Details" or "CSV" option
                export_options = [
                    "a:has-text('Export Details')",
                    "a:has-text('Formatted Report')",
                    "button:has-text('Export Details')",
                    "span:has-text('Export Details')"
                ]

                for option in export_options:
                    try:
                        page.click(option, timeout=3000)
                        log("✅ Selected export format")
                        break
                    except:
                        continue

            # Wait for CSV download (smart detection)
            csv_file = wait_for_csv_download(timeout_seconds=90, check_interval=2)

            if csv_file:
                log(f"✅ Report downloaded: {os.path.basename(csv_file)}")
                log(f"   File size: {os.path.getsize(csv_file) / 1024:.2f} KB")

                browser.close()

                # Upload to dashboard
                upload_success = upload_to_dashboard(csv_file)

                if upload_success:
                    log("="*80)
                    log("✅ Sync completed successfully!")
                    log("="*80)
                    return True
                else:
                    log("⚠️  Download succeeded but upload failed")
                    return False
            else:
                log("❌ No CSV file found in downloads folder")
                log(f"   Checked directory: {DOWNLOAD_DIR}")

                if not first_run:
                    log("\n💡 Tip: Run with --login flag for interactive mode")

                browser.close()
                return False

        except Exception as e:
            log(f"❌ Error during automation: {e}")
            if 'browser' in locals():
                browser.close()
            return False


def main():
    """Main function"""
    import sys

    # Check command line arguments
    first_run = '--login' in sys.argv or '--first-run' in sys.argv
    headless = '--headless' in sys.argv and not first_run

    if first_run:
        log("🔧 Running in FIRST-TIME SETUP mode")
        log("   Browser will stay open for manual login")
    elif headless:
        log("🔧 Running in HEADLESS mode")
        log("   Browser will run in background")

    success = download_salesforce_report(headless=headless, first_run=first_run)

    if success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
