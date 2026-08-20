#!/usr/bin/env python3
"""
Deep Discovery Script - Waits for full page load and checks everything
"""

import os
import time
from playwright.sync_api import sync_playwright

SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view?queryScope=userFolders"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")

def log(message):
    print(f"[DEEP-DISCOVER] {message}")

with sync_playwright() as p:
    log("Launching browser...")
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BROWSER_DATA_DIR,
        headless=False,
        viewport={'width': 1400, 'height': 900}
    )

    page = browser.pages[0] if browser.pages else browser.new_page()

    log("Loading report page...")
    page.goto(SALESFORCE_REPORT_URL, wait_until='networkidle', timeout=90000)

    log("Waiting for page to fully render (15 seconds)...")
    time.sleep(15)

    log("\n" + "="*80)
    log("DEEP PAGE ANALYSIS")
    log("="*80)

    # Check page title
    log(f"\nPage Title: {page.title()}")
    log(f"Page URL: {page.url}")

    # Check for ALL clickable elements
    log("\n--- ALL CLICKABLE ELEMENTS (buttons, links, divs with click) ---")

    clickable_selectors = [
        "button",
        "a",
        "[role='button']",
        ".slds-button",
        "lightning-button",
        "lightning-button-menu",
        "[onclick]",
        "[data-action]",
        ".actionLink",
    ]

    total_found = 0
    for selector in clickable_selectors:
        try:
            elements = page.locator(selector).all()
            if elements:
                log(f"\n{selector}: Found {len(elements)} elements")
                total_found += len(elements)

                # Show first 5 with text
                for i, el in enumerate(elements[:5]):
                    try:
                        text = el.inner_text(timeout=500)
                        title = el.get_attribute('title', timeout=500)
                        aria_label = el.get_attribute('aria-label', timeout=500)

                        display_text = text[:50] if text and text.strip() else "(no text)"

                        if text or title or aria_label:
                            log(f"  [{i+1}] {display_text}")
                            if title:
                                log(f"      title='{title}'")
                            if aria_label:
                                log(f"      aria-label='{aria_label}'")

                            # Check if related to export
                            search_text = f"{text} {title} {aria_label}".lower()
                            if 'export' in search_text:
                                log(f"      ⭐⭐⭐ EXPORT RELATED! ⭐⭐⭐")
                    except:
                        continue
        except Exception as e:
            log(f"  Error checking {selector}: {e}")

    log(f"\n\nTotal clickable elements found: {total_found}")

    # Check page content for "export" text
    log("\n--- SEARCHING PAGE FOR 'EXPORT' TEXT ---")
    try:
        page_text = page.content()
        if 'export' in page_text.lower():
            log("✅ Found 'export' in page HTML")

            # Count occurrences
            export_count = page_text.lower().count('export')
            log(f"   Appears {export_count} times in HTML")
        else:
            log("❌ 'export' NOT found in page HTML")
    except Exception as e:
        log(f"Error searching page: {e}")

    # Take screenshot
    screenshot_path = os.path.expanduser("~/salesforce-opportunity-tool/page_screenshot.png")
    try:
        page.screenshot(path=screenshot_path, full_page=True)
        log(f"\n📸 Screenshot saved: {screenshot_path}")
    except:
        pass

    # Check if we're actually logged in and on the right page
    log("\n--- PAGE STATE CHECK ---")
    if 'login' in page.url.lower():
        log("⚠️  WARNING: On login page, not report page!")
    elif 'report' in page.url.lower():
        log("✅ On report page")
    else:
        log(f"⚠️  Unexpected URL: {page.url}")

    log("\n" + "="*80)
    log("Keeping browser open for 2 minutes...")
    log("Please look at the page and MANUALLY click Export if you see it.")
    log("This will help me see what happens in the console.")
    log("="*80)

    time.sleep(120)

    browser.close()
    log("Done!")
