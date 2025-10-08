# LinkedIn Job Scraper

Automated LinkedIn job scraper that logs in, searches for jobs, and saves them to a SQLite database.

## 🚀 Features

- ✅ Automated LinkedIn login
- ✅ Cookie consent handling
- ✅ Job search with custom keywords and location
- ✅ Pagination support (scrapes multiple pages)
- ✅ Extracts: Job title, company, location, job ID, URL, posted date
- ✅ Saves to SQLite database with duplicate detection
- ✅ Updates existing jobs (last_seen tracking)
- ✅ Clean data extraction (no duplicates or artifacts)

## 📋 Requirements

- Python 3.7+
- Chrome browser installed
- LinkedIn account

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AX-Berglund/linkedIn_job_scraper
   cd linkedIn_job_scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file** with your LinkedIn credentials:
   ```bash
   cat > .env << 'EOF'
   # LinkedIn Credentials
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password_here
   EOF
   ```
   
   Replace `your_email@example.com` and `your_password_here` with your actual credentials.

## 🎯 Usage

### Run the scraper:
```bash
python linkedin_scraper.py
```

The scraper will:
1. Open Chrome browser
2. Navigate to LinkedIn
3. Click "Reject" on cookie consent
4. Log in with your credentials
5. Search for "data scientist" jobs in "Stockholm"
6. Scrape up to 10 pages (500 jobs)
7. Save all jobs to `jobs.db`

### View scraped jobs:
```bash
python view_jobs.py
```

Options:
- View all jobs
- View jobs by status (not_applied, applied)
- Mark jobs as applied

## 📁 Project Structure

```
linkedIn_job_scraper/
├── linkedin_scraper.py    # Main scraper script
├── database.py            # Database management
├── view_jobs.py          # View and manage scraped jobs
├── jobs.db               # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── .env                  # Your credentials (create this)
└── README.md            # This file
```

## 🔧 Customization

### Change search parameters:

Edit the search parameters in `linkedin_scraper.py` (line ~249):

```python
search_params = "&keywords=data%20scientist&location=Stockholm&refresh=true&start=100"
```

To search for different jobs:
- Change `keywords=data%20scientist` to your desired job (spaces = %20)
- Change `location=Stockholm` to your desired location
- Keep `refresh=true` for fresh results

### Adjust pagination:

Edit `max_pages` in `linkedin_scraper.py` (line ~362):

```python
max_pages = 10  # Scrape up to 10 pages (500 jobs)
```

### Change page increment:

Edit `page_increment` in `linkedin_scraper.py` (line ~361):

```python
page_increment = 50  # LinkedIn shows ~25 jobs per page, but pagination works in 50s
```

## 📊 Database Schema

The `jobs` table stores:
- `job_id` (PRIMARY KEY) - LinkedIn job ID
- `title` - Job title
- `company` - Company name
- `location` - Job location
- `link` - LinkedIn job URL
- `date_posted` - When job was posted (if available)
- `last_seen` - Last time this job was found in search
- `status` - Application status (not_applied, applied)
- `applied_on` - Date you applied (if marked as applied)
- `expired` - Whether job is still active (0=active, 1=expired)

## 🛡️ Security Notes

- **Never commit your `.env` file** - It's already in `.gitignore`
- Keep your LinkedIn credentials secure
- Don't share your `jobs.db` if it contains sensitive information

## ⚠️ Important Notes

- LinkedIn may rate-limit or block automated access
- Use responsibly and respect LinkedIn's Terms of Service
- The browser window stays visible (not headless) to appear more human-like
- Consider adding delays between runs to avoid detection

## 🐛 Troubleshooting

### Browser won't open:
- Make sure Chrome is installed
- Install Playwright browsers: `playwright install chromium`

### Login fails:
- Check your `.env` credentials
- Try logging in manually first to verify account
- LinkedIn may require email/SMS verification

### No jobs found:
- Check your search parameters (keywords, location)
- LinkedIn search results may have changed structure
- Try adjusting the CSS selectors in `scrape_jobs_from_page()` function

### "Target has been closed" error:
- This is a Playwright/Chrome issue on macOS
- The script already handles this with proper launch arguments
- If persists, try updating Playwright: `pip install --upgrade playwright`

## 📝 License

MIT License - Feel free to use and modify as needed.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📧 Support

For issues or questions, please open an issue on GitHub.
