# LinkedIn Authentication Setup

## ⚠️ Important Security Notice

**Storing your LinkedIn credentials and automating login may violate LinkedIn's Terms of Service.**

This feature is provided for:
- Personal use only
- Educational purposes
- Local job searching convenience

**Use at your own risk. LinkedIn may:**
- Lock your account
- Require additional verification
- Ban automated access

---

## 🔐 Setup Authentication

### Step 1: Create `.env` File

Copy the example file and add your credentials:

```bash
cp .env.example .env
```

### Step 2: Edit `.env` File

Open `.env` in a text editor and add your LinkedIn credentials:

```bash
# LinkedIn Credentials
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_actual_password

# Enable auto-login
LINKEDIN_AUTO_LOGIN=true
```

**⚠️ NEVER commit your `.env` file to git!** It's already in `.gitignore`.

### Step 3: Run the Scraper

```bash
python scrape_jobs.py
```

You should see:
```
🔐 Auto-login enabled
🌐 Starting web scraper...
  🔐 Attempting LinkedIn login...
  📧 Email entered
  🔑 Password entered
  🚀 Sign in clicked, waiting for redirect...
  ✅ Successfully logged in to LinkedIn!
```

---

## 🔄 How It Works

### First Run
1. Scraper logs in to LinkedIn with your credentials
2. Session is saved to `linkedin_session.json`
3. Scraping proceeds normally

### Subsequent Runs
1. Scraper loads saved session from `linkedin_session.json`
2. No login needed (session reused)
3. Much faster startup

### Session Expiry
- LinkedIn sessions expire after some time
- When expired, scraper will login again automatically
- New session is saved for next run

---

## 🛡️ Security Best Practices

### 1. Use App-Specific Password (if LinkedIn supports it)
Instead of your main password, use an app-specific password if available.

### 2. Enable Two-Factor Authentication
- Enable 2FA on your LinkedIn account
- On first login, you may need to verify manually
- Set `headless: false` in config for first-time verification

### 3. Keep .env Secure
```bash
# Check that .env is in .gitignore
cat .gitignore | grep .env

# Check file permissions (should be 600 or 644)
ls -la .env
```

### 4. Use a Separate Account (Recommended)
- Create a separate LinkedIn account for scraping
- Don't use your main professional account
- Reduces risk if account gets flagged

---

## 🔧 Troubleshooting

### Login Verification Required

If LinkedIn requires verification:

1. **Temporarily disable headless mode:**
   ```json
   {
     "scrape_settings": {
       "headless": false
     }
   }
   ```

2. **Run the scraper:**
   ```bash
   python scrape_jobs.py
   ```

3. **Complete verification in the browser window that opens**

4. **Session will be saved for future runs**

5. **Re-enable headless mode** after verification

### "Security Challenge Detected"

If you see:
```
⚠️  LinkedIn security challenge detected!
```

**Solution:**
1. Set `"headless": false` in `config.json`
2. Run scraper
3. Complete the challenge in the browser
4. Session will be saved
5. Future runs will use saved session

### Login Fails

If login fails:

1. **Verify credentials:**
   ```bash
   # Check .env file
   cat .env
   ```

2. **Test manually:** Try logging in at https://www.linkedin.com

3. **Check for CAPTCHA:** LinkedIn may require CAPTCHA on first login
   - Set `headless: false`
   - Complete CAPTCHA manually

4. **Check saved session:**
   ```bash
   # Delete old session and try fresh login
   rm linkedin_session.json
   python scrape_jobs.py
   ```

---

## 🚫 Disable Authentication

To disable automatic login:

**Option 1:** Set in `.env`:
```bash
LINKEDIN_AUTO_LOGIN=false
```

**Option 2:** Delete `.env` file:
```bash
rm .env
```

**Option 3:** Remove credentials from `.env`:
```bash
# Comment out or delete these lines
# LINKEDIN_EMAIL=...
# LINKEDIN_PASSWORD=...
```

---

## 📋 Files Used

| File | Purpose | Git Status |
|------|---------|------------|
| `.env` | Your credentials (SECRET!) | ❌ Ignored (never commit) |
| `.env.example` | Template file | ✅ Committed (safe) |
| `linkedin_session.json` | Saved login session | ❌ Ignored (auto-generated) |

---

## ⚙️ Advanced: Manual Session Management

### Export Session from Real Browser

If you want to use your regular browser's session:

1. **Login to LinkedIn in Chrome/Firefox**

2. **Export cookies using extension:**
   - Install "EditThisCookie" or similar
   - Export LinkedIn cookies as JSON

3. **Convert to Playwright format** (manual process)

4. **Save as `linkedin_session.json`**

### Delete Saved Session

```bash
rm linkedin_session.json
```

Next run will login fresh.

### Check Session Status

```bash
# Check if session file exists
ls -lh linkedin_session.json

# View session (careful - contains auth data!)
cat linkedin_session.json
```

---

## 🎯 Summary

✅ **Pros:**
- No more "sign in to view jobs" popups
- Faster scraping (session reused)
- Automatic handling of auth walls
- Session persists between runs

⚠️ **Cons:**
- Violates LinkedIn ToS
- Risk of account suspension
- Need to store credentials
- May require periodic re-authentication

---

## 📚 See Also

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [USAGE.md](USAGE.md) - General usage guide
- [CONFIG_EXAMPLES.md](CONFIG_EXAMPLES.md) - Configuration examples

