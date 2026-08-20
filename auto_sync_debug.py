#!/usr/bin/env python3
"""
Salesforce Report Auto-Sync - DEBUG VERSION
Shows detailed information about what's happening
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
SCREENSHOT_DIR = os.path.expanduser("~/salesforce-opportunity-tool/screenshots")

# Ensure directories exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def take_screenshot(page, name):
    """Take a screenshot for debugging"""
    try:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{name}_{int(time.time())}.png")
        page.screenshot(path=screenshot_path)
        log(f"📸 Screenshot saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        log(f"⚠️  Could not take screenshot: {e}")
        return None


def check_downloads_folder():
    """Show what's currently in Downloads folder"""
    log("📁 Current Downloads folder contents:")
    csv_files = glob.glob(os.path.join(DOWNLOAD_DIR, "report*.csv"))
    if csv_files:
        for f in csv_files:
            age = time.time() - os.path.getctime(f)
            log(f"   - {os.path.basename(f)} (age: {int(age)}s)")
    else:
        log("   (no report*.csv files found)")


def wait_for_new_csv(initial_files, timeout_seconds=120):
    """
    Wait for a NEW CSV file to appear

    Args:
        initial_files: Set of files that existed before export
        timeout_seconds: How long to wait
    """
    log("="*80)
    log("⏳ WAITING FOR DOWNLOAD")
    log("="*80)
    log(f"📁 Monitoring: {DOWNLOAD_DIR}")
    log(f"⏱️  Timeout: {timeout_seconds} seconds")
    log("")
    log("💡 Please click Export in the browser now!")
    log("")

    start_time = time.time()
    last_check_time = 0

    while (time.time() - start_time) < timeout_seconds:
        elapsed = int(time.time() - start_time)

        # Check for new files every 2 seconds
        current_files = set(glob.glob(os.path.join(DOWNLOAD_DIR, "report*.csv")))
        new_files = current_files - initial_files

        if new_files:
            new_file = list(new_files)[0]
            # Wait a moment to ensure download is complete
            time.sleep(3)
            log("")
            log("="*80)
            log(f"✅ NEW FILE DETECTED!")
            log("="*80)
            log(f"📄 File: {os.path.basename(new_file)}")
            log(f"📏 Size: {os.path.getsize(new_file) / 1024:.2f} KB")
            log(f"⏱️  Detected after: {elapsed} seconds")
            log("="*80)
            return new_file

        # Log progress every 10 seconds
        if elapsed > 0 and elapsed % 10 == 0 and elapsed != last_check_time:
            log(f"⏳ Still waiting... {elapsed}/{timeout_seconds}s (No new file yet)")
            last_check_time = elapsed

        time.sleep(2)

    log("")
    log("="*80)
    log("⏰ TIMEOUT - No new file detected")
    log("="*80)
    return None


