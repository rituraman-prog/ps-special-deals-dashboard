#!/usr/bin/env python3
"""
Improved Salesforce Export Automation
Handles Shadow DOM, dynamic loading, and multiple fallback strategies
"""

import os
import time
import glob
import sys
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")
LOGIN_TIMEOUT = 300000  # 5 minutes for login
PAGE_LOAD_TIMEOUT = 60000  # 1 minute for page load


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_csv_files():
    """Get all report CSV files with their modification times"""
    pattern = os.path.join(DOWNLOAD_DIR, "report*.csv")
    files = glob.glob(pattern)
    return {f: os.path.getmtime(f) for f in files}


def wait_for_new_download(initial_files, timeout=180):
    """Wait for a new CSV file to appear in Downloads"""
    log(f"⏳ Monitoring {DOWNLOAD_DIR} for new files...")

    start_time = time.time()
    while (time.time() - start_time) < timeout:
        current_files = get_csv_files()

        # Check for new or modified files
        for filepath, mtime in current_files.items():
            if filepath not in initial_files or mtime > initial_files.get(filepath, 0):
                elapsed = int(time.time() - start_time)
                size_kb = os.path.getsize(filepath) / 1024
                log(f"✅ New file detected: {os.path.basename(filepath)} ({size_kb:.1f} KB) after {elapsed}s")
                time.sleep(3)  # Wait for download to complete
                return filepath

        time.sleep(2)

    log(f"⏰ Timeout after {timeout}s - no new file detected")
    return None


def click_export_with_js(page):
    """Use JavaScript to find and click Export button, piercing Shadow DOM"""
    js_strategies = [
        # Strategy 1: Find button with "Export" text anywhere on page
        """
        (function() {
            const buttons = Array.from(document.querySelectorAll('button, a'));
            for (let btn of buttons) {
                const text = btn.textContent || btn.innerText || btn.getAttribute('title') || '';
                if (text.toLowerCase().includes('export')) {
                    btn.click();
                    return 'CLICKED: ' + text.trim();
                }
            }
            return 'NOT_FOUND';
        })();
        """,

        # Strategy 2: Look inside Shadow DOMs
        """
        (function() {
            function findInShadow(root) {
                const elements = root.querySelectorAll('*');
                for (let el of elements) {
                    if (el.shadowRoot) {
                        const result = findInShadow(el.shadowRoot);
                        if (result) return result;
                    }
                    if ((el.tagName === 'BUTTON' || el.tagName === 'A')) {
                        const text = el.textContent || el.innerText || el.getAttribute('title') || '';
                        if (text.toLowerCase().includes('export')) {
                            el.click();
                            return 'CLICKED: ' + text.trim();
                        }
                    }
                }
                return null;
            }
            return findInShadow(document) || 'NOT_FOUND';
        })();
        """,

        # Strategy 3: Lightning component specific
        """
        (function() {
            const actions = document.querySelectorAll('lightning-button-menu, lightning-button');
            for (let action of actions) {
                const text = action.textContent || action.getAttribute('title') || '';
                if (text.toLowerCase().includes('export')) {
                    action.click();
                    return 'CLICKED: ' + text.trim();
                }
            }
            return 'NOT_FOUND';
        })();
        """,

        # Strategy 4: Menu icons (⋮ or ⚙️)
        """
        (function() {
            const menus = document.querySelectorAll('[title*="Show"], [title*="More"], [title*="Actions"]');
            for (let menu of menus) {
                menu.click();
                setTimeout(() => {
                    const items = Array.from(document.querySelectorAll('a, button, span'));
                    for (let item of items) {
                        const text = item.textContent || item.innerText || '';
                        if (text.toLowerCase().includes('export')) {
                            item.click();
                            return 'CLICKED: ' + text.trim();
                        }
                    }
                }, 500);
                return 'MENU_CLICKED';
            }
            return 'NOT_FOUND';
        })();
        """
    ]

    for i, js_code in enumerate(js_strategies, 1):
        try:
            log(f"   Strategy {i}: Executing JavaScript search...")
            result = page.evaluate(js_code)

            if result and 'CLICKED' in result:
                log(f"   ✅ {result}")
                return True
            elif result == 'MENU_CLICKED':
                log(f"   ⏳ Menu clicked, waiting for submenu...")
                time.sleep(1)
                # Try simpler search after menu opens
                simple_result = page.evaluate(js_strategies[0])
                if simple_result and 'CLICKED' in simple_result:
                    log(f"   ✅ {simple_result}")
                    return True

        except Exception as e:
            log(f"   ⚠️  Strategy {i} failed: {e}")
            continue

    return False


