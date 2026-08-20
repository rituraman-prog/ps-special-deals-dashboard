#!/usr/bin/env python3
"""
Hybrid Salesforce Export - Semi-Automated Approach
Opens dialog, user selects format, script handles download
"""

import os
import time
import glob
import sys
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_recent_downloads():
    """Get all recently downloaded files"""
    patterns = [
        os.path.join(DOWNLOAD_DIR, "*.csv"),
        os.path.join(DOWNLOAD_DIR, "*.xls"),
        os.path.join(DOWNLOAD_DIR, "*.xlsx"),
    ]

    files = {}
    for pattern in patterns:
        for f in glob.glob(pattern):
            files[f] = os.path.getmtime(f)

    return files


def convert_excel_to_csv(excel_file):
    """Convert Excel file to CSV"""
    try:
        import pandas as pd

        log(f"   📊 Converting Excel to CSV...")

        # Read Excel file
        df = pd.read_excel(excel_file, engine='openpyxl' if excel_file.endswith('.xlsx') else 'xlrd')

        # Generate CSV filename
        base_name = os.path.basename(excel_file).rsplit('.', 1)[0]
        csv_file = os.path.join(DOWNLOAD_DIR, f"report_{base_name}.csv")

        # Save as CSV
        df.to_csv(csv_file, index=False, encoding='utf-8')

        log(f"   ✅ Converted to: {os.path.basename(csv_file)}")

        # Remove original Excel file
        try:
            os.remove(excel_file)
            log(f"   🗑️  Removed original Excel file")
        except:
            pass

        return csv_file

    except Exception as e:
        log(f"   ⚠️  Could not convert Excel to CSV: {e}")
        return None


def wait_for_new_download(initial_files, timeout=120):
    """Wait for a new file to appear and convert if needed"""
    log(f"⏳ Monitoring {DOWNLOAD_DIR} for new files...")
    log(f"   Timeout: {timeout} seconds")

    start_time = time.time()
    last_check_time = 0

    while (time.time() - start_time) < timeout:
        current_files = get_recent_downloads()

        # Check for new or modified files
        for filepath, mtime in current_files.items():
            if filepath not in initial_files or mtime > initial_files.get(filepath, 0):
                elapsed = int(time.time() - start_time)
                size_kb = os.path.getsize(filepath) / 1024
                filename = os.path.basename(filepath)

                log(f"")
                log(f"✅ NEW FILE DETECTED!")
                log(f"   📄 {filename}")
                log(f"   📏 {size_kb:.1f} KB")
                log(f"   ⏱️  After {elapsed}s")

                time.sleep(3)  # Wait for download to complete

                # Check file type
                if filepath.endswith('.csv'):
                    log(f"   ✅ File is CSV format")
                    return filepath
                elif filepath.endswith(('.xls', '.xlsx')):
                    log(f"   📊 File is Excel format")
                    csv_file = convert_excel_to_csv(filepath)
                    if csv_file:
                        return csv_file
                    else:
                        log(f"   ⚠️  Conversion failed, returning Excel file")
                        return filepath

        # Progress indicator every 10 seconds
        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 10 == 0 and elapsed != last_check_time:
            log(f"   ⏳ Still waiting... {elapsed}/{timeout}s")
            last_check_time = elapsed

        time.sleep(2)

    log(f"")
    log(f"⏰ TIMEOUT - No new file detected after {timeout}s")
    return None


