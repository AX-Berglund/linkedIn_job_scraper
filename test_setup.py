#!/usr/bin/env python3
"""
Test script to verify the setup is working correctly.
Runs a quick check of all components without scraping LinkedIn.
"""

import sys
import json
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import playwright
        print("  ✅ Playwright installed")
    except ImportError:
        print("  ❌ Playwright not installed")
        print("     Run: pip install -r requirements.txt")
        return False
    
    try:
        from database import JobDatabase
        print("  ✅ Database module OK")
    except ImportError as e:
        print(f"  ❌ Cannot import database module: {e}")
        return False
    
    try:
        from scraper import LinkedInScraper
        print("  ✅ Scraper module OK")
    except ImportError as e:
        print(f"  ❌ Cannot import scraper module: {e}")
        return False
    
    return True


def test_config():
    """Test that config file exists and is valid."""
    print("\n📄 Testing config file...")
    
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("  ❌ config.json not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("  ✅ config.json is valid JSON")
    except json.JSONDecodeError as e:
        print(f"  ❌ config.json is not valid JSON: {e}")
        return False
    
    if 'searches' not in config:
        print("  ❌ config.json missing 'searches' key")
        return False
    
    if not config['searches']:
        print("  ⚠️  'searches' array is empty - add your LinkedIn search URLs")
        return False
    
    print(f"  ✅ Found {len(config['searches'])} search URL(s)")
    
    return True


def test_database():
    """Test database initialization."""
    print("\n💾 Testing database...")
    
    try:
        from database import JobDatabase
        db = JobDatabase("test_jobs.db")
        print("  ✅ Database created successfully")
        
        # Test insert
        test_job = {
            'job_id': 'test123',
            'title': 'Test Job',
            'company': 'Test Company',
            'location': 'Test Location',
            'link': 'https://example.com',
            'date_posted': '2025-10-08'
        }
        
        db.insert_job(test_job)
        print("  ✅ Test job inserted")
        
        # Test stats
        stats = db.get_job_stats()
        print(f"  ✅ Stats retrieved: {stats}")
        
        # Clean up
        import os
        os.remove("test_jobs.db")
        print("  ✅ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_playwright_browser():
    """Test that Playwright browsers are installed."""
    print("\n🌐 Testing Playwright browser...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("about:blank")
            page.close()
            browser.close()
        
        print("  ✅ Chromium browser working")
        return True
        
    except Exception as e:
        print(f"  ❌ Browser test failed: {e}")
        print("     Run: playwright install chromium")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 LinkedIn Job Scraper - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Config", test_config),
        ("Database", test_database),
        ("Browser", test_playwright_browser),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name} test: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n" + "-" * 60)
    print(f"  {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✅ All tests passed! You're ready to run the scraper.")
        print("   Run: python scrape_jobs.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