def click_csv_format(page):
    """Click on 'Details' or 'CSV' format option after Export is clicked"""
    selectors = [
        "text=Details",
        "text=Export Details",
        "text=Formatted Report",
        "a:has-text('Details')",
        "a:has-text('CSV')",
        "[data-export-type='details']"
    ]

    for selector in selectors:
        try:
            if page.locator(selector).count() > 0:
                log(f"   ✅ Found format option: {selector}")
                page.click(selector, timeout=3000)
                log(f"   ✅ Clicked CSV/Details format")
                return True
        except:
            continue

    # Try JavaScript as fallback
    try:
        result = page.evaluate("""
            (function() {
                const links = Array.from(document.querySelectorAll('a, button, span'));
                for (let link of links) {
                    const text = (link.textContent || link.innerText || '').toLowerCase();
                    if (text.includes('details') || text.includes('csv') || text.includes('formatted')) {
                        link.click();
                        return 'CLICKED: ' + text.trim();
                    }
                }
                return 'NOT_FOUND';
            })();
        """)

        if result and 'CLICKED' in result:
            log(f"   ✅ {result}")
            return True
    except:
        pass

    return False


def run_export(headless=False):
    """Run the complete export process"""
    log("="*80)
    log("🚀 SALESFORCE EXPORT AUTOMATION")
    log("="*80)
    log(f"📁 Download folder: {DOWNLOAD_DIR}")
    log(f"🌐 Report URL: {SALESFORCE_REPORT_URL}")
    log(f"🖥️  Mode: {'Headless' if headless else 'Visible'}")
    log("="*80)

    # Record initial files
    initial_files = get_csv_files()
    log(f"📊 Initial state: {len(initial_files)} existing CSV file(s)")

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
            log("📊 Loading report...")
            page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=PAGE_LOAD_TIMEOUT)
            time.sleep(3)

            # Check if login required
            if 'login' in page.url.lower() or 'auth' in page.url.lower():
                log("")
                log("🔐 Login required - please log in now")
                log("   Waiting up to 5 minutes...")
                try:
                    page.wait_for_url("**/lightning/**", timeout=LOGIN_TIMEOUT)
                    log("✅ Logged in successfully")
                    time.sleep(3)
                except PlaywrightTimeout:
                    log("❌ Login timeout - please run again after logging in")
                    browser.close()
                    return None

            log("✅ Report page loaded")

            # Wait for Lightning components to fully load
            log("⏳ Waiting for report to render (10 seconds)...")
            time.sleep(10)

            # Step 1: Click Export
            log("")
            log("="*80)
            log("STEP 1: FINDING AND CLICKING EXPORT")
            log("="*80)

            export_clicked = False

            # Try standard Playwright selectors first
            standard_selectors = [
                "button[title='Export']",
                "button:has-text('Export')",
                "lightning-button-menu button",
                "a[title='Export']"
            ]

            log("📍 Trying standard selectors...")
            for selector in standard_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"   ✅ Found: {selector} (count: {count})")
                        page.click(selector, timeout=5000)
                        log(f"   ✅ Clicked Export!")
                        export_clicked = True
                        time.sleep(2)
                        break
                except Exception as e:
                    continue

            # If standard selectors failed, use JavaScript
            if not export_clicked:
                log("")
                log("📍 Standard selectors failed, trying JavaScript...")
                export_clicked = click_export_with_js(page)

            if not export_clicked:
                log("")
                log("="*80)
                log("⚠️  COULD NOT AUTO-CLICK EXPORT")
                log("="*80)
                log("")
                log("Please manually click Export now, then the script will continue.")
                log("Looking for: 'Export' button or menu (usually near top-right)")
                log("")
                log("⏳ Waiting 45 seconds for manual click...")
                log("="*80)
                time.sleep(45)

            # Step 2: Select CSV/Details format
            log("")
            log("="*80)
            log("STEP 2: SELECTING CSV FORMAT")
            log("="*80)
            time.sleep(2)

            if not click_csv_format(page):
                log("")
                log("⚠️  Could not auto-select CSV format")
                log("If a dialog appeared, please select 'Details' or 'CSV' now")
                log("⏳ Waiting 15 seconds...")
                time.sleep(15)

            # Step 3: Wait for download
            log("")
            log("="*80)
            log("STEP 3: WAITING FOR DOWNLOAD")
            log("="*80)

            downloaded_file = wait_for_new_download(initial_files, timeout=180)

            if downloaded_file:
                log("")
                log("="*80)
                log("✅ EXPORT COMPLETED SUCCESSFULLY")
                log("="*80)
                log(f"📄 File: {os.path.basename(downloaded_file)}")
                log("📤 Auto-upload watcher will process this file")
                log("="*80)
                browser.close()
                return downloaded_file
            else:
                log("")
                log("="*80)
                log("❌ EXPORT FAILED")
                log("="*80)
                log("No new file detected in Downloads folder")
                log("Please try again or export manually")
                log("="*80)
                browser.close()
                return None

        except Exception as e:
            log("")
            log(f"❌ Error during export: {e}")
            try:
                browser.close()
            except:
                pass
            return None


def main():
    parser = argparse.ArgumentParser(description='Salesforce Report Export Automation')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()

    try:
        result = run_export(headless=args.headless)
        if result:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
    except KeyboardInterrupt:
        log("")
        log("🛑 Export cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
