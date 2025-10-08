#!/usr/bin/env python3
"""
LinkedIn Job Scraper
Automated scraper that logs into LinkedIn, searches for jobs, and saves them to a database.
"""

from playwright.sync_api import sync_playwright, Page
import time
import os
import re
from dotenv import load_dotenv
from database import JobDatabase

# Load environment variables from .env file
load_dotenv()

# Configuration
SEARCH_KEYWORDS = "data scientist"
SEARCH_LOCATION = "Stockholm"
MAX_PAGES = 3  # Maximum number of pages to scrape
PAGE_INCREMENT = 50  # LinkedIn pagination increment


def extract_job_id(job_url: str) -> str:
    """
    Extract job ID from LinkedIn job URL.
    
    Args:
        job_url: LinkedIn job URL
        
    Returns:
        Job ID string or None if not found
    """
    match = re.search(r'/jobs/view/(\d+)', job_url)
    if match:
        return match.group(1)
    # Try alternative format
    match = re.search(r'currentJobId=(\d+)', job_url)
    if match:
        return match.group(1)
    return None


def handle_cookie_consent(page: Page) -> None:
    """
    Handle LinkedIn cookie consent popup by clicking 'Reject'.
    
    Args:
        page: Playwright page object
    """
    print("Looking for Reject button...")
    try:
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
                    time.sleep(1)
                    return
            except:
                continue
        
        print("ℹ️  No Reject button found (might be already dismissed)")
    except Exception as e:
        print(f"ℹ️  Could not find/click Reject button: {e}")


def click_sign_in_link(page: Page) -> bool:
    """
    Click the 'Sign in with email' link on LinkedIn homepage.
    
    Args:
        page: Playwright page object
        
    Returns:
        True if successfully clicked, False otherwise
    """
    print("Looking for 'Sign in with email' link...")
    try:
        selectors = [
            'a[data-test-id="home-hero-sign-in-cta"]',
            'a[data-tracking-control-name="homepage-basic_home-hero-sign-in-cta"]',
            'a.sign-in-form__sign-in-cta',
            'a:has-text("Sign in with email")'
        ]
        
        for selector in selectors:
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
                    return True
            except:
                continue
        
        print("ℹ️  Could not find 'Sign in with email' link")
        return False
    except Exception as e:
        print(f"ℹ️  Error clicking sign in link: {e}")
        return False


def fill_login_credentials(page: Page, email: str, password: str) -> tuple[bool, bool]:
    """
    Fill in email and password on LinkedIn login form.
    
    Args:
        page: Playwright page object
        email: LinkedIn email address
        password: LinkedIn password
        
    Returns:
        Tuple of (username_filled, password_filled) booleans
    """
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
                
    return username_filled, password_filled


def click_sign_in_button(page: Page) -> bool:
    """
    Click the 'Sign in' button to submit login form.
    
    Args:
        page: Playwright page object
        
    Returns:
        True if button clicked successfully, False otherwise
    """
    print("Looking for 'Sign in' button...")
    try:
        selectors = [
            'button[data-litms-control-urn="login-submit"]',
            'button[type="submit"]',
            'button.btn__primary--large',
            'button:has-text("Sign in")'
        ]
        
        for selector in selectors:
            try:
                sign_in_button = page.locator(selector).first
                if sign_in_button.is_visible(timeout=3000):
                    print(f"✅ Found 'Sign in' button with selector: {selector}")
                    sign_in_button.click()
                    print("✅ Clicked 'Sign in' button!")
                    return True
            except Exception as e:
                print(f"⚠️  Error with selector {selector}: {e}")
                continue
        
        print("⚠️  Could not find/click 'Sign in' button")
        return False
    except Exception as e:
        print(f"⚠️  Error clicking sign in button: {e}")
        return False


def wait_for_login(page: Page) -> None:
    """
    Wait for login process to complete.
    
    Args:
        page: Playwright page object
    """
    print("Waiting for login to complete...")
    try:
        time.sleep(5)
        page.wait_for_load_state('domcontentloaded', timeout=20000)
        print("✅ Login completed!")
    except Exception as e:
        print(f"⚠️  Timeout waiting for login, but continuing anyway: {e}")


