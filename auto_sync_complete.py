#!/usr/bin/env python3
"""
Salesforce Report Auto-Sync - Complete Multi-Step Export Handler
Handles: Export click → Format selection → Processing → Download
"""

import os
import time
import glob
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view?queryScope=userFolders"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
DASHBOARD_API_URL = "http://localhost:5001/api/upload"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_csv_files():
    """Get all report CSV files in Downloads"""
    pattern = os.path.join(DOWNLOAD_DIR, "report*.csv")
    files = glob.glob(pattern)
    return {f: os.path.getmtime(f) for f in files}


def wait_for_new_file(initial_files, timeout=180):
    """Wait for a NEW CSV file to appear"""
    log("")
    log("="*80)
    log("⏳ MONITORING FOR DOWNLOAD")
    log("="*80)
    log(f"📁 Watching: {DOWNLOAD_DIR}/report*.csv")
    log(f"⏱️  Timeout: {timeout} seconds")
    log("")

    start_time = time.time()
    last_log_time = 0

    while (time.time() - start_time) < timeout:
        current_files = get_csv_files()

        # Check for new or modified files
        for filepath, mtime in current_files.items():
            if filepath not in initial_files or mtime > initial_files.get(filepath, 0):
                elapsed = int(time.time() - start_time)
                log("")
                log("✅ NEW FILE DETECTED!")
                log(f"   📄 {os.path.basename(filepath)}")
                log(f"   📏 {os.path.getsize(filepath) / 1024:.1f} KB")
                log(f"   ⏱️  Detected after {elapsed}s")
                log("="*80)

                # Wait to ensure download is complete
                time.sleep(3)
                return filepath

        # Log progress every 15 seconds
        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 15 == 0 and elapsed != last_log_time:
            log(f"⏳ Still waiting... {elapsed}/{timeout}s")
            last_log_time = elapsed

        time.sleep(2)

    log("")
    log("⏰ TIMEOUT - No download detected")
    log("="*80)
    return None


