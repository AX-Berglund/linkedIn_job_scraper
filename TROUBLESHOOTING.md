# Troubleshooting Guide

## Common Issues

### ❌ "Target page, context or browser has been closed"

This error usually means one of these issues:

#### 1. LinkedIn Authentication Wall

**The most common issue**: LinkedIn now requires login to view job searches in many regions.

**Solution**: Run the scraper in non-headless mode first to see what's happening:

```json
{
  "scrape_settings": {
    "headless": false,
    ...
  }
}
```

Then run:
```bash
python scrape_jobs.py
```

**What you'll see:**
- If LinkedIn shows a login page, the scraper cannot work without authentication
- If you see jobs but they're not being scraped, the selectors may need updating

#### 2. Using LinkedIn with Authentication

LinkedIn's Terms of Service generally prohibit automated scraping. However, for personal use, you have options:

**Option A: Manual Cookie/Session (Advanced)**
You would need to:
1. Log in to LinkedIn manually in a browser
2. Export your cookies
3. Inject them into the Playwright session

This requires modifying the scraper code.

**Option B: LinkedIn API (Recommended)**
- Use LinkedIn's official API if you qualify
- More reliable and doesn't violate ToS
- Requires LinkedIn developer account

**Option C: Use Public Job Boards**
- Many companies post jobs on multiple platforms
- Consider scraping Indeed, Glassdoor (check their ToS too)

### ❌ No Jobs Found (Returns 0 jobs)

**Possible causes:**

1. **LinkedIn changed their HTML structure**
   - LinkedIn frequently updates their website
   - The CSS selectors in `scraper.py` may need updating
   
   **Fix**: Run with `"headless": false` and take a screenshot to see the page structure

2. **Geo-blocking or Rate Limiting**
   - LinkedIn may be blocking automated requests
   - Try increasing delays in config.json:
   ```json
   {
     "scrape_settings": {
       "scroll_delay_ms": 5000,
       "page_load_timeout_ms": 60000
     }
   }
   ```

3. **Invalid Search URL**
   - Make sure your URL is valid and works in a browser first
   - URL should start with `https://www.linkedin.com/jobs/search/`

### ❌ Timeout Errors

**Fix options:**

1. **Increase timeouts** in `config.json`:
```json
{
  "scrape_settings": {
    "page_load_timeout_ms": 60000
  }
}
```

2. **Check your internet connection**

3. **LinkedIn might be slow or down** - try again later

### ❌ Browser Installation Fails

```bash
# Install only chromium
playwright install chromium

# Or with system dependencies (Linux)
playwright install --with-deps chromium
```

### 🔍 Debug Mode

To see what's happening:

1. **Enable visible browser**:
   ```json
   {
     "scrape_settings": {
       "headless": false
     }
   }
   ```

2. **Check debug screenshots**:
   - When errors occur, the scraper saves screenshots
   - Look for `debug_screenshot_*.png` files
   - These show what the browser saw when it failed

3. **Run with Python in verbose mode**:
   ```bash
   python -v scrape_jobs.py
   ```

## LinkedIn Authentication Required?

If LinkedIn requires you to log in, you have a few options:

### Option 1: Modify Scraper to Use Cookies (Advanced)

Add authentication to the scraper by saving your session:

1. Log in to LinkedIn in Chrome
2. Export cookies using a browser extension (like "EditThisCookie")
3. Modify `scraper.py` to load those cookies

**Example modification** (add to `__enter__` method in `scraper.py`):

```python
def __enter__(self):
    self.playwright = sync_playwright().start()
    self.browser = self.playwright.chromium.launch(headless=self.headless)
    
    # Create context with persistent storage
    context = self.browser.new_context(
        storage_state="linkedin_auth.json",  # Save/load cookies here
        user_agent='...',
        viewport={'width': 1920, 'height': 1080}
    )
    
    self.page = context.new_page()
    # ... rest of code
```

### Option 2: Use Persistent Browser Context

The scraper could open a browser, let you log in manually once, then save the session for future runs.

### Option 3: Alternative Approach

Instead of scraping LinkedIn directly, consider:

1. **LinkedIn API** (official)
   - Apply for API access
   - Limited but legal and stable

2. **RSS Feeds** (if available)
   - Some job boards offer RSS feeds
   - Check if LinkedIn still provides any

3. **Job Aggregators**
   - Indeed, Glassdoor, etc.
   - May have more permissive scraping policies (check their ToS)

4. **Manual Export + Tracking**
   - Browse LinkedIn manually
   - Copy job IDs/URLs to a CSV
   - Import into the database
   - Track applications manually

## Testing Selectors

If jobs aren't being extracted, test the CSS selectors:

1. Set `"headless": false` in config
2. When the browser opens, open Developer Tools (F12)
3. Try these in the Console:

```javascript
// Check if job cards exist
document.querySelectorAll('.jobs-search__results-list li').length

// Check alternative selectors
document.querySelectorAll('.scaffold-layout__list-container li').length
document.querySelectorAll('li[class*="jobs-search-results__list-item"]').length

// Find what selectors DO exist
document.querySelectorAll('[class*="job"]').length
```

If you find different selectors, update `scraper.py` line ~140:

```python
selectors = [
    ".your-new-selector-here",
    ".jobs-search__results-list li",
    # ... existing selectors
]
```

## Still Having Issues?

1. **Check debug screenshots** - they'll show what the page actually looked like
2. **Verify URL works** in your browser first
3. **Try a simpler search** (fewer filters, common keywords)
4. **Consider alternatives** to web scraping (see Option 3 above)

## Important Reminder

⚠️ **Web scraping LinkedIn may violate their Terms of Service.** This tool is for educational purposes. Consider:
- Using official APIs when available
- Respecting rate limits
- Not running too frequently
- Personal use only

