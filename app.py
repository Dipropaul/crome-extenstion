from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            url TEXT NOT NULL,
            title TEXT,
            description TEXT,
            email TEXT,
            phone TEXT,
            logo_url TEXT,
            favicon_url TEXT,
            twitter_handle TEXT,
            linkedin_url TEXT,
            facebook_url TEXT,
            instagram_url TEXT,
            contact_page TEXT,
            industry_keywords TEXT,
            language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('leads.db')
    conn.row_factory = sqlite3.Row
    return conn

# Scraping function
def scrape_website(url):
    try:
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        # Get title - try multiple sources
        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        # If title is empty or too short, try og:title
        if not title or len(title) < 3:
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title and og_title.get('content'):
                title = og_title.get('content').strip()
        
        # If still no title, try twitter:title
        if not title or len(title) < 3:
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                title = twitter_title.get('content').strip()
        
        # If still no title, try h1
        if not title or len(title) < 3:
            h1 = soup.find('h1')
            if h1 and h1.get_text():
                title = h1.get_text().strip()[:100]  # Limit to 100 chars
        
        # Get meta description - try multiple sources
        description = ''
        
        # Try standard meta description (case-insensitive)
        meta_desc = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
        
        # Try og:description
        if not description:
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                description = og_desc.get('content').strip()
        
        # Try twitter:description
        if not description:
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc and twitter_desc.get('content'):
                description = twitter_desc.get('content').strip()
        
        # Fallback: try to get first paragraph
        if not description:
            # Look for paragraphs in main content areas
            for selector in ['main p', 'article p', '.content p', 'p']:
                paragraphs = soup.select(selector)
                for p in paragraphs:
                    text = p.get_text().strip()
                    # Skip very short paragraphs and common boilerplate
                    if len(text) > 50 and 'cookie' not in text.lower():
                        description = text[:300]  # Limit to 300 chars
                        break
                if description:
                    break
        
        # Extract company name from domain
        domain = urlparse(url).netloc
        company = domain.replace('www.', '').split('.')[0].capitalize()
        
        # Extract email addresses
        email = ''
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        # Filter out common non-contact emails
        filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'noreply', 'no-reply'])]
        if filtered_emails:
            email = filtered_emails[0]  # Take first valid email
        
        # Extract phone numbers (basic patterns)
        phone = ''
        phone_patterns = [
            r'\+?1?[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',  # US/Canada
            r'\+\d{1,3}[-.]?\d{3,4}[-.]?\d{3,4}[-.]?\d{3,4}',  # International
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, page_text)
            if phones:
                phone = phones[0]
                break
        
        # Get logo URL
        logo_url = ''
        # Try og:image first
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image and og_image.get('content'):
            logo_url = og_image.get('content')
        # Try common logo selectors
        if not logo_url:
            logo_img = soup.select_one('img[class*="logo"], img[id*="logo"], .logo img, #logo img')
            if logo_img and logo_img.get('src'):
                logo_url = logo_img.get('src')
                # Make absolute URL
                if logo_url.startswith('/'):
                    logo_url = f"{urlparse(url).scheme}://{domain}{logo_url}"
        
        # Get favicon
        favicon_url = ''
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if favicon and favicon.get('href'):
            favicon_url = favicon.get('href')
            if favicon_url.startswith('/'):
                favicon_url = f"{urlparse(url).scheme}://{domain}{favicon_url}"
        else:
            # Default favicon location
            favicon_url = f"{urlparse(url).scheme}://{domain}/favicon.ico"
        
        # Extract social media links
        twitter_handle = ''
        linkedin_url = ''
        facebook_url = ''
        instagram_url = ''
        
        # Check meta tags for Twitter
        twitter_site = soup.find('meta', attrs={'name': 'twitter:site'})
        if twitter_site and twitter_site.get('content'):
            twitter_handle = twitter_site.get('content').replace('@', '')
        
        # Find social media links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '').lower()
            if 'twitter.com' in href and not twitter_handle:
                twitter_handle = href.split('twitter.com/')[-1].split('?')[0].split('/')[0]
            elif 'linkedin.com' in href and not linkedin_url:
                linkedin_url = link.get('href')
            elif 'facebook.com' in href and not facebook_url:
                facebook_url = link.get('href')
            elif 'instagram.com' in href and not instagram_url:
                instagram_url = link.get('href')
        
        # Find contact page
        contact_page = ''
        for link in all_links:
            href = link.get('href', '').lower()
            link_text = link.get_text().lower()
            if any(word in href or word in link_text for word in ['contact', 'about', 'get-in-touch']):
                contact_page = link.get('href')
                if contact_page.startswith('/'):
                    contact_page = f"{urlparse(url).scheme}://{domain}{contact_page}"
                break
        
        # Extract industry keywords
        keywords = ''
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords.get('content').strip()
        
        # Get language
        language = 'en'  # default
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            language = html_tag.get('lang')
        
        # Add note if description is from fallback
        result = {
            'success': True,
            'company': company,
            'url': url,
            'title': title if title else 'No title found',
            'description': description if description else 'No description found',
            'email': email,
            'phone': phone,
            'logo_url': logo_url,
            'favicon_url': favicon_url,
            'twitter_handle': twitter_handle,
            'linkedin_url': linkedin_url,
            'facebook_url': facebook_url,
            'instagram_url': instagram_url,
            'contact_page': contact_page,
            'industry_keywords': keywords,
            'language': language
        }
        
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-lead', methods=['GET', 'POST'])
def add_lead():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        
        if not url:
            return render_template('add_lead.html', error='Please enter a URL')
        
        # Scrape the website
        result = scrape_website(url)
        
        if not result['success']:
            return render_template('add_lead.html', error=f"Error scraping website: {result['error']}")
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO leads (company, url, title, description, email, phone, logo_url, favicon_url, 
               twitter_handle, linkedin_url, facebook_url, instagram_url, contact_page, industry_keywords, language) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (result['company'], result['url'], result['title'], result['description'], result['email'],
             result['phone'], result['logo_url'], result['favicon_url'], result['twitter_handle'],
             result['linkedin_url'], result['facebook_url'], result['instagram_url'], result['contact_page'],
             result['industry_keywords'], result['language'])
        )
        conn.commit()
        conn.close()
        
        return render_template('add_lead.html', success=True, lead=result)
    
    return render_template('add_lead.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    leads = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', leads=leads)