def navigate_to_jobs_search(page: Page, keywords: str, location: str) -> str:
    """
    Navigate to LinkedIn jobs search page with specified keywords and location.
    
    Args:
        page: Playwright page object
        keywords: Job search keywords
        location: Job location
        
    Returns:
        Final URL after navigation
    """
    print("\nNavigating to LinkedIn Jobs Search...")
    page.goto("https://www.linkedin.com/jobs/search/", timeout=60000)
    print("✅ Navigated to Jobs Search page!")
    
    # Wait for page to load
    page.wait_for_load_state('domcontentloaded', timeout=20000)
    time.sleep(2)
    print("✅ Jobs Search page loaded!")
    
    # Get the current URL and append search parameters
    current_url = page.url
    print(f"\nCurrent URL: {current_url}")
    
    # Build search parameters
    keywords_encoded = keywords.replace(' ', '%20')
    location_encoded = location.replace(' ', '%20')
    search_params = f"&keywords={keywords_encoded}&location={location_encoded}&refresh=true"
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
    
    return page.url


def extract_job_from_card(card, page_url: str, debug: bool = False) -> dict:
    """
    Extract job information from a single job card element.
    
    Args:
        card: Playwright locator for job card
        page_url: Current page URL for reference
        debug: If True, print detailed error messages
        
    Returns:
        Dictionary with job information or None if extraction fails
    """
    try:
        # Extract job ID from data attribute
        job_id = card.get_attribute('data-occludable-job-id')
        
        # Extract job link and title
        job_link_selectors = [
            'a.job-card-list__title',
            'a.job-card-container__link',
            'a[href*="/jobs/view/"]',
            'a.scaffold-layout__list-link'
        ]
        
        job_url = None
        title = None
        
        for link_selector in job_link_selectors:
            try:
                link = card.locator(link_selector).first
                if link.count() > 0:
                    job_url = link.get_attribute('href')
                    # Prefer aria-label to avoid duplicate text
                    title = link.get_attribute('aria-label')
                    if not title or len(title) == 0:
                        # Fallback to inner text
                        title = link.inner_text().strip()
                        # Remove duplicate text if present
                        words = title.split('\n')
                        if len(words) > 1 and words[0].strip() == words[1].strip():
                            title = words[0].strip()
                    
                    # Clean up title
                    if title:
                        title = title.replace(' with verification', '')
                        title = title.replace('\nwith verification', '')
                        title = ' '.join(title.split())
                    break
            except:
                continue
        
        if not job_url:
            if debug:
                print(f"      DEBUG: No job URL found")
            return None
        
        if not title or title == "Unknown Title":
            if debug:
                print(f"      DEBUG: No title found (job_url: {job_url[:50]}...)")
            return None
        
        # Extract job ID if not found in data attribute
        if not job_id:
            job_id = extract_job_id(job_url)
        if not job_id:
            if debug:
                print(f"      DEBUG: Could not extract job_id from URL: {job_url[:50]}...")
            return None
        
        # Extract company name
        company_selectors = [
            'div.artdeco-entity-lockup__subtitle',
            '.artdeco-entity-lockup__subtitle',
            '.job-card-container__primary-description',
            '.job-card-container__company-name'
        ]
        
        company = "Unknown"
        for selector in company_selectors:
            try:
                elem = card.locator(selector).first
                if elem.count() > 0:
                    company = elem.inner_text().strip()
                    if company:
                        company = ' '.join(company.split())
                        company = company.replace(' with verification', '')
                    if company and company != "Unknown" and len(company) > 0:
                        break
            except:
                continue
        
        # Extract location
        location_selectors = [
            'div.artdeco-entity-lockup__caption ul li',
            '.artdeco-entity-lockup__caption li',
            '.job-card-container__metadata-item'
        ]
        
        location = "Unknown"
        for selector in location_selectors:
            try:
                elem = card.locator(selector).first
                if elem.count() > 0:
                    location = elem.inner_text().strip()
                    if location:
                        location = ' '.join(location.split())
                    if location and len(location) > 0:
                        break
            except:
                continue
        
        # Extract posted date
        posted_date = None
        try:
            posted_elem = card.locator('time')
            if posted_elem.count() > 0:
                posted_date = posted_elem.first.get_attribute('datetime')
        except:
            pass
        
        return {
            'job_id': job_id,
            'title': title,
            'company': company,
            'location': location,
            'link': f"https://www.linkedin.com/jobs/view/{job_id}",
            'date_posted': posted_date,
            'description': '',
            'search_url': page_url
        }
    except Exception as e:
        if debug:
            print(f"      DEBUG: Exception extracting job: {e}")
        return None


