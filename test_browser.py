#!/usr/bin/env python3
"""
Simple test to diagnose browser issues.
"""

from playwright.sync_api import sync_playwright
import time

print("Testing Playwright browser...")

try:
    with sync_playwright() as p:
        print("✅ Playwright started")
        
        # Try WebKit first (Safari engine - more stable on macOS)
        try:
            browser = p.webkit.launch(headless=False)
            print("✅ Browser launched (WebKit)")
        except Exception as e:
            print(f"WebKit failed: {e}")
            print("Trying Chromium instead...")
            browser = p.chromium.launch(headless=False)
            print("✅ Browser launched (Chromium)")
        
        page = browser.new_page()
        print("✅ Page created")
        
        # Test navigation to a simple page first
        print("\n🔍 Testing navigation to example.com...")
        page.goto("https://example.com", timeout=30000)
        print(f"✅ Navigated successfully")
        print(f"   Page title: {page.title()}")
        
        time.sleep(2)
        
        # Now try LinkedIn
        print("\n🔍 Testing navigation to LinkedIn...")
        url = "https://www.linkedin.com/jobs/search/?keywords=DATA%20SCIENTIST&location=Stockholm"
        page.goto(url, timeout=30000)
        print(f"✅ LinkedIn page loaded")
        print(f"   Final URL: {page.url}")
        print(f"   Page title: {page.title()}")
        
        # Check for auth wall
        if "/authwall" in page.url or "/login" in page.url:
            print("⚠️  LinkedIn redirected to login/authwall")
        
        time.sleep(5)  # Keep browser open to see what happened
        
        page.close()
        browser.close()
        print("\n✅ Test completed successfully!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

