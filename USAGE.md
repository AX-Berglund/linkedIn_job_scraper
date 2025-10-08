# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Your Searches

Edit `config.json` to add your job searches - just specify keywords and location:

```json
{
  "searches": [
    {
      "keywords": "python developer",
      "location": "Stockholm"
    },
    {
      "keywords": "data scientist",
      "location": "Stockholm"
    },
    {
      "keywords": "AI engineer",
      "location": "Sweden"
    }
  ],
  "scrape_settings": {
    "headless": true,
    "max_scroll_attempts": 5,
    "scroll_delay_ms": 2000,
    "page_load_timeout_ms": 30000
  }
}
```

**It's that simple!** The scraper automatically converts your keywords and location into proper LinkedIn search URLs.

**Advanced:** You can still use direct URLs if needed:
```json
{
  "searches": [
    {"keywords": "data scientist", "location": "Stockholm"},
    "https://www.linkedin.com/jobs/search/?f_E=2&keywords=junior+developer"
  ]
}
```

### 3. Run the Scraper

```bash
python scrape_jobs.py
```

## Configuration Options

### Scrape Settings

- **`headless`** (boolean): Run browser without GUI (default: `true`)
  - Set to `false` to see the browser in action (useful for debugging)

- **`max_scroll_attempts`** (integer): Number of times to scroll down to load more jobs (default: `5`)
  - Increase if you want to load more results
  - Each scroll loads approximately 20-25 jobs

- **`scroll_delay_ms`** (integer): Milliseconds to wait between scrolls (default: `2000`)
  - Increase if jobs aren't loading properly
  - Decrease to speed up scraping (but may miss jobs)

- **`page_load_timeout_ms`** (integer): Maximum time to wait for page load (default: `30000`)

## Database Operations

### Database Schema

The SQLite database (`jobs.db`) has the following structure:

```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,        -- Unique LinkedIn job ID
    title TEXT,                     -- Job title
    company TEXT,                   -- Company name
    location TEXT,                  -- Job location
    link TEXT,                      -- Direct link to job posting
    date_posted TEXT,               -- When job was posted (if available)
    last_seen TEXT,                 -- Last date this job was found
    status TEXT DEFAULT 'not_applied', -- Application status
    applied_on TEXT,                -- Date you applied (if applicable)
    expired INTEGER DEFAULT 0       -- 1 if job no longer appears in searches
);
```

### Querying the Database

You can use any SQLite tool to query your database:

**Command line:**
```bash
sqlite3 jobs.db "SELECT title, company, location FROM jobs WHERE expired = 0 LIMIT 10;"
```

**Python:**
```python
import sqlite3

conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

# Get all active jobs
cursor.execute("SELECT * FROM jobs WHERE expired = 0")
for row in cursor.fetchall():
    print(row)

conn.close()
```

**DB Browser for SQLite:**
Download from https://sqlitebrowser.org/ for a GUI interface.

### Updating Job Status

When you apply to a job, update its status:

```sql
UPDATE jobs 
SET status = 'applied', applied_on = '2025-10-08'
WHERE job_id = '1234567890';
```

## How the Update Logic Works

Each time you run `scrape_jobs.py`:

1. **New Jobs**: Jobs that weren't in the database are inserted
2. **Existing Jobs**: `last_seen` date is updated to today
3. **Expired Jobs**: Jobs that were active but no longer appear in search results are marked with `expired = 1`

This means you'll always know:
- Which jobs are new since last run
- Which jobs have disappeared (company filled the position or removed listing)
- Which jobs you've seen before

## Scheduling Regular Runs

### Using Cron (Linux/Mac)

Edit your crontab:
```bash
crontab -e
```

Add a line to run daily at 9 AM:
```cron
0 9 * * * cd /path/to/linkedIn_job_scraper && /usr/bin/python3 scrape_jobs.py >> scraper.log 2>&1
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Daily"
4. Action: Start a program
   - Program: `python`
   - Arguments: `scrape_jobs.py`
   - Start in: `C:\path\to\linkedIn_job_scraper`

### Using GitHub Actions

Create `.github/workflows/scrape.yml`:

```yaml
name: Scrape LinkedIn Jobs
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: |
          pip install -r requirements.txt
          playwright install chromium
          python scrape_jobs.py
      - name: Commit database
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add jobs.db
          git commit -m "Update jobs database" || exit 0
          git push
```

## Tips & Best Practices

### 1. Start with Headless = False
When first setting up, set `"headless": false` in config to see what's being scraped.

### 2. Don't Overload LinkedIn
- Keep `scroll_delay_ms` at least 2000ms
- Don't run the scraper more than once per day
- Respect LinkedIn's rate limits

### 3. Keep Your Searches Specific
- Use specific keywords
- Add location filters
- Use LinkedIn's date filter (e.g., "Past Week")

### 4. Monitor the Database
Regularly check job statistics to see how your job search is going:
```bash
python -c "from database import JobDatabase; db = JobDatabase(); print(db.get_job_stats())"
```

### 5. Export Your Data
Export active jobs to review:
```python
from database import JobDatabase
import json

db = JobDatabase()
jobs = db.export_jobs_to_dict(active_only=True)

with open('active_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)
```

## Troubleshooting

### No Jobs Found
- Check if your search URL is correct
- Try setting `"headless": false` to see what the browser sees
- LinkedIn may have changed their HTML structure (selectors may need updating)
- Increase `scroll_delay_ms` to give pages more time to load

### Database Locked Error
- Make sure you're not running multiple instances
- Close any database browsers or tools accessing `jobs.db`

### Browser Installation Fails
```bash
# Try installing chromium only
playwright install chromium

# Or with dependencies
playwright install --with-deps chromium
```

### TimeoutError
- Increase `page_load_timeout_ms` in config
- Check your internet connection
- LinkedIn might be temporarily blocking requests

## Important Disclaimer

⚠️ **This tool is for personal, educational use only.**

Scraping LinkedIn may violate their Terms of Service. Use responsibly:
- Don't run too frequently (once per day is reasonable)
- Don't scrape massive amounts of data
- Use for personal job search only
- Consider using LinkedIn's official API if available

**Use at your own risk!**

