#!/usr/bin/env python3
"""
Button Discovery Script
Finds all clickable elements on the Salesforce report page
"""

import os
import time
from playwright.sync_api import sync_playwright

SALESFORCE_REPORT_URL = "https://org62.lightning.force.com/lightning/r/Report/00Oed00000AP8XhEAL/view?queryScope=userFolders"
BROWSER_DATA_DIR = os.path.expanduser("~/salesforce-opportunity-tool/browser_data")

def log(message):
    print(f"[DISCOVER] {message}")

with sync_playwright() as p:
    log("Launching browser...")
    browser = p.chromium.launch_persistent_context(
        user_data_dir=BROWSER_DATA_DIR,
        headless=False,
        viewport={'width': 1400, 'height': 900}
    )

    page = browser.pages[0] if browser.pages else browser.new_page()

    log("Loading report page...")
    page.goto(SALESFORCE_REPORT_URL, wait_until='domcontentloaded', timeout=60000)
    time.sleep(5)

    log("\n" + "="*80)
    log("DISCOVERING ALL BUTTONS ON PAGE")
    log("="*80)

    # Find all buttons
    all_buttons = page.locator("button").all()
    log(f"\nFound {len(all_buttons)} button elements:")

    for i, btn in enumerate(all_buttons):
        try:
            text = btn.inner_text(timeout=1000)
            title = btn.get_attribute('title', timeout=1000)
            aria_label = btn.get_attribute('aria-label', timeout=1000)
            class_name = btn.get_attribute('class', timeout=1000)

            if text or title or aria_label:
                log(f"\n--- Button {i+1} ---")
                if text and text.strip():
                    log(f"  Text: {text.strip()}")
                if title:
                    log(f"  Title: {title}")
                if aria_label:
                    log(f"  Aria-label: {aria_label}")
                if 'export' in str(text).lower() or 'export' in str(title).lower() or 'export' in str(aria_label).lower():
                    log(f"  ⭐ THIS MIGHT BE THE EXPORT BUTTON!")
                    log(f"  Class: {class_name}")
        except:
            continue

    # Find all links
    log("\n" + "="*80)
    all_links = page.locator("a").all()
    log(f"\nFound {len(all_links)} link elements:")

    for i, link in enumerate(all_links):
        try:
            text = link.inner_text(timeout=1000)
            href = link.get_attribute('href', timeout=1000)
            title = link.get_attribute('title', timeout=1000)

            if 'export' in str(text).lower() or 'export' in str(title).lower():
                log(f"\n--- Link {i+1} ---")
                if text and text.strip():
                    log(f"  Text: {text.strip()}")
                if title:
                    log(f"  Title: {title}")
                if href:
                    log(f"  Href: {href}")
                log(f"  ⭐ THIS MIGHT BE THE EXPORT LINK!")
        except:
            continue

    # Check for dropdown menus
    log("\n" + "="*80)
    log("Looking for dropdown/menu triggers:")

    menu_selectors = [
        'lightning-button-menu',
        '[role="button"]',
        'button[data-target-reveals]',
        '.slds-dropdown-trigger',
    ]

    for selector in menu_selectors:
        try:
            elements = page.locator(selector).all()
            if elements:
                log(f"\n  Found {len(elements)} elements matching: {selector}")
                for el in elements[:3]:  # Show first 3
                    try:
                        text = el.inner_text(timeout=500)
                        if text and text.strip():
                            log(f"    - {text.strip()}")
                    except:
                        pass
        except:
            continue

    log("\n" + "="*80)
    log("DISCOVERY COMPLETE!")
    log("="*80)
    log("\nLeaving browser open for 60 seconds so you can inspect...")
    log("Look for the Export button and note its location.")

    time.sleep(60)

    browser.close()
    log("Done!")
