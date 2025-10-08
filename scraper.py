"""
LinkedIn job scraper module using Playwright.
Handles browser automation and job data extraction.
"""

import re
import time
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError


class LinkedInScraper:
    """Scrapes job postings from LinkedIn using Playwright."""
    
    def __init__(self, headless: bool = True, page_load_timeout: int = 30000, 
                 linkedin_email: str = None, linkedin_password: str = None):
        """
        Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode
            page_load_timeout: Page load timeout in milliseconds
            linkedin_email: LinkedIn email for authentication
            linkedin_password: LinkedIn password for authentication
        """
        self.headless = headless
        self.page_load_timeout = page_load_timeout
        self.linkedin_email = linkedin_email
        self.linkedin_password = linkedin_password
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        self.session_file = "linkedin_session.json"
        self.is_logged_in = False
    
    def __enter__(self):
        """Context manager entry."""
        self.playwright = sync_playwright().start()
        
        # Launch browser - prefer WebKit (Safari) on macOS, fallback to Chromium
        try:
            # WebKit is more stable on macOS
            self.browser = self.playwright.webkit.launch(
                headless=self.headless
            )
            print("  🌐 Using WebKit (Safari) engine")
        except Exception as webkit_error:
            print(f"  ⚠️  WebKit unavailable, trying Chromium: {webkit_error}")
            try:
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless
                )
                print("  🌐 Using Chromium engine")
            except Exception as chromium_error:
                print(f"  ❌ Both browsers failed. WebKit: {webkit_error}, Chromium: {chromium_error}")
                raise
        
        # Check if we have a saved session
        context_options = {
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'viewport': {'width': 1920, 'height': 1080}
        }
        
        if Path(self.session_file).exists():
            try:
                context_options['storage_state'] = self.session_file
                print("  🔐 Loading saved LinkedIn session...")
            except:
                print("  ⚠️  Could not load saved session, will login fresh")
        
        # Create browser context with session (if available)
        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()
        
        # Set extra headers to look more like a real browser
        self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        
        self.page.set_default_timeout(self.page_load_timeout)
        
        # Login to LinkedIn if credentials provided
        if self.linkedin_email and self.linkedin_password:
            self._login_to_linkedin()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Save session if logged in
        if self.is_logged_in and self.context:
            try:
                self.context.storage_state(path=self.session_file)
                print("  💾 LinkedIn session saved for next time")
            except Exception as e:
                print(f"  ⚠️  Could not save session: {e}")
        
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _login_to_linkedin(self):
        """
        Log in to LinkedIn using provided credentials.
        """
        try:
            print("  🔐 Attempting LinkedIn login...")
            
            # Go to LinkedIn login page
            self.page.goto("https://www.linkedin.com/login", timeout=30000)
            time.sleep(2)
            
            # Check if already logged in
            if "feed" in self.page.url or "mynetwork" in self.page.url:
                print("  ✅ Already logged in from saved session")
                self.is_logged_in = True
                return
            
            # Fill in email
            email_field = self.page.locator("#username")
            if email_field.count() > 0:
                email_field.fill(self.linkedin_email)
                print("  📧 Email entered")
            else:
                print("  ⚠️  Could not find email field")
                return
            
            # Fill in password
            password_field = self.page.locator("#password")
            if password_field.count() > 0:
                password_field.fill(self.linkedin_password)
                print("  🔑 Password entered")
            else:
                print("  ⚠️  Could not find password field")
                return
            
            # Click sign in button
            sign_in_button = self.page.locator("button[type='submit']")
            if sign_in_button.count() > 0:
                sign_in_button.click()
                print("  🚀 Sign in clicked, waiting for redirect...")
                
                # Wait for navigation with timeout
                try:
                    self.page.wait_for_url(lambda url: "feed" in url or "jobs" in url or "challenge" in url, timeout=10000)
                except:
                    pass
                
                time.sleep(3)  # Additional wait
                
                # Check if login was successful
                current_url = self.page.url
                if "feed" in current_url or "mynetwork" in current_url or "jobs" in current_url:
                    print("  ✅ Successfully logged in to LinkedIn!")
                    self.is_logged_in = True
                elif "challenge" in current_url or "checkpoint" in current_url:
                    print("  ⚠️  LinkedIn security challenge detected!")
                    print("     Set headless=false in config and complete verification manually.")
                    self.is_logged_in = False
                else:
                    print(f"  ⚠️  Login uncertain. Current URL: {current_url[:50]}...")
                    self.is_logged_in = True  # Assume logged in and continue
            else:
                print("  ⚠️  Could not find sign in button")
                
        except Exception as e:
            print(f"  ❌ Login failed: {e}")
            print("     Continuing without authentication...")
    
    def scrape_jobs_from_url(
        self, 
        url: str, 
        max_scroll_attempts: int = 5,
        scroll_delay: float = 2.0
    ) -> List[Dict]:
        """
        Scrape job postings from a LinkedIn search URL.
        
        Args:
            url: LinkedIn job search URL
            max_scroll_attempts: Maximum number of scroll attempts
            scroll_delay: Delay between scrolls in seconds
            
        Returns:
            List of job dictionaries
        """
        print(f"\n🔍 Scraping: {url}")
        
        try:
            # Navigate to the page with a longer timeout
            print("  ⏳ Loading page...")
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Check if we got redirected to login
            current_url = self.page.url
            if "/authwall" in current_url or "/login" in current_url:
                print("  ⚠️  LinkedIn is asking for login. Trying to continue anyway...")
            
            # Wait for job results to appear - try multiple selectors
            print("  ⏳ Waiting for job listings to load...")
            
            # Wait for any of these selectors to appear
            job_list_selectors = [
                ".jobs-search__results-list",
                ".scaffold-layout__list-container",
                ".jobs-search-results-list",
                "ul[class*='jobs']",
                "[data-test-component='jobs-search-results-list']"
            ]
            
            loaded = False
            for selector in job_list_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=10000)
                    print(f"  ✅ Job list loaded (found: {selector})")
                    loaded = True
                    break
                except:
                    continue
            
            if not loaded:
                print("  ⚠️  Job list container not found, waiting longer...")
                time.sleep(5)
                
            else:
                # Give JavaScript time to render the found elements
                time.sleep(2)
            
            # Debug: Save screenshot and HTML only if enabled
            debug_mode = os.getenv('DEBUG_SCRAPER', 'false').lower() == 'true'
            if debug_mode:
                try:
                    timestamp = int(time.time())
                    debug_path = f"debug_logged_in_{timestamp}.png"
                    html_path = f"debug_html_{timestamp}.html"
                    
                    self.page.screenshot(path=debug_path, full_page=True)
                    html_content = self.page.content()
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    print(f"  📸 Debug screenshot: {debug_path}")
                    print(f"  📄 Debug HTML: {html_path}")
                except Exception as e:
                    print(f"  ⚠️  Debug save failed: {e}")
            
            # Scroll to load more jobs
            print("  📜 Scrolling to load more jobs...")
            self._scroll_to_load_jobs(max_scroll_attempts, scroll_delay)
            
            # Extract job data
            print("  📊 Extracting job data...")
            jobs = self._extract_job_cards()
            
            print(f"✅ Found {len(jobs)} jobs from this search")
            return jobs
            
        except PlaywrightTimeoutError as e:
            print(f"⚠️  Timeout while loading: {url}")
            print(f"     {str(e)}")
            self._save_debug_screenshot("timeout_error")
            return []
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            import traceback
            print(f"     Full error: {traceback.format_exc()}")
            self._save_debug_screenshot("scraping_error")
            return []
    
    def _save_debug_screenshot(self, error_type: str):
        """
        Save a screenshot for debugging purposes.
        
        Args:
            error_type: Type of error that occurred
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_screenshot_{error_type}_{timestamp}.png"
            self.page.screenshot(path=filename)
            print(f"  📸 Debug screenshot saved: {filename}")
        except Exception as e:
            print(f"  ⚠️  Could not save screenshot: {e}")
    
    def _scroll_to_load_jobs(self, max_attempts: int, delay: float):
        """
        Scroll the page to trigger lazy loading of job listings.
        
        Args:
            max_attempts: Maximum number of scroll attempts
            delay: Delay between scrolls in seconds
        """
        for i in range(max_attempts):
            try:
                # Scroll to bottom
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(delay)
                
                # Check if we've reached the end
                try:
                    # Look for "end of results" indicator
                    if self.page.locator("text=/No more results/i").count() > 0:
                        print(f"    📄 Reached end of results after {i+1} scrolls")
                        break
                except:
                    pass
            except Exception as e:
                print(f"    ⚠️  Error during scroll {i+1}: {str(e)}")
                break
    
    def _extract_job_cards(self) -> List[Dict]:
        """
        Extract job information from all job cards on the page.
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # LinkedIn uses different selectors for logged-in vs logged-out users
        selectors = [
            ".jobs-search__results-list li",  # Common selector
            ".scaffold-layout__list-container li",  # Logged-in layout
            "li[class*='jobs-search-results__list-item']",
            "ul.jobs-search__results-list > li",
            ".job-card-container",  # Alternative selector
            ".jobs-search-results__list-item",  # Direct class
            "[data-job-id]",  # Has job ID attribute
            "li.ember-view"  # Ember framework used by LinkedIn
        ]
        
        job_cards = None
        for selector in selectors:
            job_cards = self.page.locator(selector).all()
            if job_cards:
                print(f"  📋 Using selector: {selector} (found {len(job_cards)} elements)")
                break
        
        if not job_cards:
            print("  ⚠️  No job cards found with any selector")
            print("  🔍 Debug: Checking page content...")
            
            # Print what's on the page for debugging
            try:
                page_text = self.page.inner_text("body")
                if "sign in" in page_text.lower() or "join now" in page_text.lower():
                    print("  ⚠️  Page seems to require authentication")
                elif "no matching jobs" in page_text.lower():
                    print("  ℹ️  LinkedIn says 'no matching jobs found'")
                else:
                    print(f"  ℹ️  Page loaded, current URL: {self.page.url}")
                    # Try to find any list items at all
                    all_li = self.page.locator("li").all()
                    print(f"  ℹ️  Found {len(all_li)} total <li> elements on page")
            except:
                pass
            
            return jobs
        
        for idx, card in enumerate(job_cards):
            try:
                job_data = self._extract_job_from_card(card)
                if job_data and job_data.get('job_id'):
                    jobs.append(job_data)
            except Exception as e:
                # Skip cards that fail to parse
                continue
        
        return jobs
    
    def _extract_job_from_card(self, card) -> Optional[Dict]:
        """
        Extract job information from a single job card element.
        
        Args:
            card: Playwright Locator for job card
            
        Returns:
            Dictionary with job information or None
        """
        try:
            # Extract job ID from data attribute or link
            job_id = None
            
            # Try data-entity-urn first (LinkedIn's new format)
            try:
                entity_urn = card.locator("[data-entity-urn]").first.get_attribute("data-entity-urn")
                if entity_urn:
                    # Extract ID from urn:li:jobPosting:1234567890
                    match = re.search(r':jobPosting:(\d+)', entity_urn)
                    if match:
                        job_id = match.group(1)
            except:
                pass
            
            # Fallback: try data-job-id attribute
            if not job_id:
                try:
                    job_id = card.get_attribute("data-job-id")
                except:
                    pass
            
            # Fallback: extract from link href
            if not job_id:
                try:
                    link_element = card.locator("a[href*='/jobs/view/']").first
                    if link_element.count() > 0:
                        href = link_element.get_attribute("href")
                        if href:
                            match = re.search(r'/jobs/view/[^/]*?(\d+)', href)
                            if match:
                                job_id = match.group(1)
                except Exception as e:
                    pass
            
            if not job_id:
                return None
            
            # Extract title
            title = ""
            try:
                title_selectors = [
                    ".base-search-card__title",
                    "h3.base-search-card__title",
                    ".job-card-list__title",
                    "a[class*='job-card-container__link'] strong"
                ]
                for selector in title_selectors:
                    title_element = card.locator(selector).first
                    if title_element.count() > 0:
                        title = title_element.inner_text().strip()
                        if title:  # Make sure we got actual text
                            break
            except Exception as e:
                pass
            
            # Extract company
            company = ""
            try:
                company_selectors = [
                    ".base-search-card__subtitle",
                    "h4.base-search-card__subtitle",
                    ".job-card-container__company-name",
                    "a[class*='subtitle']"
                ]
                for selector in company_selectors:
                    company_element = card.locator(selector).first
                    if company_element.count() > 0:
                        company = company_element.inner_text().strip()
                        if company:  # Make sure we got actual text
                            break
            except Exception as e:
                pass
            
            # Extract location
            location = ""
            try:
                location_selectors = [
                    ".base-search-card__metadata",
                    ".job-card-container__metadata-item",
                    "span[class*='metadata']"
                ]
                for selector in location_selectors:
                    location_element = card.locator(selector).first
                    if location_element.count() > 0:
                        location = location_element.inner_text().strip()
                        if location:  # Make sure we got actual text
                            break
            except Exception as e:
                pass
            
            # Extract link
            link = f"https://www.linkedin.com/jobs/view/{job_id}"
            
            # Extract date posted (if available)
            date_posted = ""
            try:
                time_selectors = [
                    "time",
                    ".job-card-container__listed-time",
                    "time[class*='posted']"
                ]
                for selector in time_selectors:
                    time_element = card.locator(selector).first
                    if time_element.count() > 0:
                        date_posted = time_element.get_attribute("datetime") or time_element.inner_text().strip()
                        break
            except:
                pass
            
            return {
                'job_id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'link': link,
                'date_posted': date_posted
            }
            
        except Exception as e:
            return None
    
    def scrape_multiple_searches(
        self, 
        search_urls: List[str],
        max_scroll_attempts: int = 5,
        scroll_delay: float = 2.0
    ) -> List[Dict]:
        """
        Scrape jobs from multiple search URLs.
        
        Args:
            search_urls: List of LinkedIn job search URLs
            max_scroll_attempts: Maximum scroll attempts per search
            scroll_delay: Delay between scrolls in seconds
            
        Returns:
            Combined list of all jobs found
        """
        all_jobs = []
        
        for idx, url in enumerate(search_urls):
            jobs = self.scrape_jobs_from_url(url, max_scroll_attempts, scroll_delay)
            all_jobs.extend(jobs)
            
            # Add delay between searches to avoid rate limiting
            if idx < len(search_urls) - 1:  # Don't delay after last search
                delay = 3
                print(f"\n  ⏸️  Waiting {delay}s before next search (rate limiting)...")
                time.sleep(delay)
        
        # Remove duplicates based on job_id
        unique_jobs = {}
        for job in all_jobs:
            job_id = job.get('job_id')
            if job_id and job_id not in unique_jobs:
                unique_jobs[job_id] = job
        
        return list(unique_jobs.values())

