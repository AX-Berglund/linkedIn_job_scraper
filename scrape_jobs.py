#!/usr/bin/env python3
"""
Main script to scrape LinkedIn jobs and update the database.

This script:
1. Reads search URLs from config.json
2. Scrapes job postings from LinkedIn
3. Updates the SQLite database:
   - Adds new jobs
   - Updates last_seen for existing jobs
   - Marks missing jobs as expired
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

from database import JobDatabase
from scraper import LinkedInScraper

# Load environment variables from .env file
load_dotenv()


def build_linkedin_url(keywords: str, location: str) -> str:
    """
    Build a LinkedIn job search URL from keywords and location.
    
    Args:
        keywords: Job search keywords (e.g., "data scientist")
        location: Job location (e.g., "Stockholm")
        
    Returns:
        Full LinkedIn job search URL
    """
    base_url = "https://www.linkedin.com/jobs/search/"
    # LinkedIn uses + for spaces (form encoding style)
    params = f"?keywords={quote_plus(keywords)}&location={quote_plus(location)}"
    return base_url + params


def parse_search_config(search_item) -> str:
    """
    Parse a search configuration item and return a LinkedIn URL.
    
    Args:
        search_item: Either a dict with 'keywords' and 'location', or a URL string
        
    Returns:
        LinkedIn job search URL
        
    Raises:
        ValueError: If the search item is invalid
    """
    # Handle new format: {"keywords": "...", "location": "..."}
    if isinstance(search_item, dict):
        if 'keywords' not in search_item or 'location' not in search_item:
            raise ValueError(
                "Search object must contain both 'keywords' and 'location' fields.\n"
                f"Example: {{'keywords': 'data scientist', 'location': 'Stockholm'}}"
            )
        return build_linkedin_url(search_item['keywords'], search_item['location'])
    
    # Handle old format: direct URL string
    elif isinstance(search_item, str):
        if not search_item.startswith('http'):
            raise ValueError(f"Invalid URL: {search_item}")
        return search_item
    
    else:
        raise ValueError(f"Invalid search item type: {type(search_item)}")


def load_config(config_path: str = "config.json") -> dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please create a config.json file with your LinkedIn search URLs."
        )
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if 'searches' not in config or not config['searches']:
        raise ValueError(
            "Config file must contain a 'searches' array with at least one search.\n"
            "Example:\n"
            '{\n'
            '  "searches": [\n'
            '    {"keywords": "data scientist", "location": "Stockholm"}\n'
            '  ]\n'
            '}'
        )
    
    return config


def print_header():
    """Print a nice header for the script."""
    print("\n" + "="*60)
    print("🔗 LinkedIn Job Scraper")
    print("="*60)
    print(f"⏰ Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


def print_summary(stats: dict, new_count: int, updated_count: int, expired_count: int):
    """
    Print summary statistics.
    
    Args:
        stats: Database statistics
        new_count: Number of new jobs added
        updated_count: Number of jobs updated
        expired_count: Number of jobs marked as expired
    """
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    print(f"  New jobs added:      {new_count}")
    print(f"  Jobs updated:        {updated_count}")
    print(f"  Jobs expired:        {expired_count}")
    print("\n" + "-"*60)
    print(f"  Total jobs in DB:    {stats['total']}")
    print(f"  Active jobs:         {stats['active']}")
    print(f"  Expired jobs:        {stats['expired']}")
    print(f"  Applied to:          {stats['applied']}")
    print(f"  Not yet applied:     {stats['not_applied']}")
    print("="*60 + "\n")


def main():
    """Main execution function."""
    try:
        print_header()
        
        # Load configuration
        print("\n📄 Loading configuration...")
        config = load_config()
        search_configs = config['searches']
        scrape_settings = config.get('scrape_settings', {})
        
        # Parse search configurations and build URLs
        search_urls = []
        print(f"✅ Loaded {len(search_configs)} search(es):")
        for idx, search_item in enumerate(search_configs, 1):
            url = parse_search_config(search_item)
            search_urls.append(url)
            
            # Display in user-friendly format
            if isinstance(search_item, dict):
                print(f"   {idx}. {search_item['keywords']} in {search_item['location']}")
            else:
                print(f"   {idx}. {url}")
        
        # Initialize database
        print("\n💾 Initializing database...")
        db = JobDatabase()
        print("✅ Database ready")
        
        # Get existing job IDs before scraping
        existing_jobs_before = db.get_all_active_job_ids()
        print(f"📊 Currently tracking {len(existing_jobs_before)} active jobs")
        
        # Load LinkedIn credentials from environment
        linkedin_email = os.getenv('LINKEDIN_EMAIL')
        linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        auto_login = os.getenv('LINKEDIN_AUTO_LOGIN', 'false').lower() == 'true'
        
        if auto_login and linkedin_email and linkedin_password:
            print("🔐 Auto-login enabled")
        elif auto_login:
            print("⚠️  Auto-login enabled but credentials not found in .env file")
            linkedin_email = linkedin_password = None
        else:
            linkedin_email = linkedin_password = None
        
        # Scrape jobs
        print("\n🌐 Starting web scraper...")
        with LinkedInScraper(
            headless=scrape_settings.get('headless', True),
            page_load_timeout=scrape_settings.get('page_load_timeout_ms', 30000),
            linkedin_email=linkedin_email,
            linkedin_password=linkedin_password
        ) as scraper:
            jobs = scraper.scrape_multiple_searches(
                search_urls,
                max_scroll_attempts=scrape_settings.get('max_scroll_attempts', 5),
                scroll_delay=scrape_settings.get('scroll_delay_ms', 2000) / 1000
            )
        
        print(f"\n✅ Scraping complete: Found {len(jobs)} total jobs")
        
        # Process scraped jobs
        print("\n💾 Updating database...")
        new_count = 0
        updated_count = 0
        scraped_job_ids = set()
        
        for job in jobs:
            job_id = job['job_id']
            scraped_job_ids.add(job_id)
            
            # Try to insert new job
            if db.insert_job(job):
                new_count += 1
                print(f"  ➕ New: {job['title']} at {job['company']}")
            else:
                # Job exists, update last_seen
                db.update_last_seen(job_id)
                updated_count += 1
        
        # Mark jobs as expired if they're no longer in the search results
        expired_job_ids = existing_jobs_before - scraped_job_ids
        expired_count = db.mark_jobs_as_expired(list(expired_job_ids))
        
        if expired_count > 0:
            print(f"\n  ⏳ Marked {expired_count} job(s) as expired")
        
        # Get final statistics
        stats = db.get_job_stats()
        
        # Print summary
        print_summary(stats, new_count, updated_count, expired_count)
        
        print("✅ Job scraping completed successfully!")
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

