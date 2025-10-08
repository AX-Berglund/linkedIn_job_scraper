# Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)
```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Test Everything Works (1 minute)
```bash
python test_setup.py
```
If all tests pass ✅, you're good to go!

### Step 3: Add Your Job Searches (1 minute)

Simply edit `config.json` with your keywords and location:

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
    }
  ]
}
```

**That's it!** The scraper automatically builds LinkedIn URLs for you.

### Step 4: Run the Scraper (1 minute)
```bash
python scrape_jobs.py
```

🎉 **Done!** Your jobs are now saved in `jobs.db`

---

## 📊 View Your Jobs

```bash
# See statistics
python view_jobs.py stats

# List first 10 jobs
python view_jobs.py list --limit 10 --compact

# Search for specific jobs
python view_jobs.py search "python"

# See recent jobs (last 7 days)
python view_jobs.py recent --days 7
```

---

## 🔄 Daily Updates

Run `python scrape_jobs.py` daily to:
- ✅ Add new job postings
- 🔄 Update existing jobs (refresh last_seen date)
- ❌ Mark missing jobs as expired

**Tip:** Set up a cron job or use GitHub Actions (see [USAGE.md](USAGE.md))

---

## 🆘 Troubleshooting

### ❌ "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### ❌ "No jobs found"
- Check your search URL is correct
- Try setting `"headless": false` in config.json to see what's happening
- LinkedIn may have changed their layout (selectors may need updating)

### ❌ "Config file not found"
Make sure `config.json` exists in the same directory as `scrape_jobs.py`

---

## 📚 More Information

- **Detailed Usage:** [USAGE.md](USAGE.md)
- **Project Overview:** [README.md](README.md)

## ⚠️ Important

This tool is for **personal use only**. Scraping LinkedIn may violate their Terms of Service. Use responsibly!

