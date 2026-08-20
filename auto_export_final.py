#!/usr/bin/env python3
"""
Final Salesforce Export Automation
Based on actual UI: Edit dropdown → Export → Details Only → CSV → Export button
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


def get_csv_files():
    """Get all CSV files in Downloads with modification times"""
    pattern = os.path.join(DOWNLOAD_DIR, "*.csv")
    files = glob.glob(pattern)
    return {f: os.path.getmtime(f) for f in files}


def get_recent_downloads():
    """Get all recently downloaded files (CSV, Excel, or files without extension)"""
    patterns = [
        os.path.join(DOWNLOAD_DIR, "*.csv"),
        os.path.join(DOWNLOAD_DIR, "*.xls"),
        os.path.join(DOWNLOAD_DIR, "*.xlsx"),
    ]

    files = {}
    for pattern in patterns:
        for f in glob.glob(pattern):
            files[f] = os.path.getmtime(f)

    # Also check for files without extensions (Salesforce sometimes does this)
    all_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))
    for f in all_files:
        if os.path.isfile(f) and not any(f.endswith(ext) for ext in ['.csv', '.xls', '.xlsx', '.pdf', '.png', '.jpg', '.zip', '.txt', '.md', '.py']):
            # File with no common extension - might be our download
            files[f] = os.path.getmtime(f)

    return files


def convert_excel_to_csv(excel_file):
    """Convert Excel file to CSV"""
    try:
        import pandas as pd

        log(f"   Converting Excel to CSV...")

        # Read Excel file
        df = pd.read_excel(excel_file)

        # Generate CSV filename
        csv_file = excel_file.rsplit('.', 1)[0] + '.csv'
        if not csv_file.endswith('.csv'):
            csv_file = excel_file + '.csv'

        # Save as CSV
        df.to_csv(csv_file, index=False, encoding='utf-8')

        log(f"   ✅ Converted to: {os.path.basename(csv_file)}")

        # Remove original Excel file
        try:
            os.remove(excel_file)
            log(f"   Removed original Excel file")
        except:
            pass

        return csv_file

    except Exception as e:
        log(f"   ⚠️  Could not convert Excel to CSV: {e}")
        return None


def wait_for_new_download(initial_files, timeout=120):
    """Wait for a new file to appear (CSV or Excel) and convert if needed"""
    log(f"⏳ Monitoring {DOWNLOAD_DIR} for new files...")

    start_time = time.time()
    while (time.time() - start_time) < timeout:
        current_files = get_recent_downloads()

        # Check for new or modified files
        for filepath, mtime in current_files.items():
            if filepath not in initial_files or mtime > initial_files.get(filepath, 0):
                elapsed = int(time.time() - start_time)
                size_kb = os.path.getsize(filepath) / 1024
                filename = os.path.basename(filepath)

                log(f"✅ New file detected: {filename} ({size_kb:.1f} KB) after {elapsed}s")
                time.sleep(3)  # Wait for download to complete

                # Check file type and rename appropriately
                timestamp = int(time.time() * 1000)

                if filepath.endswith('.csv'):
                    log(f"   ✅ File is already CSV")
                    # Rename to report*.csv for watcher
                    new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                    try:
                        os.rename(filepath, new_path)
                        log(f"   📝 Renamed to: {os.path.basename(new_path)}")
                        return new_path
                    except:
                        return filepath

                elif filepath.endswith(('.xls', '.xlsx')):
                    log(f"   📊 File is Excel format - converting to CSV...")
                    csv_file = convert_excel_to_csv(filepath)
                    if csv_file:
                        # Rename converted file
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        try:
                            os.rename(csv_file, new_path)
                            log(f"   📝 Renamed to: {os.path.basename(new_path)}")
                            return new_path
                        except:
                            return csv_file
                    else:
                        return filepath

                else:
                    # File without extension - detect type and convert
                    log(f"   🔍 File has no extension - detecting type...")

                    # Check if it's Excel by trying to read it
                    try:
                        import pandas as pd
                        df = pd.read_excel(filepath)
                        log(f"   📊 Detected as Excel format")

                        # Save as CSV with proper name
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        df.to_csv(new_path, index=False, encoding='utf-8')
                        log(f"   ✅ Converted and saved as: {os.path.basename(new_path)}")

                        # Remove original
                        try:
                            os.remove(filepath)
                        except:
                            pass

                        return new_path

                    except:
                        # Might be CSV without extension - just rename it
                        log(f"   📝 Assuming CSV format - renaming...")
                        new_path = os.path.join(DOWNLOAD_DIR, f"report{timestamp}.csv")
                        try:
                            os.rename(filepath, new_path)
                            log(f"   ✅ Renamed to: {os.path.basename(new_path)}")
                            return new_path
                        except Exception as e:
                            log(f"   ⚠️  Could not rename: {e}")
                            return filepath

        time.sleep(2)

    log(f"⏰ Timeout after {timeout}s - no new file detected")
    return None


def run_export(headless=False):
    """Run complete export automation"""
    log("="*80)
    log("🚀 SALESFORCE EXPORT AUTOMATION - FINAL VERSION")
    log("="*80)
    log(f"📁 Download folder: {DOWNLOAD_DIR}")
    log(f"🌐 Report URL: {SALESFORCE_REPORT_URL}")
    log(f"🖥️  Mode: {'Headless' if headless else 'Visible'}")
    log("="*80)

    # Record initial files
    initial_files = get_recent_downloads()
    log(f"📊 Initial state: {len(initial_files)} existing file(s) in Downloads")

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
                log("🔐 Login required - please complete authentication")
                log("   Waiting up to 3 minutes...")
                try:
                    page.wait_for_url("**/lightning/**", timeout=180000)
                    log("✅ Logged in successfully")
                    time.sleep(5)
                except PlaywrightTimeout:
                    log("❌ Login timeout")
                    browser.close()
                    return None

            log("✅ Report page loaded")
            log("⏳ Waiting for page to fully render (10 seconds)...")
            time.sleep(10)

            # STEP 1: Find and click the dropdown next to Edit
            log("")
            log("="*80)
            log("STEP 1: CLICKING DROPDOWN NEXT TO EDIT")
            log("="*80)

            dropdown_found = False
            dropdown_selectors = [
                # The dropdown button next to Edit
                "button[title='Edit'] + button",  # Button immediately after Edit
                "div:has(button[title='Edit']) button[aria-haspopup='true']",  # Dropdown in same container as Edit
                "lightning-button-menu button",  # Lightning dropdown menu
                "button.slds-button_icon-border",  # Salesforce icon button style
                "button[class*='slds-button'][class*='icon']"  # Generic SLDS icon button
            ]

            for selector in dropdown_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"   Found dropdown: {selector} (count: {count})")

                        # Try clicking the first matching dropdown
                        dropdown = page.locator(selector).first
                        log(f"   Clicking dropdown...")
                        dropdown.click(timeout=5000)
                        dropdown_found = True
                        time.sleep(2)
                        break
                except Exception as e:
                    continue

            # If selectors didn't work, try JavaScript
            if not dropdown_found:
                log("   Trying JavaScript approach...")
                result = page.evaluate("""
                    () => {
                        // Find Edit button first
                        const editButton = Array.from(document.querySelectorAll('button')).find(b =>
                            (b.getAttribute('title') || '').includes('Edit')
                        );

                        if (editButton) {
                            // Look for dropdown button near Edit
                            const parent = editButton.parentElement;
                            const dropdowns = parent.querySelectorAll('button[aria-haspopup="true"]');
                            if (dropdowns.length > 0) {
                                dropdowns[0].click();
                                return 'CLICKED_DROPDOWN';
                            }
                        }

                        // Fallback: click any dropdown that might have Export
                        const allDropdowns = document.querySelectorAll('button[aria-haspopup="true"]');
                        for (let btn of allDropdowns) {
                            btn.click();
                            return 'CLICKED_GENERIC_DROPDOWN';
                        }

                        return 'NOT_FOUND';
                    }
                """)

                if 'CLICKED' in result:
                    log(f"   ✅ {result}")
                    dropdown_found = True
                    time.sleep(2)

            if not dropdown_found:
                log("   ⚠️  Could not find dropdown automatically")
                log("   Please click the dropdown next to Edit button now...")
                time.sleep(10)

            # STEP 2: Click Export in the menu
            log("")
            log("="*80)
            log("STEP 2: CLICKING EXPORT IN MENU")
            log("="*80)

            export_clicked = False
            export_selectors = [
                "a:has-text('Export')",
                "span:has-text('Export')",
                "div[role='menuitem']:has-text('Export')",
                "[data-label='Export']"
            ]

            for selector in export_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"   ✅ Found Export option: {selector}")
                        page.click(selector, timeout=3000)
                        log(f"   ✅ Clicked Export!")
                        export_clicked = True
                        time.sleep(2)
                        break
                except:
                    continue

            if not export_clicked:
                log("   Trying JavaScript to find Export...")
                result = page.evaluate("""
                    () => {
                        const items = Array.from(document.querySelectorAll('a, span, div'));
                        const exportItem = items.find(el =>
                            (el.textContent || '').trim() === 'Export'
                        );
                        if (exportItem) {
                            exportItem.click();
                            return 'CLICKED_EXPORT';
                        }
                        return 'NOT_FOUND';
                    }
                """)

                if 'CLICKED' in result:
                    log(f"   ✅ {result}")
                    export_clicked = True
                    time.sleep(2)

            if not export_clicked:
                log("   ⚠️  Could not find Export option")
                log("   Please click Export in the menu now...")
                time.sleep(10)

            # STEP 3: Wait for Export dialog and configure it
            log("")
            log("="*80)
            log("STEP 3: CONFIGURING EXPORT DIALOG")
            log("="*80)

            # Wait for dialog to appear
            time.sleep(3)

            # Click "Details Only" option
            log("   Selecting 'Details Only'...")
            details_selectors = [
                "text=Details Only",
                "div:has-text('Details Only')",
                "input[value='DETAIL_ROWS']"
            ]

            details_clicked = False
            for selector in details_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector, timeout=3000)
                        log(f"   ✅ Selected 'Details Only'")
                        details_clicked = True
                        time.sleep(1)
                        break
                except:
                    continue

            # Select CSV format from dropdown
            log("   Selecting 'Comma Delimited .csv' format...")

            csv_selected = False

            # Strategy 1: Find and click the format dropdown button
            format_dropdown_selectors = [
                "button:has-text('Excel Format')",
                "button:has-text('.xls')",
                "select",
                "[class*='dropdown']:has-text('Format')",
                "button[aria-haspopup='listbox']"
            ]

            for selector in format_dropdown_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"      Found format control: {selector}")

                        # Check if it's a <select> element
                        if selector == "select":
                            # Standard HTML select
                            page.select_option(selector, label="Comma Delimited .csv", timeout=3000)
                            log("   ✅ Selected CSV format (via select)")
                            csv_selected = True
                            break
                        else:
                            # Button-style dropdown - click to open
                            page.click(selector, timeout=3000)
                            log(f"      Clicked dropdown button")
                            time.sleep(1)

                            # Now click the CSV option
                            csv_option_selectors = [
                                "text=Comma Delimited .csv",
                                "span:has-text('Comma Delimited .csv')",
                                "div:has-text('Comma Delimited .csv')",
                                "[data-value='csv']"
                            ]

                            for csv_sel in csv_option_selectors:
                                try:
                                    if page.locator(csv_sel).count() > 0:
                                        page.click(csv_sel, timeout=2000)
                                        log("   ✅ Selected CSV format")
                                        csv_selected = True
                                        break
                                except:
                                    continue

                            if csv_selected:
                                break
                except Exception as e:
                    continue

            # Strategy 2: Use JavaScript to find and change format
            if not csv_selected:
                log("      Trying JavaScript approach...")
                result = page.evaluate("""
                    () => {
                        // Try to find select element
                        const selects = document.querySelectorAll('select');
                        for (let select of selects) {
                            const options = Array.from(select.options);
                            const csvOption = options.find(opt =>
                                opt.text.includes('Comma') || opt.text.includes('csv') || opt.value === 'csv'
                            );
                            if (csvOption) {
                                select.value = csvOption.value;
                                select.dispatchEvent(new Event('change', { bubbles: true }));
                                return 'SELECTED_CSV_VIA_SELECT';
                            }
                        }

                        // Try to find and click CSV option directly
                        const allElements = Array.from(document.querySelectorAll('*'));
                        const csvElement = allElements.find(el => {
                            const text = (el.textContent || '').trim();
                            return text === 'Comma Delimited .csv' || text.includes('.csv');
                        });

                        if (csvElement) {
                            csvElement.click();
                            return 'CLICKED_CSV_OPTION';
                        }

                        return 'NOT_FOUND';
                    }
                """)

                if result and 'SELECTED' in result or 'CLICKED' in result:
                    log(f"   ✅ {result}")
                    csv_selected = True

            if not csv_selected:
                log("   ⚠️  Could not change format to CSV (may default to Excel)")
                log("   You may need to manually select CSV format in the dialog")

            time.sleep(2)

            # STEP 4: Click Export button
            log("")
            log("="*80)
            log("STEP 4: CLICKING EXPORT BUTTON")
            log("="*80)

            export_button_clicked = False
            export_button_selectors = [
                "button:has-text('Export'):not([disabled])",
                "button.slds-button_brand:has-text('Export')",
                "input[type='submit'][value='Export']"
            ]

            for selector in export_button_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        log(f"   ✅ Found Export button: {selector}")
                        page.click(selector, timeout=5000)
                        log(f"   ✅ Clicked Export button!")
                        export_button_clicked = True
                        time.sleep(2)
                        break
                except Exception as e:
                    continue

            if not export_button_clicked:
                log("   ⚠️  Could not find Export button")
                log("   Please click the blue Export button now...")
                time.sleep(10)

            # STEP 5: Wait for download
            log("")
            log("="*80)
            log("STEP 5: WAITING FOR DOWNLOAD")
            log("="*80)

            downloaded_file = wait_for_new_download(initial_files, timeout=120)

            if downloaded_file:
                log("")
                log("="*80)
                log("✅ EXPORT COMPLETED SUCCESSFULLY!")
                log("="*80)
                log(f"📄 File: {os.path.basename(downloaded_file)}")
                log(f"📁 Location: {downloaded_file}")
                log(f"📏 Size: {os.path.getsize(downloaded_file) / 1024:.1f} KB")
                log("📤 Auto-upload watcher will process this file")
                log("="*80)
                browser.close()
                return downloaded_file
            else:
                log("")
                log("="*80)
                log("❌ EXPORT FAILED - NO FILE DOWNLOADED")
                log("="*80)
                log("   Check if:")
                log("   1. Browser blocked the download")
                log("   2. Download went to a different folder")
                log("   3. Format wasn't changed to CSV")
                log("="*80)
                browser.close()
                return None

        except Exception as e:
            log("")
            log(f"❌ Error during export: {e}")
            import traceback
            traceback.print_exc()
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
