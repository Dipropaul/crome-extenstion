"""
Test script to verify improved scraping functionality
Run this to test various websites and see the scraping results
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_website(url):
    """Enhanced scraping function with multiple fallbacks"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title - try multiple sources
        title = ''
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        if not title or len(title) < 3:
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            if og_title and og_title.get('content'):
                title = og_title.get('content').strip()
        
        if not title or len(title) < 3:
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                title = twitter_title.get('content').strip()
        
        if not title or len(title) < 3:
            h1 = soup.find('h1')
            if h1 and h1.get_text():
                title = h1.get_text().strip()[:100]
        
        # Get meta description - try multiple sources
        description = ''
        
        meta_desc = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content').strip()
        
        if not description:
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc and og_desc.get('content'):
                description = og_desc.get('content').strip()
        
        if not description:
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc and twitter_desc.get('content'):
                description = twitter_desc.get('content').strip()
        
        if not description:
            for selector in ['main p', 'article p', '.content p', 'p']:
                paragraphs = soup.select(selector)
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50 and 'cookie' not in text.lower():
                        description = text[:300]
                        break
                if description:
                    break
        
        domain = urlparse(url).netloc
        company = domain.replace('www.', '').split('.')[0].capitalize()
        
        return {
            'success': True,
            'company': company,
            'url': url,
            'title': title if title else 'No title found',
            'description': description if description else 'No description found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == '__main__':
    print("=" * 70)
    print("WEBSITE SCRAPING TEST")
    print("=" * 70)
    
    # Test different types of websites
    test_sites = [
        ('https://github.com', 'GitHub - Should work great'),
        ('https://stackoverflow.com', 'Stack Overflow - Should work great'),
        ('https://python.org', 'Python.org - Should work great'),
        ('https://example.com', 'Example.com - Simple site'),
        ('https://joinventureai.com/', 'JVAI - JavaScript SPA (limited data expected)')
    ]
    
    for url, description in test_sites:
        print(f"\n{description}")
        print(f"URL: {url}")
        print("-" * 70)
        
        result = scrape_website(url)
        
        if result['success']:
            print(f"✓ Company: {result['company']}")
            print(f"✓ Title: {result['title']}")
            desc_preview = result['description'][:100] + '...' if len(result['description']) > 100 else result['description']
            print(f"✓ Description: {desc_preview}")
        else:
            print(f"✗ Error: {result['error']}")
        
        print()
    
    print("=" * 70)
    print("NOTES:")
    print("- Sites with 'No description found' may be JavaScript-rendered")
    print("- Use the Chrome extension for best results on JavaScript sites")
    print("- The extension captures data AFTER JavaScript executes")
    print("=" * 70)
