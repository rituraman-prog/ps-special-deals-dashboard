#!/usr/bin/env python3
"""
Salesforce Auto-Sync - AGGRESSIVE AUTOMATION
Uses multiple strategies to click Export without specific selectors
"""

import os
import time
import glob
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view?queryScope=userFolders"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
DASHBOARD_API_URL = "http://localhost:5001/api/upload"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_csv_files():
    """Get all report CSV files"""
    pattern = os.path.join(DOWNLOAD_DIR, "report*.csv")
    files = glob.glob(pattern)
    return {f: os.path.getmtime(f) for f in files}


def wait_for_new_file(initial_files, timeout=180):
    """Wait for new CSV file"""
    log("⏳ Monitoring for download...")
    start_time = time.time()
    last_log = 0

    while (time.time() - start_time) < timeout:
        current_files = get_csv_files()

        for filepath, mtime in current_files.items():
            if filepath not in initial_files or mtime > initial_files.get(filepath, 0):
                elapsed = int(time.time() - start_time)
                log(f"✅ NEW FILE DETECTED: {os.path.basename(filepath)} (after {elapsed}s)")
                time.sleep(3)
                return filepath

        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 15 == 0 and elapsed != last_log:
            log(f"   Still waiting... {elapsed}/{timeout}s")
            last_log = elapsed

        time.sleep(2)

    log("⏰ Timeout - no download detected")
    return None


