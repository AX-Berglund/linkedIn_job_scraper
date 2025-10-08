# Changelog

## [1.2.0] - 2025-10-08

### 🔐 LinkedIn Authentication

#### Automatic Login Feature
**New capability to bypass LinkedIn auth walls!**

- Automatic LinkedIn login with stored credentials
- Session persistence between runs
- Secure credential storage in `.env` file
- Interactive setup script (`setup_auth.py`)
- Comprehensive authentication guide

**Files Added:**
- `.env.example` - Credentials template
- `setup_auth.py` - Interactive setup tool
- `AUTHENTICATION.md` - Complete auth guide
- `AUTH_SETUP_SUMMARY.md` - Implementation summary

**Security Features:**
- Git-ignored credential files
- Secure file permissions (600)
- Password masking during input
- Session file auto-management

**⚠️ Important:** Use at your own risk - may violate LinkedIn ToS

---

## [1.1.0] - 2025-10-08

### ✨ Major Improvements

#### Simplified Configuration Format
**Before:**
```json
{
  "searches": [
    "https://www.linkedin.com/jobs/search/?keywords=data%20scientist&location=Stockholm"
  ]
}
```

**Now:**
```json
{
  "searches": [
    {
      "keywords": "data scientist",
      "location": "Stockholm"
    }
  ]
}
```

**Benefits:**
- ✅ More user-friendly - no need to manually build URLs
- ✅ Cleaner and easier to read
- ✅ Automatic URL encoding
- ✅ Still supports direct URLs for advanced users
- ✅ Better output display showing "X in Y" format

#### Technical Changes
- Added `build_linkedin_url()` function to automatically create LinkedIn search URLs
- Added `parse_search_config()` to support both new format and legacy URLs
- Updated output to show searches in human-readable format
- Backward compatible with old URL-based format

---

## [1.0.0] - 2025-10-08

### 🎉 Initial Release

#### Core Features
- ✅ Web scraping using Playwright (WebKit/Safari engine)
- ✅ SQLite database with job tracking
- ✅ Automatic detection of new, updated, and expired jobs
- ✅ Duplicate removal across multiple searches
- ✅ Job extraction: title, company, location, link, date posted
- ✅ Status tracking (applied/not applied)

#### Tools & Scripts
- `scrape_jobs.py` - Main scraper script
- `database.py` - Database operations
- `scraper.py` - LinkedIn scraping logic
- `view_jobs.py` - Interactive CLI for exploring jobs
- `test_setup.py` - Setup verification
- `test_browser.py` - Browser diagnostics

#### Documentation
- `README.md` - Project overview
- `QUICKSTART.md` - 5-minute setup guide
- `USAGE.md` - Comprehensive usage guide
- `TROUBLESHOOTING.md` - Common issues and fixes

#### Known Issues Fixed
- ✅ DNS resolution issues (fixed with Google DNS)
- ✅ Browser compatibility (switched to WebKit)
- ✅ LinkedIn selector updates (updated to match current HTML)
- ✅ Job ID extraction from `data-entity-urn`

---

## Future Roadmap

### Phase 2: LLM-Powered Job Ranking (Planned)
- Integrate LLM to analyze job descriptions
- Rank jobs by relevance to user profile
- Extract key requirements and skills
- Match user skills to job requirements

### Phase 3: Application Prefill (Planned)
- Store user profile data
- Prefill application forms automatically
- Track application status

### Phase 4: Automated Applications (Planned)
- Semi-automated or fully automated job applications
- Approval workflow for user control

