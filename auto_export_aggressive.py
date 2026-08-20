#!/usr/bin/env python3
"""
Aggressive Salesforce Export Automation
Uses multiple strategies and longer waits for dynamic content
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


def wait_for_new_download(initial_files, timeout=180):
    """Wait for a new file and rename it properly"""
    log(f"⏳ Monitoring downloads folder...")

    start_time = time.time()
    while (time.time() - start_time) < timeout:
        # Check all files, not just CSV
        all_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))

        for filepath in all_files:
            if not os.path.isfile(filepath):
                continue

            mtime = os.path.getmtime(filepath)

            # Check if this is a new file (created after we started monitoring)
            if filepath not in initial_files or mtime > initial_files.get(filepath, start_time):
                # Skip common non-report files
                filename = os.path.basename(filepath).lower()
                if any(skip in filename for skip in ['.ds_store', '.tmp', '.download', '.crdownload', '.part']):
                    continue

                elapsed = int(time.time() - start_time)
                size_kb = os.path.getsize(filepath) / 1024

                log(f"✅ New file detected: {os.path.basename(filepath)} ({size_kb:.1f} KB) after {elapsed}s")
                time.sleep(3)  # Wait for download to complete

                # Rename to report*.csv
                timestamp = int(time.time() * 1000)

                if filepath.endswith('.csv'):
                    if not os.path.basename(filepath).startswith('report'):
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        try:
                            os.rename(filepath, new_path)
                            log(f"   📝 Renamed to: {os.path.basename(new_path)}")
                            return new_path
                        except:
                            return filepath
                    return filepath

                elif filepath.endswith(('.xls', '.xlsx')):
                    log(f"   📊 Converting Excel to CSV...")
                    try:
                        import pandas as pd
                        df = pd.read_excel(filepath)
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        df.to_csv(new_path, index=False, encoding='utf-8')
                        log(f"   ✅ Converted to: {os.path.basename(new_path)}")
                        os.remove(filepath)
                        return new_path
                    except Exception as e:
                        log(f"   ⚠️  Conversion failed: {e}")
                        return filepath

                else:
                    # Unknown extension or no extension - try to convert or rename
                    log(f"   🔍 Attempting to process unknown file type...")
                    try:
                        import pandas as pd
                        df = pd.read_excel(filepath)
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        df.to_csv(new_path, index=False, encoding='utf-8')
                        log(f"   ✅ Converted Excel to: {os.path.basename(new_path)}")
                        os.remove(filepath)
                        return new_path
                    except:
                        # Not Excel, assume CSV and just rename
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        try:
                            os.rename(filepath, new_path)
                            log(f"   📝 Renamed to: {os.path.basename(new_path)}")
                            return new_path
                        except Exception as e:
                            log(f"   ⚠️  Could not process: {e}")
                            return filepath

        time.sleep(2)

    log(f"⏰ Timeout - no download detected after {timeout}s")
    return None


def aggressive_click_export(page):
    """Use multiple aggressive strategies to click Export"""

    log("🎯 Using aggressive automation strategies...")

    # Strategy 1: Wait for page to be completely idle
    log("   Waiting for page to be fully loaded...")
    time.sleep(15)  # Longer wait for Lightning components

    # Strategy 2: Use JavaScript to find and click dropdown
    log("   Trying to find dropdown button...")

    result = page.evaluate("""
        async () => {
            // Wait for buttons to appear
            await new Promise(resolve => setTimeout(resolve, 5000));

            // Find all buttons
            const allButtons = Array.from(document.querySelectorAll('button'));

            // Look for dropdown near Edit
            for (let btn of allButtons) {
                const hasPopup = btn.getAttribute('aria-haspopup');
                const ariaLabel = btn.getAttribute('aria-label') || '';
                const title = btn.getAttribute('title') || '';

                if (hasPopup === 'true' || ariaLabel.includes('more') || title.includes('more') || ariaLabel.includes('actions')) {
                    btn.click();
                    await new Promise(resolve => setTimeout(resolve, 2000));

                    // Now look for Export option
                    const allElements = Array.from(document.querySelectorAll('a, span, div'));
                    for (let el of allElements) {
                        const text = (el.textContent || '').trim();
                        if (text === 'Export') {
                            el.click();
                            return {success: true, step: 'export_clicked'};
                        }
                    }
                }
            }

            return {success: false, step: 'dropdown_not_found'};
        }
    """)

    if result.get('success'):
        log(f"   ✅ Successfully clicked: {result.get('step')}")
        time.sleep(3)
        return True

    log(f"   ⚠️  Failed at: {result.get('step')}")
    return False


def aggressive_configure_export(page):
    """Aggressively configure export dialog"""

    log("⚙️  Configuring export dialog...")
    time.sleep(3)

    result = page.evaluate("""
        async () => {
            await new Promise(resolve => setTimeout(resolve, 2000));

            let configured = {details: false, csv: false, exported: false};

            // 1. Click Details Only
            const allElements = Array.from(document.querySelectorAll('*'));
            for (let el of allElements) {
                const text = (el.textContent || '').trim();
                if (text === 'Details Only' || text.includes('Detail rows')) {
                    el.click();
                    configured.details = true;
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    break;
                }
            }

            // 2. Find and change format dropdown to CSV
            const selects = document.querySelectorAll('select');
            for (let select of selects) {
                const options = Array.from(select.options);
                const csvOption = options.find(opt =>
                    opt.text.includes('Comma') || opt.text.includes('csv') || opt.value === 'csv'
                );
                if (csvOption) {
                    select.value = csvOption.value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                    configured.csv = true;
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    break;
                }
            }

            // If no select found, try clicking CSV option directly
            if (!configured.csv) {
                for (let el of allElements) {
                    const text = (el.textContent || '').trim();
                    if (text === 'Comma Delimited .csv') {
                        el.click();
                        configured.csv = true;
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        break;
                    }
                }
            }

            // 3. Click Export button
            const buttons = Array.from(document.querySelectorAll('button'));
            for (let btn of buttons) {
                const text = (btn.textContent || '').trim();
                const disabled = btn.disabled;
                if (text === 'Export' && !disabled) {
                    btn.click();
                    configured.exported = true;
                    break;
                }
            }

            return configured;
        }
    """)

    log(f"   Details Only: {'✅' if result.get('details') else '❌'}")
    log(f"   CSV Format: {'✅' if result.get('csv') else '❌'}")
    log(f"   Export Clicked: {'✅' if result.get('exported') else '❌'}")

    return result.get('exported', False)


def run_export(headless=False, auto_configure=True):
    """Run aggressive export automation"""
    log("="*80)
    log("🚀 AGGRESSIVE SALESFORCE EXPORT AUTOMATION")
    log("="*80)
    log(f"🖥️  Mode: {'Headless' if headless else 'Visible'}")
    log(f"⚙️  Auto-configure: {auto_configure}")
    log("="*80)

    initial_files = {}
    for pattern in [os.path.join(DOWNLOAD_DIR, "*")]:
        for f in glob.glob(pattern):
            if os.path.isfile(f):
                initial_files[f] = os.path.getmtime(f)

    with sync_playwright() as p:
        try:
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

            log("📊 Navigating to report...")
            page.goto(SALESFORCE_REPORT_URL, wait_until='networkidle', timeout=90000)
            time.sleep(5)

            # Handle login
            if 'login' in page.url.lower() or 'auth' in page.url.lower() or 'signing' in page.url.lower():
                log("🔐 Login required - waiting up to 3 minutes...")
                try:
                    page.wait_for_url("**/lightning/**", timeout=180000)
                    log("✅ Logged in")
                    time.sleep(10)  # Wait for report to fully load after login
                except PlaywrightTimeout:
                    log("❌ Login timeout")
                    browser.close()
                    return None

            log("✅ Report page loaded")
            log("⏳ Waiting for Lightning components to render (15 seconds)...")
            time.sleep(15)

            if auto_configure:
                # Try aggressive automation
                export_success = aggressive_click_export(page)

                if export_success:
                    configure_success = aggressive_configure_export(page)

                    if configure_success:
                        log("✅ Export automation successful!")
                    else:
                        log("⚠️  Export dialog not fully configured")
                        log("   Please manually select CSV format and click Export")
                        time.sleep(30)
                else:
                    log("⚠️  Could not automate Export click")
                    log("   Please manually: Click dropdown → Export → Configure → Export")
                    time.sleep(45)
            else:
                log("👉 Please manually export the report now")
                log("   (Dropdown → Export → Details Only → CSV → Export button)")
                time.sleep(60)

            # Wait for download
            log("")
            log("="*80)
            log("WAITING FOR DOWNLOAD")
            log("="*80)

            downloaded_file = wait_for_new_download(initial_files, timeout=180)

            if downloaded_file:
                log("")
                log("="*80)
                log("✅ EXPORT COMPLETED!")
                log("="*80)
                log(f"📄 {os.path.basename(downloaded_file)}")
                log(f"📏 {os.path.getsize(downloaded_file) / 1024:.1f} KB")
                log("📤 Auto-upload watcher will process this")
                log("="*80)
                browser.close()
                return downloaded_file
            else:
                log("")
                log("="*80)
                log("❌ NO DOWNLOAD DETECTED")
                log("="*80)
                browser.close()
                return None

        except Exception as e:
            log(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            try:
                browser.close()
            except:
                pass
            return None


def main():
    parser = argparse.ArgumentParser(description='Aggressive Salesforce Export')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--manual', action='store_true', help='Skip automation, wait for manual export')
    args = parser.parse_args()

    try:
        result = run_export(headless=args.headless, auto_configure=not args.manual)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        log("🛑 Cancelled")
        sys.exit(1)


if __name__ == "__main__":
    main()