def upload_to_dashboard(csv_file):
    """Upload CSV to dashboard"""
    try:
        log("")
        log("="*80)
        log("📤 UPLOADING TO DASHBOARD")
        log("="*80)
        log(f"📄 File: {os.path.basename(csv_file)}")

        with open(csv_file, 'rb') as f:
            files = {'file': (os.path.basename(csv_file), f, 'text/csv')}
            response = requests.post(DASHBOARD_API_URL, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            log("✅ UPLOAD SUCCESSFUL!")
            log(f"   📊 New records: {result.get('new', 0)}")
            log(f"   🔄 Updated records: {result.get('updated', 0)}")
            log(f"   📝 Total processed: {result.get('new', 0) + result.get('updated', 0)}")
            log("="*80)
            return True
        else:
            log(f"❌ UPLOAD FAILED!")
            log(f"   Status: {response.status_code}")
            log(f"   Error: {response.text}")
            log("="*80)
            return False

    except Exception as e:
        log(f"❌ UPLOAD ERROR: {e}")
        log("="*80)
        return False


def main():
    """Main debug function"""
    log("="*80)
    log("🐛 SALESFORCE AUTO-SYNC - DEBUG MODE")
    log("="*80)
    log(f"📁 Downloads folder: {DOWNLOAD_DIR}")
    log(f"📸 Screenshots folder: {SCREENSHOT_DIR}")
    log(f"🌐 Report URL: {SALESFORCE_REPORT_URL}")
    log("="*80)

    # Check initial state
    check_downloads_folder()
    initial_files = set(glob.glob(os.path.join(DOWNLOAD_DIR, "report*.csv")))
    log(f"📊 Starting with {len(initial_files)} existing report CSV(s)")
    log("="*80)

    with sync_playwright() as p:
        try:
            log("")
            log("🌐 LAUNCHING BROWSER")
            log("   This will open in a visible window so you can see what's happening")

            # Launch browser (NOT headless for debugging)
            browser = p.chromium.launch_persistent_context(
                user_data_dir=BROWSER_DATA_DIR,
                headless=False,  # Always visible in debug mode
                accept_downloads=True,
                viewport={'width': 1400, 'height': 900}
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            log("✅ Browser launched")
            log("")
            log("="*80)
            log("🔐 NAVIGATING TO SALESFORCE")
            log("="*80)
            log(f"🌐 URL: {SALESFORCE_REPORT_URL}")

            page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)
            log("✅ Page loaded")

            # Check if we need to login
            if 'login' in page.url.lower() or 'auth' in page.url.lower():
                log("")
                log("="*80)
                log("🔐 LOGIN REQUIRED")
                log("="*80)
                log("Please log in to Salesforce in the browser window")
                log("Waiting up to 5 minutes for login...")
                log("="*80)

                try:
                    page.wait_for_url("**/lightning/**", timeout=300000)
                    log("✅ Login successful!")
                except PlaywrightTimeout:
                    log("❌ Login timeout")
                    browser.close()
                    return False

            # Wait for report to load
            log("")
            log("⏳ Waiting for report to load...")
            time.sleep(5)

            # Take screenshot of the loaded page
            take_screenshot(page, "01_report_loaded")
            log("✅ Report loaded")

            # Try to find and click Export button
            log("")
            log("="*80)
            log("🔍 LOOKING FOR EXPORT BUTTON")
            log("="*80)

            export_selectors = [
                ("button[title='Export']", "Button with title='Export'"),
                ("button:has-text('Export')", "Button containing 'Export'"),
                ("lightning-button-menu button", "Lightning button menu"),
                ("[data-action='export']", "Element with data-action='export'"),
                ("button.slds-button", "SLDS button (any)"),
            ]

            export_found = False
            for selector, description in export_selectors:
                try:
                    log(f"🔍 Trying: {description}")
                    log(f"   Selector: {selector}")

                    if page.locator(selector).count() > 0:
                        log(f"   ✅ Found! Clicking...")
                        page.click(selector, timeout=3000)
                        log(f"   ✅ Clicked successfully!")
                        take_screenshot(page, "02_after_export_click")
                        export_found = True
                        time.sleep(2)
                        break
                    else:
                        log(f"   ❌ Not found")

                except Exception as e:
                    log(f"   ❌ Error: {e}")
                    continue

            if not export_found:
                log("")
                log("="*80)
                log("⚠️  EXPORT BUTTON NOT FOUND AUTOMATICALLY")
                log("="*80)
                log("")
                log("📸 Taking screenshot for analysis...")
                screenshot = take_screenshot(page, "03_export_not_found")
                log("")
                log("👆 MANUAL ACTION REQUIRED:")
                log("")
                log("   Please find and click the Export button yourself:")
                log("   1. Look for a dropdown menu (⚙️ gear, ⋮ dots, or 'Show Actions')")
                log("   2. Click to open the menu")
                log("   3. Click 'Export' or 'Export Details'")
                log("   4. Select 'CSV' or 'Formatted Report'")
                log("")
                log(f"   Screenshot saved to: {screenshot}")
                log("")
                log("="*80)

            # Wait for download (whether automatic or manual)
            csv_file = wait_for_new_csv(initial_files, timeout_seconds=120)

            # Take final screenshot
            take_screenshot(page, "04_final_state")

            # Close browser
            log("")
            log("🔒 Closing browser...")
            browser.close()
            log("✅ Browser closed")

            if csv_file:
                # Upload to dashboard
                success = upload_to_dashboard(csv_file)

                if success:
                    log("")
                    log("="*80)
                    log("🎉 SYNC COMPLETED SUCCESSFULLY!")
                    log("="*80)
                    return True
                else:
                    log("")
                    log("="*80)
                    log("⚠️  Download succeeded but upload failed")
                    log("="*80)
                    return False
            else:
                log("")
                log("="*80)
                log("❌ SYNC FAILED - No file downloaded")
                log("="*80)
                log("")
                log("🔍 Troubleshooting:")
                log("   1. Check screenshots in: " + SCREENSHOT_DIR)
                log("   2. Verify Export button was clicked")
                log("   3. Check Downloads folder manually: " + DOWNLOAD_DIR)
                log("="*80)
                return False

        except Exception as e:
            log("")
            log("="*80)
            log(f"❌ UNEXPECTED ERROR: {e}")
            log("="*80)
            if 'browser' in locals():
                try:
                    take_screenshot(page, "99_error_state")
                    browser.close()
                except:
                    pass
            return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
