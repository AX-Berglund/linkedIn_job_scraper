#!/usr/bin/env python3
"""
Simple browser test - Just opens Chrome and goes to LinkedIn.
Use this to verify Playwright is working on your system.
"""

from playwright.sync_api import sync_playwright
import time
import os
import re
from dotenv import load_dotenv
from database import JobDatabase

# Load environment variables from .env file
load_dotenv()

def extract_job_id(job_url: str) -> str:
    """Extract job ID from LinkedIn job URL."""
    match = re.search(r'/jobs/view/(\d+)', job_url)
    if match:
        return match.group(1)
    # Try alternative format
    match = re.search(r'currentJobId=(\d+)', job_url)
    if match:
        return match.group(1)
    return None


def scrape_jobs_from_page(page):
    """
    Scrape job information from the current LinkedIn jobs page.
    
    Args:
        page: Playwright page object
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    try:
        # Try multiple selectors for the job list container
        job_list_selectors = [
            '.jobs-search__results-list',
            '.scaffold-layout__list-container',
            'ul.jobs-search-results__list',
            '[data-job-search-results]'
        ]
        
        for selector in job_list_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                print(f"  ✅ Found job list with selector: {selector}")
                break
            except:
                continue
        
        time.sleep(3)  # Let the page fully settle
        
        # Try multiple selectors for job cards
        job_card_selectors = [
            'li.jobs-search-results__list-item',
            'li[data-occludable-job-id]',
            'div.job-card-container',
            'li.scaffold-layout__list-item'
        ]
        
        job_cards = None
        for selector in job_card_selectors:
            cards = page.locator(selector).all()
            if len(cards) > 0:
                job_cards = cards
                print(f"  📋 Found {len(job_cards)} job cards with selector: {selector}")
                break
        
        if not job_cards:
            print("  ⚠️  Could not find any job cards")
            return jobs
        
        for idx, card in enumerate(job_cards, 1):
            try:
                # Try to get job ID from data attribute first
                job_id = card.get_attribute('data-occludable-job-id')
                
                # Extract job link - try multiple selectors
                job_link_selectors = [
                    'a.job-card-list__title',
                    'a.job-card-container__link',
                    'a[href*="/jobs/view/"]',
                    'a.scaffold-layout__list-link'
                ]
                
                job_link = None
                job_url = None
                title = None
                
                for link_selector in job_link_selectors:
                    try:
                        link = card.locator(link_selector).first
                        if link.count() > 0:
                            job_link = link
                            job_url = link.get_attribute('href')
                            # Prefer aria-label to avoid duplicate text from multiple spans
                            title = link.get_attribute('aria-label')
                            if not title or len(title) == 0:
                                try:
                                    # Fallback to inner text, but clean it up
                                    title = link.inner_text().strip()
                                    # Remove duplicate text (sometimes title appears twice)
                                    words = title.split('\n')
                                    if len(words) > 1 and words[0].strip() == words[1].strip():
                                        title = words[0].strip()
                                except:
                                    title = "Unknown Title"
                            
                            # Clean up common artifacts
                            if title:
                                # Remove "with verification" and similar artifacts
                                title = title.replace(' with verification', '')
                                title = title.replace('\nwith verification', '')
                                # Remove extra whitespace and newlines
                                title = ' '.join(title.split())
                            
                            break
                    except:
                        continue
                
                if not job_url:
                    continue
                
                # Extract job ID if not found in data attribute
                if not job_id:
                    job_id = extract_job_id(job_url)
                if not job_id:
                    print(f"    ⚠️  Could not extract job ID")
                    continue
                
                # Extract company name - try multiple selectors
                company_selectors = [
                    'div.artdeco-entity-lockup__subtitle',  # Most common - company name is here
                    '.artdeco-entity-lockup__subtitle',
                    '.job-card-container__primary-description',
                    '.job-card-container__company-name',
                    'span.job-card-container__company-name',
                    'a[data-test-id="job-card-company-name"]',
                    'span[class*="company"]',
                    'div[class*="company"]'
                ]
                company = "Unknown"
                for comp_selector in company_selectors:
                    try:
                        comp_elem = card.locator(comp_selector).first
                        if comp_elem.count() > 0:
                            company = comp_elem.inner_text().strip()
                            # Clean up company name
                            if company:
                                company = ' '.join(company.split())  # Remove extra whitespace
                                company = company.replace(' with verification', '')
                            if company and company != "Unknown" and len(company) > 0:
                                break
                    except:
                        continue
                
                # If still unknown, try to get from any text that looks like a company
                if company == "Unknown":
                    try:
                        # Look for any div or span that might contain company info
                        all_text_elems = card.locator('span, div').all()
                        for elem in all_text_elems[:20]:  # Check first 20 elements
                            try:
                                text = elem.inner_text().strip()
                                # Skip if it's the title or empty
                                if text and text != title and len(text) > 2 and len(text) < 100:
                                    # Check if it looks like a company name (not a location, not a date)
                                    if not any(x in text.lower() for x in ['ago', 'promoted', 'matches', 'applicant', 'easy apply']):
                                        company = text
                                        break
                            except:
                                continue
                    except:
                        pass
                
                # Extract location - try multiple selectors
                location_selectors = [
                    'div.artdeco-entity-lockup__caption ul li',  # Most common - location is in caption
                    '.artdeco-entity-lockup__caption li',
                    '.job-card-container__metadata-item',
                    'li.job-card-container__metadata-item',
                    'ul.job-card-container__metadata-wrapper li',
                    'span[class*="location"]'
                ]
                location = "Unknown"
                for loc_selector in location_selectors:
                    try:
                        loc_elem = card.locator(loc_selector).first
                        if loc_elem.count() > 0:
                            location = loc_elem.inner_text().strip()
                            # Clean up location
                            if location:
                                location = ' '.join(location.split())  # Remove extra whitespace
                            if location and len(location) > 0:
                                break
                    except:
                        continue
                
                # Extract posted date (if available)
                posted_date = None
                try:
                    posted_elem = card.locator('time')
                    if posted_elem.count() > 0:
                        posted_date = posted_elem.first.get_attribute('datetime')
                except:
                    pass
                
                # Make sure we have minimum required data
                if not title or title == "Unknown Title":
                    print(f"    ⚠️  Skipping job {idx} - no title found")
                    continue
                
                job_data = {
                    'job_id': job_id,
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': f"https://www.linkedin.com/jobs/view/{job_id}",  # Database expects 'link' not 'url'
                    'date_posted': posted_date,
                    'description': '',  # Would need to click into job to get full description
                    'search_url': page.url
                }
                
                jobs.append(job_data)
                print(f"    ✅ {idx}. {title[:50]}{'...' if len(title) > 50 else ''} at {company}")
                
            except Exception as e:
                print(f"    ⚠️  Error extracting job {idx}: {e}")
                continue
        
    except Exception as e:
        print(f"  ❌ Error scraping page: {e}")
    
    return jobs


print("="*60)
print("🔗 LinkedIn Job Scraper with Browser")
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
                                
                                # Initialize database
                                print("\n💾 Initializing database...")
                                db = JobDatabase()
                                print("✅ Database ready")
                                
                                # Start scraping jobs with pagination
                                print("\n🔍 Starting job scraping...")
                                all_jobs = []
                                start_value = 0
                                page_increment = 50
                                max_pages = 10  # Safety limit - scrape max 10 pages (500 jobs)
                                pages_scraped = 0
                                
                                # Get the base URL (without start parameter)
                                base_url = page.url.split('&start=')[0] if '&start=' in page.url else page.url
                                
                                for page_num in range(max_pages):
                                    print(f"\n📄 Scraping page {page_num + 1} (start={start_value})...")
                                    
                                    # Build URL with current start value
                                    if '?' in base_url:
                                        current_url = f"{base_url}&start={start_value}"
                                    else:
                                        current_url = f"{base_url}?start={start_value}"
                                    
                                    # Navigate to page
                                    try:
                                        page.goto(current_url, timeout=60000)
                                        page.wait_for_load_state('domcontentloaded', timeout=20000)
                                        time.sleep(2)
                                    except Exception as page_nav_e:
                                        print(f"  ⚠️  Error navigating to page: {page_nav_e}")
                                        break
                                    
                                    # Scrape jobs from current page
                                    jobs_on_page = scrape_jobs_from_page(page)
                                    
                                    if not jobs_on_page:
                                        print("  ℹ️  No jobs found on this page. Reached end of results.")
                                        break
                                    
                                    all_jobs.extend(jobs_on_page)
                                    pages_scraped += 1
                                    
                                    # Save to database
                                    print(f"  💾 Saving {len(jobs_on_page)} jobs to database...")
                                    new_count = 0
                                    updated_count = 0
                                    
                                    for job in jobs_on_page:
                                        if db.insert_job(job):
                                            new_count += 1
                                        else:
                                            db.update_last_seen(job['job_id'])
                                            updated_count += 1
                                    
                                    print(f"  ✅ Page {page_num + 1}: {new_count} new, {updated_count} updated")
                                    
                                    # Move to next page
                                    start_value += page_increment
                                    
                                    # Small delay between pages
                                    time.sleep(2)
                                
                                # Print summary
                                print("\n" + "="*60)
                                print("📊 Scraping Summary")
                                print("="*60)
                                print(f"  Pages scraped:       {pages_scraped}")
                                print(f"  Total jobs found:    {len(all_jobs)}")
                                
                                stats = db.get_job_stats()
                                print(f"\n  Total in database:   {stats['total']}")
                                print(f"  Active jobs:         {stats['active']}")
                                print(f"  Applied to:          {stats['applied']}")
                                print("="*60)
                                
                            except Exception as nav_e:
                                print(f"⚠️  Error in job scraping process: {nav_e}")
                                print(f"Current URL: {page.url}")
                                import traceback
                                traceback.print_exc()
                                
                    except Exception as btn_e:
                        print(f"⚠️  Error in sign in process: {btn_e}")
                        import traceback
                        traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Error filling login form: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("✅ Scraping complete!")
        print("Browser will stay open for 10 seconds for you to review...")
        print("Press Ctrl+C to close immediately.")
        print("="*60 + "\n")
        
        # Keep the browser open for review
        for i in range(10, 0, -1):
            print(f"  Closing in {i} seconds...", end='\r')
            time.sleep(1)
        print("\n👋 Closing browser...")        
            
except KeyboardInterrupt:
    print("\n\n👋 Closing browser...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("✅ Done!")