def scrape_jobs_from_page(page: Page) -> list:
    """
    Scrape all job postings from the current page.
    
    Args:
        page: Playwright page object
        
    Returns:
        List of job dictionaries
    """
    jobs = []
    
    try:
        # Wait for job list to load
        job_list_selectors = [
            '.jobs-search__results-list',
            '.scaffold-layout__list-container',
            'ul.jobs-search-results__list'
        ]
        
        for selector in job_list_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                print(f"  ✅ Found job list with selector: {selector}")
                break
            except:
                continue
        
        time.sleep(3)  # Let page fully settle
        
        # Find all job cards first
        print("  🔄 Loading all job cards...")
        
        # Find all job cards
        job_card_selectors = [
            'li[data-occludable-job-id]',
            'li.jobs-search-results__list-item',
            'div.job-card-container'
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
        
        # Scroll through each job card to trigger lazy loading
        print(f"  📜 Scrolling through {len(job_cards)} cards to trigger lazy loading...")
        for idx, card in enumerate(job_cards):
            try:
                # Scroll the card into view
                card.scroll_into_view_if_needed()
                # Small delay to let content load
                time.sleep(0.3)
            except Exception as e:
                # If scrolling fails, continue anyway
                pass
        
        print(f"  ✅ Finished scrolling, waiting for content to load...")
        time.sleep(2)  # Give extra time for any final loading
        
        # Extract information from each job card
        failed_count = 0
        for idx, card in enumerate(job_cards, 1):
            # Enable debug for first 3 failed extractions
            debug = (failed_count < 3)
            job_data = extract_job_from_card(card, page.url, debug=debug)
            if job_data:
                jobs.append(job_data)
                title_display = job_data['title'][:50] + ('...' if len(job_data['title']) > 50 else '')
                print(f"    ✅ {idx}. {title_display} at {job_data['company']}")
            else:
                failed_count += 1
                print(f"    ⚠️  Skipping job {idx} - could not extract data")
    
    except Exception as e:
        print(f"  ❌ Error scraping page: {e}")
    
    return jobs


def save_jobs_to_database(jobs: list, db: JobDatabase) -> tuple[int, int]:
    """
    Save scraped jobs to database.
    
    Args:
        jobs: List of job dictionaries
        db: JobDatabase instance
        
    Returns:
        Tuple of (new_count, updated_count)
    """
    new_count = 0
    updated_count = 0
    
    for job in jobs:
        if db.insert_job(job):
            new_count += 1
        else:
            db.update_last_seen(job['job_id'])
            updated_count += 1
    
    return new_count, updated_count


def scrape_multiple_pages(page: Page, base_url: str, db: JobDatabase, 
                         max_pages: int, page_increment: int) -> list:
    """
    Scrape jobs from multiple pages with pagination.
    
    Args:
        page: Playwright page object
        base_url: Base URL for pagination
        db: JobDatabase instance
        max_pages: Maximum number of pages to scrape
        page_increment: Number to increment 'start' parameter by
        
    Returns:
        List of all scraped jobs
    """
    all_jobs = []
    start_value = 0
    pages_scraped = 0
    
    # Remove existing start parameter from base URL
    base_url = base_url.split('&start=')[0] if '&start=' in base_url else base_url
    
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
        except Exception as e:
            print(f"  ⚠️  Error navigating to page: {e}")
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
        new_count, updated_count = save_jobs_to_database(jobs_on_page, db)
        print(f"  ✅ Page {page_num + 1}: {new_count} new, {updated_count} updated")
        
        # Move to next page
        start_value += page_increment
        time.sleep(2)  # Delay between pages
    
    return all_jobs

                                    
def print_summary(all_jobs: list, db: JobDatabase) -> None:
    """
    Print scraping summary statistics.
    
    Args:
        all_jobs: List of all scraped jobs
        db: JobDatabase instance
    """
    print("\n" + "="*60)
    print("📊 Scraping Summary")
    print("="*60)
    print(f"  Total jobs found:    {len(all_jobs)}")
    
    stats = db.get_job_stats()
    print(f"\n  Total in database:   {stats['total']}")
    print(f"  Active jobs:         {stats['active']}")
    print(f"  Applied to:          {stats['applied']}")
    print("="*60)
                                

def login_to_linkedin(page: Page) -> bool:
    """
    Complete LinkedIn login process.
    
    Args:
        page: Playwright page object
        
    Returns:
        True if login successful, False otherwise
    """
    # Handle cookie consent
    handle_cookie_consent(page)
    
    # Click sign in link
    if not click_sign_in_link(page):
        return False
    
    # Get credentials
    print("Filling in login credentials...")
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("⚠️  WARNING: LINKEDIN_EMAIL or LINKEDIN_PASSWORD not found in .env file")
        print("Please create a .env file with your credentials.")
        return False
    
    # Fill in credentials
    username_filled, password_filled = fill_login_credentials(page, email, password)
    
    if not (username_filled and password_filled):
        print("⚠️  Could not fill in login credentials")
        return False
    
    print("✅ Login form filled successfully!")
    
    # Click sign in button
    if not click_sign_in_button(page):
        return False
    
    # Wait for login to complete
    wait_for_login(page)
    
    return True


def main():
    """Main execution function."""
    print("="*60)
    print("🔗 LinkedIn Job Scraper")
    print("="*60)
    print(f"\nSearching for: {SEARCH_KEYWORDS}")
    print(f"Location: {SEARCH_LOCATION}")
    print(f"Max pages: {MAX_PAGES}\n")
    
    try:
        with sync_playwright() as p:
            # Launch browser
            print("Starting Chrome...")
            try:
                browser = p.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled'
                    ]
                )
                print("✅ Using system Chrome")
            except Exception as e:
                print(f"⚠️  Could not use system Chrome: {e}")
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
            
            # Create page
            print("Creating new page...")
            page = browser.new_page()
            print("✅ Page created successfully!")
            
            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com", timeout=60000)
            print("✅ Successfully loaded LinkedIn!")
            
            time.sleep(2)
            
            # Login to LinkedIn
            if not login_to_linkedin(page):
                print("❌ Login failed")
                return
            
            # Navigate to jobs search
            final_url = navigate_to_jobs_search(page, SEARCH_KEYWORDS, SEARCH_LOCATION)
            
            # Initialize database
            print("\n💾 Initializing database...")
            db = JobDatabase()
            print("✅ Database ready")
            
            # Scrape jobs with pagination
            print("\n🔍 Starting job scraping...")
            all_jobs = scrape_multiple_pages(page, final_url, db, MAX_PAGES, PAGE_INCREMENT)
            
            # Print summary
            print_summary(all_jobs, db)
            
            # Keep browser open briefly
            print("\n✅ Scraping complete!")
            print("Browser will close in 10 seconds...")
            for i in range(10, 0, -1):
                print(f"  Closing in {i} seconds...", end='\r')
                time.sleep(1)
            print("\n👋 Closing browser...")        
            
    except KeyboardInterrupt:
        print("\n\n👋 User interrupted - closing browser...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("✅ Done!")


if __name__ == "__main__":
    main()