# API endpoint for Chrome extension
@app.route('/api/leads', methods=['POST'])
def add_lead_api():
    data = request.json
    
    url = data.get('url', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    # Extract company name from URL
    domain = urlparse(url).netloc
    company = domain.replace('www.', '').split('.')[0].capitalize()
    
    # Extract additional data from request
    email = data.get('email', '')
    phone = data.get('phone', '')
    logo_url = data.get('logo_url', '')
    favicon_url = data.get('favicon_url', '')
    twitter_handle = data.get('twitter_handle', '')
    linkedin_url = data.get('linkedin_url', '')
    facebook_url = data.get('facebook_url', '')
    instagram_url = data.get('instagram_url', '')
    contact_page = data.get('contact_page', '')
    keywords = data.get('industry_keywords', '')
    language = data.get('language', 'en')
    
    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO leads (company, url, title, description, email, phone, logo_url, favicon_url,
           twitter_handle, linkedin_url, facebook_url, instagram_url, contact_page, industry_keywords, language)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (company, url, title, description, email, phone, logo_url, favicon_url, twitter_handle,
         linkedin_url, facebook_url, instagram_url, contact_page, keywords, language)
    )
    conn.commit()
    lead_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'lead': {
            'id': lead_id,
            'company': company,
            'url': url,
            'title': title,
            'description': description,
            'email': email,
            'phone': phone,
            'logo_url': logo_url,
            'favicon_url': favicon_url,
            'twitter_handle': twitter_handle,
            'linkedin_url': linkedin_url,
            'facebook_url': facebook_url,
            'instagram_url': instagram_url,
            'contact_page': contact_page,
            'industry_keywords': keywords,
            'language': language
        }
    })

@app.route('/api/leads', methods=['GET'])
def get_leads_api():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        leads.append({
            'id': row['id'],
            'company': row['company'],
            'url': row['url'],
            'title': row['title'],
            'description': row['description'],
            'email': row['email'],
            'phone': row['phone'],
            'logo_url': row['logo_url'],
            'favicon_url': row['favicon_url'],
            'twitter_handle': row['twitter_handle'],
            'linkedin_url': row['linkedin_url'],
            'facebook_url': row['facebook_url'],
            'instagram_url': row['instagram_url'],
            'contact_page': row['contact_page'],
            'industry_keywords': row['industry_keywords'],
            'language': row['language'],
            'created_at': row['created_at']
        })
    
    return jsonify({'success': True, 'leads': leads})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
