# Configuration Examples

## Simple Configuration

The easiest way to configure your job searches:

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

---

## Multiple Searches

Search for multiple job types in the same location:

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
    },
    {
      "keywords": "AI engineer",
      "location": "Stockholm"
    }
  ]
}
```

---

## Different Locations

Search the same role in different cities:

```json
{
  "searches": [
    {
      "keywords": "python developer",
      "location": "Stockholm"
    },
    {
      "keywords": "python developer",
      "location": "Gothenburg"
    },
    {
      "keywords": "python developer",
      "location": "Malmö"
    }
  ]
}
```

---

## Broader Searches

Use broader location terms:

```json
{
  "searches": [
    {
      "keywords": "data scientist",
      "location": "Sweden"
    },
    {
      "keywords": "remote data scientist",
      "location": "Europe"
    }
  ]
}
```

---

## Specific Keywords

Be as specific as you want with keywords:

```json
{
  "searches": [
    {
      "keywords": "senior python developer",
      "location": "Stockholm"
    },
    {
      "keywords": "junior data analyst",
      "location": "Stockholm"
    },
    {
      "keywords": "tensorflow deep learning",
      "location": "Sweden"
    }
  ]
}
```

---

## Mixed Format (Advanced)

You can mix the simple format with direct URLs if you need LinkedIn's advanced filters:

```json
{
  "searches": [
    {
      "keywords": "data scientist",
      "location": "Stockholm"
    },
    "https://www.linkedin.com/jobs/search/?f_E=2&keywords=junior+developer&location=Stockholm"
  ]
}
```

**Direct URL benefits:**
- Use LinkedIn's experience level filters (`f_E=2` for entry level)
- Use job type filters (full-time, contract, etc.)
- Use company size filters
- Use date posted filters

---

## Complete Configuration with Settings

Full example with scraper settings:

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

### Settings Explained

- **`headless`** (boolean): Run browser without GUI
  - `true` = invisible (default, faster)
  - `false` = visible (for debugging)

- **`max_scroll_attempts`** (integer): Number of times to scroll for more jobs
  - Default: `5`
  - Each scroll loads ~15-25 jobs
  - Increase for more results (but slower)

- **`scroll_delay_ms`** (integer): Milliseconds to wait between scrolls
  - Default: `2000` (2 seconds)
  - Increase if jobs aren't loading
  - Decrease for faster scraping (risky)

- **`page_load_timeout_ms`** (integer): Max time to wait for page load
  - Default: `30000` (30 seconds)
  - Increase if you get timeout errors

---

## Tips for Better Results

### 1. Use Specific Keywords
❌ Bad: `"job"`
✅ Good: `"senior python developer"`

### 2. Include Variations
```json
{
  "searches": [
    {"keywords": "data scientist", "location": "Stockholm"},
    {"keywords": "data analyst", "location": "Stockholm"},
    {"keywords": "machine learning engineer", "location": "Stockholm"}
  ]
}
```

### 3. Try Different Location Formats
- City name: `"Stockholm"`
- Broader region: `"Sweden"`
- Remote: `"Remote"`
- Multiple countries: `"Scandinavia"`

### 4. Don't Overdo It
- **Recommended**: 3-5 searches
- **Why**: Each search takes 10-20 seconds
- **Duplicates**: Automatically removed

---

## Validation

The scraper validates your configuration:

✅ **Valid:**
```json
{"keywords": "data scientist", "location": "Stockholm"}
```

❌ **Invalid - Missing location:**
```json
{"keywords": "data scientist"}
```

❌ **Invalid - Missing keywords:**
```json
{"location": "Stockholm"}
```

❌ **Invalid - Empty:**
```json
{"keywords": "", "location": ""}
```

---

## Testing Your Configuration

After editing `config.json`, run:

```bash
python scrape_jobs.py
```

You should see:
```
✅ Loaded 2 search(es):
   1. data scientist in Stockholm
   2. machine learning engineer in Stockholm
```

If you see an error, check:
1. Valid JSON syntax (commas, quotes, brackets)
2. Both `keywords` and `location` are present
3. No trailing commas
4. Proper quote marks (`"` not `"` or `'`)

