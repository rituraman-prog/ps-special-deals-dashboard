#!/usr/bin/env python3
"""
Test finding Export in the dropdown next to Edit tab
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
log("🔍 FINDING EXPORT IN DROPDOWN")
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

        # Check for login
        if 'login' in page.url.lower() or 'auth' in page.url.lower():
            log("🔐 Waiting for login (up to 2 minutes)...")
            try:
                page.wait_for_url("**/lightning/**", timeout=120000)
                log("✅ Logged in")
                time.sleep(5)
            except PlaywrightTimeout:
                log("❌ Login timeout")
                browser.close()
                exit(1)

        log("✅ Report page loaded")
        log("⏳ Waiting for page to fully render (10 seconds)...")
        time.sleep(10)

        log("")
        log("="*80)
        log("STEP 1: FINDING EDIT TAB")
        log("="*80)

        # Look for Edit tab/button
        edit_selectors = [
            "button:has-text('Edit')",
            "a:has-text('Edit')",
            "[title='Edit']",
            "span:has-text('Edit')"
        ]

        edit_found = False
        for selector in edit_selectors:
            try:
                count = page.locator(selector).count()
                if count > 0:
                    log(f"✅ Found Edit element: {selector} (count: {count})")
                    edit_found = True

                    # Get info about it
                    element = page.locator(selector).first
                    log(f"   Tag: {element.evaluate('el => el.tagName')}")
                    log(f"   Text: {element.inner_text(timeout=2000)}")

            except Exception as e:
                continue

        if not edit_found:
            log("⚠️  Edit tab not found, searching with JavaScript...")
            result = page.evaluate("""
                () => {
                    const all = Array.from(document.querySelectorAll('*'));
                    const editElements = all.filter(el => {
                        const text = (el.textContent || '').trim();
                        return text === 'Edit' || text.includes('Edit');
                    });
                    return editElements.slice(0, 5).map(el => ({
                        tag: el.tagName,
                        text: el.textContent?.trim().substring(0, 50),
                        class: el.className,
                        id: el.id
                    }));
                }
            """)
            log(f"   Found {len(result)} Edit-related elements:")
            for item in result:
                log(f"   - {item}")

        log("")
        log("="*80)
        log("STEP 2: FINDING DROPDOWN NEXT TO EDIT")
        log("="*80)

        # Look for dropdown buttons (common patterns)
        dropdown_selectors = [
            "button[title*='Show more']",
            "button[title*='Show actions']",
            "button[title*='More actions']",
            "lightning-button-menu button",
            "button.slds-button_icon-border-filled",
            "button[class*='dropdown']",
            "button:has-text('▼')",
            "button[aria-haspopup='true']"
        ]

        dropdown_found = False
        for selector in dropdown_selectors:
            try:
                count = page.locator(selector).count()
                if count > 0:
                    log(f"✅ Found dropdown: {selector} (count: {count})")
                    dropdown_found = True

                    # Get details
                    for i in range(min(count, 3)):
                        element = page.locator(selector).nth(i)
                        title = element.get_attribute("title", timeout=1000) or ""
                        aria_label = element.get_attribute("aria-label", timeout=1000) or ""
                        log(f"   Dropdown {i+1}: title='{title}' aria-label='{aria_label}'")

            except Exception as e:
                continue

        log("")
        log("="*80)
        log("STEP 3: TRYING TO CLICK DROPDOWN AND FIND EXPORT")
        log("="*80)

        # Strategy 1: Click likely dropdown menus and look for Export
        tried_dropdowns = []

        for selector in dropdown_selectors:
            try:
                count = page.locator(selector).count()
                if count > 0:
                    for i in range(min(count, 3)):  # Try first 3 dropdowns
                        dropdown = page.locator(selector).nth(i)

                        log(f"📍 Clicking dropdown: {selector} (#{i+1})")
                        dropdown.click(timeout=3000)
                        time.sleep(1)

                        # Look for Export in the opened menu
                        export_in_menu = page.locator("a:has-text('Export'), span:has-text('Export'), div:has-text('Export')")
                        export_count = export_in_menu.count()

                        if export_count > 0:
                            log(f"   ✅✅✅ FOUND EXPORT IN MENU! (count: {export_count})")
                            for j in range(export_count):
                                item = export_in_menu.nth(j)
                                log(f"   Export option {j+1}: {item.inner_text(timeout=2000)}")

                            log("")
                            log("🎯 SUCCESS! Export found in this dropdown!")
                            log("   Keeping browser open for 30 seconds so you can see...")
                            time.sleep(30)
                            browser.close()
                            exit(0)
                        else:
                            log(f"   ❌ No Export found in this menu")
                            # Click somewhere else to close the menu
                            page.keyboard.press("Escape")
                            time.sleep(0.5)

            except Exception as e:
                log(f"   ⚠️  Error clicking: {e}")
                continue

        log("")
        log("⚠️  Couldn't automatically find Export in dropdown")
        log("   Keeping browser open for 60 seconds...")
        log("   Please manually click the dropdown next to Edit and tell me what you see")
        log("")
        time.sleep(60)

        browser.close()
        log("✅ Test completed")

except Exception as e:
    log(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
