# Chrome Extension Installation Guide

## 📦 Your Extension is Ready!

The Chrome extension is located in: `c:\Users\dipro\scrapin_data\chrome-extension\`

## 🚀 Step-by-Step Installation

### 1. Start Your Backend Server

First, make sure your Flask backend is running:

```powershell
cd c:\Users\dipro\scrapin_data
C:/Users/dipro/scrapin_data/.venv/Scripts/python.exe app.py
```

The server must be running at `http://localhost:5000` for the extension to work.

### 2. Open Chrome Extensions Page

**Option A:** Type in the address bar:
```
chrome://extensions/
```

**Option B:** Use the menu:
- Click the three dots (⋮) in the top-right corner
- Go to: **More tools** → **Extensions**

### 3. Enable Developer Mode

- Look for the **"Developer mode"** toggle in the top-right corner
- **Turn it ON** (it will turn blue/green)

### 4. Load the Extension

- Click the **"Load unpacked"** button (appears after enabling Developer mode)
- Navigate to: `c:\Users\dipro\scrapin_data\chrome-extension\`
- Click **"Select Folder"**

### 5. Verify Installation

You should see:
- ✅ **Lead Scraper** extension card with logo
- ✅ Extension is enabled (toggle is ON)
- ✅ No errors displayed

### 6. Pin the Extension (Optional)

- Click the **puzzle piece icon** (🧩) in Chrome toolbar
- Find **"Lead Scraper"** in the list
- Click the **pin icon** to keep it visible in toolbar

## 🎯 How to Use

### On Any Website:

1. **Visit any website** (e.g., https://github.com, https://stackoverflow.com)
2. **Click the Lead Scraper icon** in your Chrome toolbar
3. **Review the scraped data**:
   - Title
   - Description
   - Email (if found)
   - Phone (if found)
   - Social media links
   - And more!
4. **Click "Save Lead"** to send it to your database
5. **View saved leads** at http://localhost:5000/dashboard

## ✅ Verification Steps

### Test the Extension:

1. Go to **https://github.com**
2. Click the extension icon
3. You should see:
   ```
   Title: GitHub – Change is constant...
   Description: Join the world's most widely adopted...
   Twitter: github
   LinkedIn: LinkedIn profile found
   Instagram: Instagram profile found
   ```
4. Click "Save Lead"
5. Check http://localhost:5000/dashboard to see the saved lead

## 🔧 Troubleshooting

### Extension Not Loading?
- Make sure you selected the correct folder: `chrome-extension` (not the parent folder)
- Check for errors on the extension card
- Ensure all required files exist:
  - `manifest.json` ✓
  - `popup.html` ✓
  - `popup.js` ✓
  - `icon16.png`, `icon48.png`, `icon128.png` ✓

### "Save Lead" Not Working?
- **Check backend is running**: Visit http://localhost:5000
- **Check console**: Right-click extension popup → Inspect → Console tab
- **Common issue**: CORS errors mean backend isn't running

### No Data Showing?
- Some websites may not have all metadata
- Try different websites (GitHub, Stack Overflow work great)
- JavaScript-heavy sites show more data in the extension than backend scraping

### Icons Not Showing?
- The extension should work fine even if icons don't display
- Icons are simple placeholders - functionality is not affected

## 🎨 Extension Features

### What It Captures:
- ✅ Page title (with multiple fallbacks)
- ✅ Meta description
- ✅ Email addresses (extracted from page)
- ✅ Phone numbers (multiple formats)
- ✅ Company logo URL
- ✅ Favicon
- ✅ Twitter handle
- ✅ LinkedIn profile
- ✅ Facebook page
- ✅ Instagram profile
- ✅ Contact page URL
- ✅ Keywords
- ✅ Language

### Popup Interface Shows:
- **Basic Info**: URL, Title, Description
- **Contact Info**: Email, Phone, Contact page (if found)
- **Social Media**: Twitter, LinkedIn, Facebook, Instagram (if found)
- **Metadata**: Language, Logo status

## 🔄 Updating the Extension

If you make changes to the extension files:

1. Go to `chrome://extensions/`
2. Find "Lead Scraper"
3. Click the **reload icon** (🔄) on the extension card
4. Changes will take effect immediately

## 🌐 Backend URLs

- **Home**: http://localhost:5000/
- **Add Lead**: http://localhost:5000/add-lead
- **Dashboard**: http://localhost:5000/dashboard
- **API**: http://localhost:5000/api/leads

## 📝 Notes

- Extension requires **Chrome Manifest V3** (modern Chrome versions)
- Works on **all websites** (some may have more data than others)
- **Backend must be running** for saving leads
- Extension captures data **after JavaScript loads** (better than backend scraping for SPAs)

## 🎉 Success!

Once installed, you can:
1. Browse any website
2. Click the extension
3. Review and save leads with one click
4. Build your lead database effortlessly!

---

**Need Help?** Check the console in the extension popup (Right-click → Inspect) for error messages.
