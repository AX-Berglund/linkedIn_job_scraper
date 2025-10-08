#!/usr/bin/env python3
"""
Interactive LinkedIn Explorer
Opens a browser window so you can manually explore and see exact URLs.
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load credentials
load_dotenv()

def main():
    print("="*60)
    print("🔍 LinkedIn Interactive Explorer")
    print("="*60)
    print("\nThis will open a browser window for you to explore LinkedIn.")
    print("You can:")
    print("  - Log in manually")
    print("  - Navigate to job searches")
    print("  - See the exact URLs in the address bar")
    print("  - Inspect page elements")
    print("\nThe browser will stay open until you close this script.")
    print("="*60)
    
    # Ask if auto-login
    auto_login = os.getenv('LINKEDIN_AUTO_LOGIN', 'false').lower() == 'true'
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    with sync_playwright() as p:
        # Launch visible browser (Chromium is more stable than WebKit for interactive use)
        print("\n🌐 Launching Chromium browser...")
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']  # Start maximized for better visibility
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # Auto-login if enabled
        if auto_login and email and password:
            print("🔐 Auto-login enabled, attempting to log in...")
            try:
                page.goto("https://www.linkedin.com/login", timeout=30000)
                time.sleep(2)
                
                # Fill email
                email_field = page.locator("#username")
                if email_field.count() > 0:
                    email_field.fill(email)
                    print("  ✅ Email entered")
                
                # Fill password
                password_field = page.locator("#password")
                if password_field.count() > 0:
                    password_field.fill(password)
                    print("  ✅ Password entered")
                
                # Click sign in
                sign_in_button = page.locator("button[type='submit']")
                if sign_in_button.count() > 0:
                    sign_in_button.click()
                    print("  🚀 Sign in clicked")
                    time.sleep(5)
                    
                    if "feed" in page.url or "jobs" in page.url:
                        print("  ✅ Successfully logged in!")
                    else:
                        print(f"  ⚠️  Current URL: {page.url}")
            except Exception as e:
                print(f"  ⚠️  Auto-login failed: {e}")
                print("     You can log in manually in the browser window")
        else:
            # Go to LinkedIn homepage
            print("📍 Opening LinkedIn...")
            page.goto("https://www.linkedin.com")
        
        print("\n" + "="*60)
        print("✅ Browser is ready!")
        print("="*60)
        print("\n📋 Instructions:")
        print("  1. The browser window is now open and visible")
        print("  2. Navigate around LinkedIn manually")
        print("  3. Try searching for jobs")
        print("  4. Look at the URLs in the address bar")
        print("  5. Note the exact format LinkedIn uses")
        print("\n💡 Suggested exploration:")
        print("  - Go to Jobs section")
        print("  - Search: 'data scientist'")
        print("  - Location: 'Stockholm'")
        print("  - Look at the URL after search")
        print("  - Try scrolling down")
        print("  - See if LinkedIn asks you to sign in")
        print("\n⌨️  Press Ctrl+C in this terminal to close the browser")
        print("="*60)
        
        # Keep checking current URL
        try:
            last_url = ""
            while True:
                current_url = page.url
                if current_url != last_url:
                    print(f"\n📍 Current URL: {current_url}")
                    last_url = current_url
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n👋 Closing browser...")
        
        browser.close()
        print("✅ Done!")

if __name__ == "__main__":
    main()