def upload_to_dashboard(csv_file):
    """Upload CSV to dashboard"""
    try:
        log("📤 Uploading to dashboard...")
        with open(csv_file, 'rb') as f:
            files = {'file': (os.path.basename(csv_file), f, 'text/csv')}
            response = requests.post(DASHBOARD_API_URL, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            log(f"✅ Upload successful! New: {result.get('new', 0)}, Updated: {result.get('updated', 0)}")

            # Archive
            archive_dir = os.path.join(DOWNLOAD_DIR, "salesforce_archive")
            os.makedirs(archive_dir, exist_ok=True)
            try:
                archive_path = os.path.join(archive_dir, os.path.basename(csv_file))
                os.rename(csv_file, archive_path)
                log(f"📁 Archived file")
            except:
                pass

            return True
        else:
            log(f"❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Upload error: {e}")
        return False


def try_export_automation(page):
    """
    Try multiple strategies to trigger export
    Returns True if something was clicked
    """
    log("")
    log("="*80)
    log("🤖 ATTEMPTING AUTOMATED EXPORT")
    log("="*80)

    strategies = [
        # Strategy 1: Look for any button/link with "export" in text
        ("Text: Export", lambda: page.get_by_text("Export", exact=False).first.click(timeout=3000)),

        # Strategy 2: Try button with export in title
        ("Title attribute", lambda: page.locator("button[title*='Export' i]").first.click(timeout=3000)),

        # Strategy 3: Click any lightning button menu then look for export
        ("Lightning menu", lambda: (
            page.locator("lightning-button-menu").first.click(timeout=3000),
            time.sleep(1),
            page.get_by_text("Export", exact=False).first.click(timeout=3000)
        )),

        # Strategy 4: Look for action menu (three dots or gear)
        ("Action menu", lambda: (
            page.locator('button[title*="Show Actions" i], button[title*="More" i]').first.click(timeout=3000),
            time.sleep(1),
            page.get_by_text("Export", exact=False).first.click(timeout=3000)
        )),

        # Strategy 5: Try clicking anything that looks like a menu trigger
        ("Menu trigger", lambda: (
            page.locator('.slds-dropdown-trigger, [data-target-reveals]').first.click(timeout=3000),
            time.sleep(1),
            page.get_by_text("Export", exact=False).first.click(timeout=3000)
        )),

        # Strategy 6: Use role-based selector
        ("Role button", lambda: page.locator('button[role="button"]:has-text("Export")').first.click(timeout=3000)),

        # Strategy 7: Click by aria-label
        ("Aria label", lambda: page.locator('button[aria-label*="Export" i]').first.click(timeout=3000)),
    ]

    for strategy_name, strategy_func in strategies:
        try:
            log(f"🔍 Trying strategy: {strategy_name}")
            strategy_func()
            log(f"✅ SUCCESS with: {strategy_name}")
            time.sleep(2)
            return True
        except Exception as e:
            log(f"   ❌ Failed: {strategy_name}")
            continue

    log("⚠️  All strategies failed")
    return False


def try_csv_selection(page):
    """Try to select CSV/Details format"""
    log("")
    log("🔍 Looking for CSV format option...")

    csv_strategies = [
        ("Text: Details", lambda: page.get_by_text("Details", exact=False).first.click(timeout=3000)),
        ("Text: Export Details", lambda: page.get_by_text("Export Details").first.click(timeout=3000)),
        ("Text: Formatted Report", lambda: page.get_by_text("Formatted Report").first.click(timeout=3000)),
        ("Link: Details", lambda: page.locator("a:has-text('Details')").first.click(timeout=3000)),
    ]

    for strategy_name, strategy_func in csv_strategies:
        try:
            log(f"🔍 Trying: {strategy_name}")
            strategy_func()
            log(f"✅ SUCCESS: {strategy_name}")
            time.sleep(2)
            return True
        except:
            continue

    log("⚠️  Could not auto-select CSV format")
    return False


def main():
    log("="*80)
    log("🚀 SALESFORCE AUTO-SYNC - AGGRESSIVE AUTOMATION")
    log("="*80)

    initial_files = get_csv_files()
    log(f"📊 Initial state: {len(initial_files)} existing CSV file(s)")

    with sync_playwright() as p:
        try:
            log("🌐 Launching browser...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=BROWSER_DATA_DIR,
                headless=False,
                accept_downloads=True,
                viewport={'width': 1400, 'height': 900},
                # Accept all downloads automatically
                accept_downloads=True,
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            log("✅ Browser launched")

            log("📊 Loading report...")
            page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)

            # Check for login
            if 'login' in page.url.lower() or 'auth' in page.url.lower():
                log("🔐 Login required")
                try:
                    page.wait_for_url("**/lightning/**", timeout=300000)
                    log("✅ Logged in")
                except:
                    log("❌ Login timeout")
                    browser.close()
                    return False

            log("✅ Report loaded")
            time.sleep(5)

            # Try automated export
            export_clicked = try_export_automation(page)

            if not export_clicked:
                log("")
                log("="*80)
                log("⚠️  AUTOMATION FAILED - MANUAL ACTION NEEDED")
                log("="*80)
                log("")
                log("Please click Export button manually:")
                log("  1. Find Export button (gear icon ⚙️ or three dots ⋮)")
                log("  2. Click it")
                log("")
                log("⏳ Waiting 30 seconds...")
                time.sleep(30)

            # Try to select CSV format
            time.sleep(2)
            csv_selected = try_csv_selection(page)

            if not csv_selected:
                log("")
                log("⚠️  Please select CSV format manually")
                log("  Click 'Export Details' or 'CSV' or 'Formatted Report'")
                log("")
                log("⏳ Waiting 30 seconds...")
                time.sleep(30)

            # Wait for download
            log("")
            log("="*80)
            log("⏳ WAITING FOR DOWNLOAD")
            log("="*80)
            log("Salesforce is processing... This may take 1-3 minutes")

            new_file = wait_for_new_file(initial_files, timeout=180)

            browser.close()
            log("🔒 Browser closed")

            if new_file:
                success = upload_to_dashboard(new_file)

                if success:
                    log("")
                    log("="*80)
                    log("🎉 SYNC COMPLETED SUCCESSFULLY!")
                    log("="*80)
                    return True
                else:
                    log("⚠️  Download succeeded but upload failed")
                    return False
            else:
                log("")
                log("="*80)
                log("❌ SYNC FAILED - No download detected")
                log("="*80)
                return False

        except Exception as e:
            log(f"❌ Error: {e}")
            if 'browser' in locals():
                try:
                    browser.close()
                except:
                    pass
            return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