def run_export(headless=False):
    """Run hybrid export automation"""
    log("="*80)
    log("🚀 SALESFORCE EXPORT - HYBRID AUTOMATION")
    log("="*80)
    log(f"📁 Download folder: {DOWNLOAD_DIR}")
    log(f"🌐 Report URL: {SALESFORCE_REPORT_URL}")
    log(f"🖥️  Mode: {'Headless' if headless else 'Visible'}")
    log("")
    log("📝 How this works:")
    log("   1. Script opens browser and Export dialog")
    log("   2. YOU select format (CSV or Excel) and click Export")
    log("   3. Script detects download and converts Excel→CSV if needed")
    log("="*80)

    # Record initial files
    initial_files = get_recent_downloads()
    log(f"📊 Initial state: {len(initial_files)} existing file(s)")

    with sync_playwright() as p:
        try:
            log("")
            log("🌐 Launching browser...")

            browser = p.chromium.launch_persistent_context(
                user_data_dir=BROWSER_DATA_DIR,
                headless=headless,
                accept_downloads=True,
                viewport={'width': 1400, 'height': 900},
                downloads_path=DOWNLOAD_DIR
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            log("✅ Browser launched")

            # Navigate to report
            log("")
            log("📊 Loading report page...")
            page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)

            # Check for login
            if 'login' in page.url.lower() or 'auth' in page.url.lower() or 'signing' in page.url.lower():
                log("")
                log("🔐 Login required")
                log("   Please log in - waiting up to 3 minutes...")
                try:
                    page.wait_for_url("**/lightning/**", timeout=180000)
                    log("✅ Logged in")
                    time.sleep(5)
                except PlaywrightTimeout:
                    log("❌ Login timeout")
                    browser.close()
                    return None

            log("✅ Report page loaded")
            log("⏳ Waiting for page to render (10 seconds)...")
            time.sleep(10)

            # STEP 1: Click dropdown next to Edit
            log("")
            log("="*80)
            log("STEP 1: OPENING EXPORT MENU")
            log("="*80)

            # Try to find and click the dropdown
            dropdown_clicked = False

            # Method 1: Try standard selectors
            dropdown_selectors = [
                "button[title='Edit'] + button",
                "lightning-button-menu button",
                "button[aria-haspopup='true']"
            ]

            for selector in dropdown_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"   Found dropdown: {selector}")
                        page.locator(selector).first.click(timeout=3000)
                        dropdown_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            # Method 2: JavaScript
            if not dropdown_clicked:
                log("   Trying JavaScript...")
                result = page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button[aria-haspopup="true"]'));
                        if (buttons.length > 0) {
                            buttons[0].click();
                            return 'CLICKED';
                        }
                        return 'NOT_FOUND';
                    }
                """)
                if 'CLICKED' in result:
                    dropdown_clicked = True
                    log(f"   ✅ Clicked dropdown via JavaScript")
                    time.sleep(2)

            if not dropdown_clicked:
                log("   ⚠️  Couldn't find dropdown automatically")
                log("   Please click the dropdown next to Edit now...")
                time.sleep(15)

            # STEP 2: Click Export
            log("")
            log("="*80)
            log("STEP 2: CLICKING EXPORT")
            log("="*80)

            export_clicked = False
            export_selectors = [
                "a:has-text('Export')",
                "span:has-text('Export')",
                "div[role='menuitem']:has-text('Export')"
            ]

            for selector in export_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        page.click(selector, timeout=3000)
                        log(f"   ✅ Clicked Export")
                        export_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            if not export_clicked:
                log("   ⚠️  Couldn't find Export automatically")
                log("   Please click Export in the menu now...")
                time.sleep(15)

            # STEP 3: User handles the dialog
            log("")
            log("="*80)
            log("STEP 3: YOUR TURN!")
            log("="*80)
            log("")
            log("👉 The Export dialog should now be open")
            log("")
            log("Please do these steps:")
            log("   1. Select 'Details Only'")
            log("   2. Change format to 'Comma Delimited .csv'")
            log("   3. Click the blue 'Export' button")
            log("")
            log("⏳ Waiting 60 seconds for you to complete these steps...")
            log("")

            time.sleep(60)

            # STEP 4: Wait for download
            log("")
            log("="*80)
            log("STEP 4: WAITING FOR DOWNLOAD")
            log("="*80)

            downloaded_file = wait_for_new_download(initial_files, timeout=120)

            if downloaded_file:
                log("")
                log("="*80)
                log("✅ EXPORT COMPLETED!")
                log("="*80)
                log(f"📄 File: {os.path.basename(downloaded_file)}")
                log(f"📁 Location: {downloaded_file}")
                log(f"📏 Size: {os.path.getsize(downloaded_file) / 1024:.1f} KB")
                log("")
                log("📤 Auto-upload watcher will process this file")
                log("="*80)
                browser.close()
                return downloaded_file
            else:
                log("")
                log("="*80)
                log("❌ NO FILE DOWNLOADED")
                log("="*80)
                log("Possible reasons:")
                log("   • Browser blocked the download")
                log("   • Export dialog was cancelled")
                log("   • Download went to a different folder")
                log("="*80)
                browser.close()
                return None

        except Exception as e:
            log("")
            log(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            try:
                browser.close()
            except:
                pass
            return None


def main():
    parser = argparse.ArgumentParser(description='Hybrid Salesforce Export')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (not recommended)')
    args = parser.parse_args()

    try:
        result = run_export(headless=args.headless)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        log("")
        log("🛑 Export cancelled")
        sys.exit(1)


if __name__ == "__main__":
    main()
