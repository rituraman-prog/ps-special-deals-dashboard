#!/usr/bin/env python3
"""
Better browser test - waits for login and report to load
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

log("="*80)
log("🧪 BROWSER TEST V2")
log("="*80)

try:
    with sync_playwright() as p:
        log("🌐 Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,
            viewport={'width': 1400, 'height': 900}
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        log("✅ Browser launched")

        log(f"📊 Navigating to report...")
        page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)

        log(f"📄 Current URL: {page.url}")
        log(f"📄 Page title: {page.title()}")

        # Check if we need to log in
        if 'login' in page.url.lower() or 'auth' in page.url.lower() or page.title() == 'Log In Using | Salesforce':
            log("")
            log("🔐 Login/Authentication needed")
            log("   Please complete login in the browser window")
            log("   Waiting up to 2 minutes...")
            log("")

            try:
                # Wait for URL to change to lightning (report page)
                page.wait_for_url("**/lightning/**", timeout=120000)
                log("✅ Login successful!")
                time.sleep(3)
            except PlaywrightTimeout:
                log("⏰ Timeout waiting for login")
                browser.close()
                exit(1)

        log("")
        log("✅ Report page should be loaded now")
        log(f"📄 Current URL: {page.url}")
        log(f"📄 Page title: {page.title()}")
        log("")

        # Wait for page to fully render
        log("⏳ Waiting for report to fully render (10 seconds)...")
        time.sleep(10)

        log("")
        log("🔍 Looking for buttons on the page...")

        # Count all buttons
        buttons = page.locator("button").all()
        log(f"   Found {len(buttons)} button elements")

        # Show first few button texts
        for i, btn in enumerate(buttons[:10]):
            try:
                text = btn.inner_text(timeout=1000)
                title = btn.get_attribute("title", timeout=1000)
                if text or title:
                    log(f"   Button {i+1}: text='{text}' title='{title}'")
            except:
                pass

        log("")
        log("🔍 Searching for Export button specifically...")

        # Try to find Export button
        export_found = False

        # Method 1: By title
        try:
            export_btn = page.locator("button[title*='Export']").first
            if export_btn.count() > 0:
                log(f"   ✅ Found by title: {export_btn.get_attribute('title')}")
                export_found = True
        except:
            pass

        # Method 2: By text
        try:
            export_btn = page.locator("button:has-text('Export')").first
            if export_btn.count() > 0:
                log(f"   ✅ Found by text: {export_btn.inner_text()}")
                export_found = True
        except:
            pass

        # Method 3: Using JavaScript
        result = page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button, a'));
                const exportButtons = buttons.filter(b => {
                    const text = (b.textContent || '').toLowerCase();
                    const title = (b.getAttribute('title') || '').toLowerCase();
                    return text.includes('export') || title.includes('export');
                });
                return exportButtons.map(b => ({
                    tag: b.tagName,
                    text: b.textContent?.trim(),
                    title: b.getAttribute('title'),
                    class: b.className
                }));
            }
        """)

        if result:
            log(f"   ✅ Found {len(result)} Export-related elements via JavaScript:")
            for item in result:
                log(f"      - {item['tag']}: text='{item['text']}' title='{item['title']}'")
            export_found = True

        if not export_found:
            log("   ⚠️  No Export button found")
            log("   The page might still be loading, or Export is in a menu")

        log("")
        log("⏳ Keeping browser open for 30 seconds so you can inspect...")
        log("   Look for the Export button/menu in the browser window")
        log("")
        time.sleep(30)

        browser.close()
        log("✅ Test completed!")

except Exception as e:
    log(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
