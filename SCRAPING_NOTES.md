# Important Notes about Web Scraping

## JavaScript-Rendered Sites (SPAs)

Some modern websites use JavaScript frameworks (React, Vue, Angular) that render content dynamically **after** the initial HTML loads. This means:

### The Problem:
- When our Flask backend scrapes with `requests`, it only gets the initial HTML
- JavaScript-added content (including meta tags) is not available
- Sites like joinventureai.com may have limited or no metadata in the initial HTML

### Solutions:

#### 1. Use the Chrome Extension (Recommended)
The Chrome extension runs **after** JavaScript has executed, so it can capture:
- Dynamically added titles
- JavaScript-generated meta descriptions
- Content rendered by frameworks

**Best Practice**: For JavaScript-heavy sites, use the Chrome extension to capture data.

#### 2. For Server-Side Scraping of JavaScript Sites
If you need to scrape JavaScript-rendered sites from the backend, you would need to:
- Install Selenium or Playwright (headless browser)
- Let the page fully render before scraping
- Note: This is slower and more resource-intensive

### Example Install for Selenium (Optional):
```bash
pip install selenium
# Also need Chrome driver
```

### Current Behavior:
- **Backend scraping**: Works best for traditional server-rendered websites
- **Chrome extension**: Works for all websites including JavaScript-rendered ones
- **Fallbacks**: If no meta description exists, we try to extract from:
  - og:description (Open Graph)
  - twitter:description
  - First meaningful paragraph (>50 chars)

## Testing Different Site Types

### Works Great:
- GitHub.com (has proper meta tags)
- StackOverflow.com (server-rendered with metadata)
- WordPress blogs
- Traditional websites

### May Need Chrome Extension:
- React/Vue/Angular single-page apps
- Sites with client-side routing
- JavaScript-heavy modern web apps
