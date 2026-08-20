#!/usr/bin/env python3
"""
Quick test to see if browser automation works at all
"""

import os
from datetime import datetime
from playwright.sync_api import sync_playwright

SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

log("="*80)
log("🧪 BROWSER TEST")
log("="*80)

try:
    with sync_playwright() as p:
        log("✅ Playwright imported successfully")

        log("🌐 Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BROWSER_DATA_DIR,
            headless=False,
            viewport={'width': 1400, 'height': 900}
        )

        log("✅ Browser launched")

        page = browser.pages[0] if browser.pages else browser.new_page()
        log("✅ Page created")

        log(f"📊 Navigating to: {SALESFORCE_REPORT_URL}")
        page.goto(SALESFORCE_REPORT_URL, timeout=60000)

        log(f"✅ Page loaded: {page.url}")
        log(f"📄 Page title: {page.title()}")

        log("")
        log("⏳ Keeping browser open for 20 seconds...")
        log("   Look at the browser window - do you see the Salesforce report?")
        log("")

        import time
        time.sleep(20)

        browser.close()
        log("✅ Test completed successfully!")

except Exception as e:
    log(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
