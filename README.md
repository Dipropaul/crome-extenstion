# Lead Scraper

A simple web scraping system with a Flask backend, web dashboard, and Chrome extension for capturing leads from websites.

## Features

- **Web Dashboard**: Add leads by URL and view all saved leads
- **Automatic Scraping**: Extracts title and meta description from websites
- **SQLite Database**: Stores all leads locally
- **Chrome Extension**: Quick capture leads from any webpage
- **REST API**: Backend API for programmatic access

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Flask Backend

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Access the Web Dashboard

Open your browser and navigate to:
- **Home**: http://localhost:5000/
- **Add Lead**: http://localhost:5000/add-lead
- **Dashboard**: http://localhost:5000/dashboard

### 4. Install Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder from this project
5. The Lead Scraper extension will appear in your toolbar

## Usage

### Web Dashboard

1. **Add a Lead**:
   - Go to "Add Lead" page
   - Enter a website URL (e.g., `https://example.com`)
   - Click "Scrape & Save"
   - The system will automatically extract the title and meta description

2. **View Leads**:
   - Go to "Dashboard" page
   - See all saved leads with company name, URL, title, and description

### Chrome Extension

1. Click the Lead Scraper icon in your Chrome toolbar while on any website
2. The extension will automatically scrape the current page's title and description
3. Review the scraped data
4. Click "Save Lead" to send it to your backend
5. The lead will be saved to your database

## API Endpoints

### POST /api/leads
Save a new lead

**Request Body**:
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "description": "This domain is for use in examples"
}
```

**Response**:
```json
{
  "success": true,
  "lead": {
    "id": 1,
    "company": "Example",
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "This domain is for use in examples"
  }
}
```

### GET /api/leads
Get all leads

**Response**:
```json
{
  "success": true,
  "leads": [...]
}
```

## Project Structure

```
scrapin_data/
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── leads.db                    # SQLite database (created automatically)
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Home page
│   ├── add_lead.html          # Add lead form
│   └── dashboard.html         # Leads dashboard
└── chrome-extension/
    ├── manifest.json          # Extension manifest
    ├── popup.html            # Extension popup UI
    ├── popup.js              # Extension logic
    └── icon*.png             # Extension icons
```

## Technologies Used

- **Backend**: Python, Flask, SQLite
- **Scraping**: BeautifulSoup4, Requests
- **Frontend**: HTML, CSS, JavaScript
- **Extension**: Chrome Extension Manifest V3

## Notes

- Make sure the Flask backend is running before using the Chrome extension
- The extension requires the backend to be accessible at `http://localhost:5000`
- CORS is enabled to allow the extension to communicate with the backend
- The database is created automatically on first run

## Troubleshooting

**Chrome Extension Not Saving**:
- Ensure the Flask backend is running
- Check that the API_URL in `popup.js` matches your backend address
- Look at the browser console for error messages

**Scraping Fails**:
- Some websites may block scraping
- Ensure the URL includes the protocol (http:// or https://)
- Check your internet connection
