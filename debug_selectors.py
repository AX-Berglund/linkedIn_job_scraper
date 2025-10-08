#!/usr/bin/env python3
"""
Debug script to test LinkedIn selectors and see what's actually on the page.
"""

from playwright.sync_api import sync_playwright
import time

url = "https://www.linkedin.com/jobs/search/?keywords=DATA%20SCIENTIST&location=Stockholm"

print("🔍 Debugging LinkedIn selectors...\n")

with sync_playwright() as p:
    browser = p.webkit.launch(headless=False)
    page = browser.new_page()
    
    print(f"📄 Navigating to: {url}")
    page.goto(url, timeout=30000)
    
    print("⏳ Waiting 5 seconds for page to load...")
    time.sleep(5)
    
    # Take screenshot
    page.screenshot(path="debug_linkedin_page.png")
    print("📸 Screenshot saved: debug_linkedin_page.png")
    
    # Check for auth wall
    current_url = page.url
    if "/authwall" in current_url or "/login" in current_url:
        print(f"\n⚠️  REDIRECTED TO AUTH/LOGIN: {current_url}")
        print("   LinkedIn requires you to be logged in!")
    else:
        print(f"\n✅ Page loaded: {current_url}")
    
    print(f"📄 Page title: {page.title()}\n")
    
    # Test different selectors for job cards
    print("="*60)
    print("Testing job card selectors:")
    print("="*60)
    
    selectors = [
        ".jobs-search__results-list li",
        ".scaffold-layout__list-container li",
        "li[class*='jobs-search-results__list-item']",
        "ul.jobs-search__results-list > li",
        ".base-card",
        "[data-job-id]"
    ]
    
    for selector in selectors:
        count = page.locator(selector).count()
        print(f"  {selector:50} → {count} elements")
    
    # Get the first job card and analyze it
    print("\n" + "="*60)
    print("Analyzing first job card:")
    print("="*60)
    
    first_card = page.locator(".jobs-search__results-list li").first
    if first_card.count() > 0:
        print("\n🔍 First card HTML (first 500 chars):")
        try:
            html = first_card.inner_html()
            print(html[:500])
            print("...\n")
        except:
            print("  ❌ Could not get HTML\n")
        
        # Try to extract job ID
        print("🆔 Testing job ID extraction:")
        try:
            job_id = first_card.get_attribute("data-job-id")
            print(f"  data-job-id attribute: {job_id}")
        except:
            print("  ❌ No data-job-id attribute")
        
        try:
            link = first_card.locator("a[href*='/jobs/view/']").first
            if link.count() > 0:
                href = link.get_attribute("href")
                print(f"  Link href: {href}")
            else:
                print("  ❌ No link with '/jobs/view/' found")
        except Exception as e:
            print(f"  ❌ Error finding link: {e}")
        
        # Try to extract title
        print("\n📝 Testing title extraction:")
        title_selectors = [
            ".job-card-list__title",
            "a[class*='job-card-container__link'] strong",
            ".base-search-card__title",
            "h3.base-search-card__title"
        ]
        for sel in title_selectors:
            try:
                elem = first_card.locator(sel).first
                if elem.count() > 0:
                    text = elem.inner_text()
                    print(f"  ✅ {sel}: '{text}'")
                else:
                    print(f"  ❌ {sel}: not found")
            except Exception as e:
                print(f"  ❌ {sel}: error - {e}")
    else:
        print("❌ No job cards found!")
    
    print("\n" + "="*60)
    print("⏸️  Keeping browser open for 30 seconds...")
    print("   You can inspect the page in the browser")
    print("="*60)
    time.sleep(30)
    
    browser.close()
    print("\n✅ Debug complete!")