def upload_to_dashboard(csv_file):
    """Upload CSV to dashboard"""
    try:
        log("")
        log("="*80)
        log("📤 UPLOADING TO DASHBOARD")
        log("="*80)

        with open(csv_file, 'rb') as f:
            files = {'file': (os.path.basename(csv_file), f, 'text/csv')}
            response = requests.post(DASHBOARD_API_URL, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            log("✅ UPLOAD SUCCESSFUL!")
            log(f"   📊 New records: {result.get('new', 0)}")
            log(f"   🔄 Updated records: {result.get('updated', 0)}")
            log("="*80)

            # Archive the uploaded file
            archive_dir = os.path.join(DOWNLOAD_DIR, "salesforce_archive")
            os.makedirs(archive_dir, exist_ok=True)
            try:
                archive_path = os.path.join(archive_dir, os.path.basename(csv_file))
                os.rename(csv_file, archive_path)
                log(f"📁 Archived to: salesforce_archive/")
            except:
                pass

            return True
        else:
            log(f"❌ Upload failed: {response.status_code}")
            return False

    except Exception as e:
        log(f"❌ Upload error: {e}")
        return False


def main():
    """Main function with complete export flow"""
    log("="*80)
    log("🚀 SALESFORCE AUTO-SYNC - COMPLETE VERSION")
    log("="*80)
    log(f"📁 Downloads folder: {DOWNLOAD_DIR}")
    log(f"🌐 Report URL: {SALESFORCE_REPORT_URL}")
    log("="*80)

    # Record initial state
    initial_files = get_csv_files()
    log(f"📊 Initial state: {len(initial_files)} existing CSV file(s)")
    log("="*80)

    with sync_playwright() as p:
        try:
            log("")
            log("🌐 Launching browser (visible mode)...")

            browser = p.chromium.launch_persistent_context(
                user_data_dir=BROWSER_DATA_DIR,
                headless=False,
                accept_downloads=True,
                viewport={'width': 1400, 'height': 900}
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            log("✅ Browser launched")

            # Navigate to report
            log("")
            log("📊 Loading report page...")
            page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)

            # Check for login
            if 'login' in page.url.lower() or 'auth' in page.url.lower():
                log("")
                log("🔐 Login required - please log in manually")
                log("   Waiting up to 5 minutes...")
                try:
                    page.wait_for_url("**/lightning/**", timeout=300000)
                    log("✅ Logged in successfully")
                    time.sleep(2)
                except PlaywrightTimeout:
                    log("❌ Login timeout")
                    browser.close()
                    return False

            log("✅ Report page loaded")
            log("")
            log("⏳ Waiting for report to fully render...")
            time.sleep(5)

            # Step 1: Find and click Export button
            log("")
            log("="*80)
            log("STEP 1: CLICKING EXPORT BUTTON")
            log("="*80)

            export_selectors = [
                "button[title='Export']",
                "button:has-text('Export')",
                "lightning-button-menu button:has-text('Export')",
                "a:has-text('Export')",
            ]

            export_clicked = False
            for selector in export_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"✅ Found Export button: {selector}")
                        page.click(selector, timeout=5000)
                        log("✅ Clicked Export button!")
                        export_clicked = True
                        time.sleep(2)
                        break
                except Exception as e:
                    continue

            if not export_clicked:
                log("⚠️  Could not auto-click Export")
                log("")
                log("="*80)
                log("👆 MANUAL ACTION REQUIRED")
                log("="*80)
                log("")
                log("Please click Export now:")
                log("   1. Look for Export button or dropdown (⚙️ ⋮)")
                log("   2. Click it")
                log("")
                log("⏳ Waiting 30 seconds for you to click...")
                log("="*80)
                time.sleep(30)

            # Step 2: Handle format selection dialog
            log("")
            log("="*80)
            log("STEP 2: SELECTING CSV FORMAT")
            log("="*80)

            # Wait for dialog/options to appear
            time.sleep(2)

            # Try to find and click CSV option
            csv_selectors = [
                "a:has-text('Details')",
                "a:has-text('Formatted Report')",
                "span:has-text('Details')",
                "button:has-text('Details')",
                "[data-export-type='details']",
                "a:has-text('Export Details')",
            ]

            csv_clicked = False
            for selector in csv_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        log(f"✅ Found CSV option: {selector}")
                        page.click(selector, timeout=3000)
                        log("✅ Clicked CSV/Details option!")
                        csv_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            if not csv_clicked:
                log("⚠️  Could not auto-select CSV format")
                log("")
                log("="*80)
                log("👆 MANUAL ACTION REQUIRED")
                log("="*80)
                log("")
                log("Please select CSV format now:")
                log("   1. A dialog should be open")
                log("   2. Click 'Export Details' or 'CSV' or 'Formatted Report'")
                log("")
                log("⏳ Waiting 30 seconds for you to select...")
                log("="*80)
                time.sleep(30)

            # Step 3: Wait for processing and download
            log("")
            log("="*80)
            log("STEP 3: WAITING FOR PROCESSING & DOWNLOAD")
            log("="*80)
            log("")
            log("⏳ Salesforce is processing the export...")
            log("   This may open a new tab with 'Processing...'")
            log("   Download will start automatically when ready")
            log("")

            # Handle potential new tab
            try:
                # Wait a bit for new tab to open
                time.sleep(3)

                # Check if new tab/page opened
                if len(browser.pages) > 1:
                    log("📄 New tab detected (processing page)")
                    # Switch to the new tab if needed
                    processing_page = browser.pages[-1]
                    processing_page.bring_to_front()
            except:
                pass

            # Now wait for the actual file download
            new_file = wait_for_new_file(initial_files, timeout=180)

            # Close browser
            log("")
            log("🔒 Closing browser...")
            browser.close()
            log("✅ Browser closed")

            if new_file:
                # Upload to dashboard
                success = upload_to_dashboard(new_file)

                if success:
                    log("")
                    log("="*80)
                    log("🎉 SYNC COMPLETED SUCCESSFULLY!")
                    log("="*80)
                    return True
                else:
                    log("")
                    log("⚠️  Download succeeded but upload failed")
                    return False
            else:
                log("")
                log("="*80)
                log("❌ SYNC FAILED - No file downloaded")
                log("="*80)
                log("")
                log("🔍 Troubleshooting:")
                log("   1. Did you complete all the export steps?")
                log("   2. Check if processing completed in the new tab")
                log("   3. Look in Downloads for report*.csv")
                log("="*80)
                return False

        except Exception as e:
            log("")
            log(f"❌ Unexpected error: {e}")
            if 'browser' in locals():
                try:
                    browser.close()
                except:
                    pass
            return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
