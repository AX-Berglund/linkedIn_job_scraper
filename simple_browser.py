#!/usr/bin/env python3
"""
Simple browser test - Just opens Chrome and goes to LinkedIn.
Use this to verify Playwright is working on your system.
"""

from playwright.sync_api import sync_playwright
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("="*60)
print("🌐 Simple Browser Test")
print("="*60)
print("\nOpening Chrome and navigating to LinkedIn...")
print("Press Ctrl+C to close the browser.\n")

try:
    with sync_playwright() as p:
        # Launch Chrome with proper arguments for macOS
        print("Starting Chrome...")
        
        # Try to use system Chrome first (more stable on macOS)
        try:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",  # Use system Chrome instead of Chromium
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            print("✅ Using system Chrome")
        except Exception as e:
            print(f"⚠️  Could not use system Chrome, trying Chromium: {e}")
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            print("✅ Using Chromium")
        
        print("✅ Browser launched successfully!")
        
        # Create a page
        print("Creating new page...")
        page = browser.new_page()
        
        print("✅ Page created successfully!")
        
        # Navigate to LinkedIn
        print("Navigating to LinkedIn...")
        page.goto("https://www.linkedin.com", timeout=60000)
        
        print("✅ Successfully loaded LinkedIn!")
        
        # Wait a moment for the page to fully load
        print("Waiting for page to settle...")
        time.sleep(2)
        
        # Try to click the Reject button (cookie consent)
        print("Looking for Reject button...")
        try:
            # Try multiple selectors to find the reject button
            reject_button = None
            selectors = [
                'button[data-control-name="ga-cookie.consent.deny.v4"]',
                'button[action-type="DENY"]',
                'button.artdeco-global-alert-action:has-text("Reject")',
                'button:has-text("Reject")'
            ]
            
            for selector in selectors:
                try:
                    reject_button = page.locator(selector).first
                    if reject_button.is_visible(timeout=3000):
                        print(f"✅ Found Reject button with selector: {selector}")
                        reject_button.click()
                        print("✅ Clicked Reject button!")
                        time.sleep(1)  # Wait for cookie banner to disappear
                        break
                except:
                    continue
            
            if not reject_button:
                print("ℹ️  No Reject button found (might be already dismissed)")
                
        except Exception as e:
            print(f"ℹ️  Could not find/click Reject button: {e}")
        
        # Click the "Sign in with email" link
        print("Looking for 'Sign in with email' link...")
        try:
            sign_in_selectors = [
                'a[data-test-id="home-hero-sign-in-cta"]',
                'a[data-tracking-control-name="homepage-basic_home-hero-sign-in-cta"]',
                'a.sign-in-form__sign-in-cta',
                'a:has-text("Sign in with email")'
            ]
            
            sign_in_clicked = False
            for selector in sign_in_selectors:
                try:
                    sign_in_link = page.locator(selector).first
                    if sign_in_link.is_visible(timeout=5000):
                        print(f"✅ Found 'Sign in with email' link with selector: {selector}")
                        sign_in_link.click()
                        print("✅ Clicked 'Sign in with email' link!")
                        
                        # Wait for navigation to login page
                        print("Waiting for login page to load...")
                        page.wait_for_load_state('networkidle', timeout=10000)
                        time.sleep(1)
                        sign_in_clicked = True
                        break
                except Exception as inner_e:
                    continue
            
            if not sign_in_clicked:
                print("ℹ️  Could not find 'Sign in with email' link")
                
        except Exception as e:
            print(f"ℹ️  Error clicking sign in link: {e}")
        
        # Fill in login credentials
        print("Filling in login credentials...")
        try:
            # Get credentials from environment variables
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if not email or not password:
                print("⚠️  WARNING: LINKEDIN_EMAIL or LINKEDIN_PASSWORD not found in .env file")
                print("Please edit the .env file and add your credentials.")
            else:
                # Fill in email/username field
                username_selectors = [
                    'input#username',
                    'input[name="session_key"]',
                    'input[autocomplete="username webauthn"]'
                ]
                
                username_filled = False
                for selector in username_selectors:
                    try:
                        username_field = page.locator(selector).first
                        if username_field.is_visible(timeout=5000):
                            print(f"✅ Found username field with selector: {selector}")
                            username_field.fill(email)
                            print(f"✅ Filled in email: {email}")
                            username_filled = True
                            break
                    except:
                        continue
                
                if not username_filled:
                    print("⚠️  Could not find username field")
                
                # Fill in password field
                password_selectors = [
                    'input#password',
                    'input[name="session_password"]',
                    'input[type="password"]'
                ]
                
                password_filled = False
                for selector in password_selectors:
                    try:
                        password_field = page.locator(selector).first
                        if password_field.is_visible(timeout=5000):
                            print(f"✅ Found password field with selector: {selector}")
                            password_field.fill(password)
                            print("✅ Filled in password: ********")
                            password_filled = True
                            break
                    except:
                        continue
                
                if not password_filled:
                    print("⚠️  Could not find password field")
                
                # Small delay to see the filled fields
                time.sleep(1)
                
                if username_filled and password_filled:
                    print("✅ Login form filled successfully!")
                    
                    # Click the Sign in button
                    print("Looking for 'Sign in' button...")
                    try:
                        sign_in_button_selectors = [
                            'button[data-litms-control-urn="login-submit"]',
                            'button[type="submit"]',
                            'button.btn__primary--large',
                            'button:has-text("Sign in")'
                        ]
                        
                        button_clicked = False
                        for selector in sign_in_button_selectors:
                            try:
                                sign_in_button = page.locator(selector).first
                                if sign_in_button.is_visible(timeout=3000):
                                    print(f"✅ Found 'Sign in' button with selector: {selector}")
                                    sign_in_button.click()
                                    print("✅ Clicked 'Sign in' button!")
                                    button_clicked = True
                                    break
                            except Exception as e:
                                print(f"⚠️  Error with selector {selector}: {e}")
                                continue
                        
                        if not button_clicked:
                            print("⚠️  Could not find/click 'Sign in' button")
                        else:
                            # Wait for navigation after login (separate from button click)
                            print("Waiting for login to complete...")
                            try:
                                time.sleep(5)  # Give more time for login
                                page.wait_for_load_state('domcontentloaded', timeout=20000)
                                print("✅ Login completed!")
                            except Exception as wait_e:
                                print(f"⚠️  Timeout waiting for login, but continuing anyway: {wait_e}")
                            
                            # Navigate to jobs search page
                            print("\nNavigating to LinkedIn Jobs Search...")
                            try:
                                page.goto("https://www.linkedin.com/jobs/search/", timeout=60000)
                                print("✅ Navigated to Jobs Search page!")
                                
                                # Wait for page to load
                                page.wait_for_load_state('domcontentloaded', timeout=20000)
                                time.sleep(2)
                                print("✅ Jobs Search page loaded!")
                                
                                # Get the current URL and append search parameters
                                current_url = page.url
                                print(f"\nCurrent URL: {current_url}")
                                
                                # Append search parameters
                                search_params = "&keywords=data%20scientist&location=Stockholm&refresh=true&start=100"
                                new_url = current_url + search_params
                                
                                print(f"Adding search parameters...")
                                print(f"New URL: {new_url}")
                                
                                # Navigate to the URL with search parameters
                                page.goto(new_url, timeout=60000)
                                print("✅ Navigated to search results!")
                                
                                # Wait for results to load
                                page.wait_for_load_state('domcontentloaded', timeout=20000)
                                time.sleep(2)
                                print("✅ Search results loaded!")
                                print(f"Final URL: {page.url}")
                                
                            except Exception as nav_e:
                                print(f"⚠️  Error navigating to jobs page: {nav_e}")
                                print("Current URL:", page.url)
                                
                    except Exception as btn_e:
                        print(f"⚠️  Error in sign in process: {btn_e}")
                        import traceback
                        traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Error filling login form: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("Browser is now open. You can interact with it.")
        print("Press Ctrl+C in this terminal to close.")
        print("="*60 + "\n")
        
        # Keep the browser open
        while True:
            time.sleep(1)
            
except KeyboardInterrupt:
    print("\n\n👋 Closing browser...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("✅ Done!")

