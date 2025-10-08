# LinkedIn Jobs Tracker

A Python-based LinkedIn job scraper that saves job postings to a local SQLite database.  
Runs daily to keep track of **new**, **updated**, and **expired** job listings for your chosen searches.

---

## 🚀 Features

- Scrape job postings from LinkedIn search results (via Playwright).
- Store all jobs in a local SQLite database.
- Daily update logic:
  - Add **new** job postings.
  - Refresh `last_seen` date for existing jobs.
  - Mark jobs as **expired** when they disappear.
- Local, lightweight, and easy to extend.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- [Playwright](https://playwright.dev/python/) for browser automation & scraping.
- **SQLite** for lightweight local database storage.

---

## 📂 Project Structure

```
linkedIn_job_scraper/
├── README.md              # Project overview
├── USAGE.md              # Detailed usage guide
├── requirements.txt      # Python dependencies
├── config.json          # Your search URLs and settings
├── scrape_jobs.py       # Main script to run
├── database.py          # Database operations
├── scraper.py           # LinkedIn scraping logic
├── test_setup.py        # Setup verification script
├── jobs.db              # SQLite database (created on first run)
└── .gitignore
```

### Database Schema

```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    link TEXT,
    date_posted TEXT,
    last_seen TEXT,
    status TEXT DEFAULT 'not_applied',
    applied_on TEXT,
    expired INTEGER DEFAULT 0
);
```


## ⚡ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/AX-Berglund/linkedIn_job_scraper.git
cd linkedIn_job_scraper
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Set up LinkedIn authentication (recommended)

LinkedIn may ask you to sign in. To bypass this:

```bash
python setup_auth.py
```

This will securely store your LinkedIn credentials in a `.env` file.

**⚠️ Note:** Automating LinkedIn login may violate their ToS. Use for personal purposes only.

**Alternative:** Skip this step and deal with manual login when needed.

### 4. Test your setup (optional but recommended)

```bash
python test_setup.py
```

### 5. Configure your search

Edit `config.json` and add your job searches with keywords and location:

```json
{
  "searches": [
    {
      "keywords": "data scientist",
      "location": "Stockholm"
    },
    {
      "keywords": "machine learning engineer",
      "location": "Stockholm"
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

**💡 It's that simple!** Just specify keywords and location - the scraper builds the LinkedIn URLs automatically.

### 6. Run the scraper

```bash
python scrape_jobs.py
```

This will:

* Open LinkedIn in a headless Chromium browser
* Scrape jobs from your saved searches
* Save results in `jobs.db`
* Track new, updated, and expired jobs

📖 **For detailed usage instructions, see [USAGE.md](USAGE.md)**

---

## 📊 Example Workflow

1. **Day 1**: Run `python scrape_jobs.py`
   - Scrapes 150 jobs matching your search
   - All saved to database

2. **Day 2**: Run again
   - Finds 160 jobs total
   - 10 new jobs → added to database
   - 145 existing jobs → `last_seen` updated
   - 5 old jobs gone → marked as expired

3. **View your data**:
   ```bash
   sqlite3 jobs.db "SELECT title, company, location FROM jobs WHERE expired = 0 LIMIT 10;"
   ```

4. **Schedule daily runs** (see [USAGE.md](USAGE.md) for cron/GitHub Actions setup)

---

## 🛣️ Roadmap

* [x] **Phase 1: Scrape LinkedIn jobs & save to SQLite** ✅ COMPLETE
  - [x] Playwright-based scraper
  - [x] SQLite database with job tracking
  - [x] Daily update logic (new/updated/expired)
  - [x] Configuration system
  - [x] Comprehensive documentation
* [ ] **Phase 2: Add LLM-powered filters** (rank jobs by relevance)
* [ ] **Phase 3: Prefill job applications** with stored profile data
* [ ] **Phase 4: Semi-automated or fully automated applications**

---

## ⚠️ Disclaimer

This project is intended **for educational and personal use only**.
Scraping or automating interactions with LinkedIn may violate their Terms of Service.
Use responsibly and at your own risk.
