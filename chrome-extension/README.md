# Lead Scraper Chrome Extension

## Installation

1. Open Chrome and go to: `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select this folder: `chrome-extension`

## Requirements

- Flask backend must be running at `http://localhost:5000`
- Chrome browser (Manifest V3 compatible)

## Usage

1. Visit any website
2. Click the extension icon
3. Review scraped data
4. Click "Save Lead" to store in database

## Files

- `manifest.json` - Extension configuration
- `popup.html` - Extension popup UI
- `popup.js` - Scraping and API logic
- `icon*.png` - Extension icons

## Features

Automatically captures:
- Title and description
- Email and phone numbers
- Social media profiles
- Logo and favicon
- Contact page
- And more!

## Support

See `QUICK_START.txt` or `CHROME_EXTENSION_INSTALL.md` in parent folder.
