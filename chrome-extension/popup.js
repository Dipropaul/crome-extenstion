// API endpoint - change this if your backend runs on a different port
const API_URL = 'http://localhost:5000/api/leads';

let scrapedData = {
    url: '',
    title: '',
    description: '',
    email: '',
    phone: '',
    logo_url: '',
    favicon_url: '',
    twitter_handle: '',
    linkedin_url: '',
    facebook_url: '',
    instagram_url: '',
    contact_page: '',
    industry_keywords: '',
    language: 'en'
};

// Function to scrape the current page
async function scrapeCurrentPage() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Execute script in the page context to get all lead details
    const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            // Get title - try multiple sources
            let title = document.title || '';
            
            // If title is empty or too short, try og:title
            if (!title || title.length < 3) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle) title = ogTitle.getAttribute('content') || title;
            }
            
            // If still no title, try twitter:title
            if (!title || title.length < 3) {
                const twitterTitle = document.querySelector('meta[name="twitter:title"]');
                if (twitterTitle) title = twitterTitle.getAttribute('content') || title;
            }
            
            // If still no title, try h1
            if (!title || title.length < 3) {
                const h1 = document.querySelector('h1');
                if (h1) title = h1.textContent.trim().substring(0, 100);
            }
            
            // Get meta description - try multiple sources
            let description = '';
            
            // Try standard meta description (case-insensitive)
            let metaDesc = document.querySelector('meta[name="description"]');
            if (!metaDesc) {
                metaDesc = document.querySelector('meta[name="Description"]');
            }
            if (metaDesc) {
                description = metaDesc.getAttribute('content') || '';
            }
            
            // Try og:description
            if (!description) {
                const ogDesc = document.querySelector('meta[property="og:description"]');
                if (ogDesc) description = ogDesc.getAttribute('content') || '';
            }
            
            // Try twitter:description
            if (!description) {
                const twitterDesc = document.querySelector('meta[name="twitter:description"]');
                if (twitterDesc) description = twitterDesc.getAttribute('content') || '';
            }
            
            // Fallback: try to get first meaningful paragraph
            if (!description) {
                const selectors = ['main p', 'article p', '.content p', 'p'];
                for (const selector of selectors) {
                    const paragraphs = document.querySelectorAll(selector);
                    for (const p of paragraphs) {
                        const text = p.textContent.trim();
                        // Skip very short paragraphs and common boilerplate
                        if (text.length > 50 && !text.toLowerCase().includes('cookie')) {
                            description = text.substring(0, 300);
                            break;
                        }
                    }
                    if (description) break;
                }
            }
            
            // Extract email addresses from page text
            let email = '';
            const pageText = document.body.innerText;
            const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
            const emails = pageText.match(emailRegex) || [];
            const filteredEmails = emails.filter(e => 
                !e.toLowerCase().includes('example') && 
                !e.toLowerCase().includes('test') &&
                !e.toLowerCase().includes('noreply')
            );
            if (filteredEmails.length > 0) email = filteredEmails[0];
            
            // Extract phone numbers
            let phone = '';
            const phoneRegex = /(\+?1?[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}|\+\d{1,3}[-.]?\d{3,4}[-.]?\d{3,4}[-.]?\d{3,4})/g;
            const phones = pageText.match(phoneRegex) || [];
            if (phones.length > 0) phone = phones[0];
            
            // Get logo URL
            let logoUrl = '';
            const ogImage = document.querySelector('meta[property="og:image"]');
            if (ogImage) {
                logoUrl = ogImage.getAttribute('content') || '';
            }
            if (!logoUrl) {
                const logoImg = document.querySelector('img[class*="logo"], img[id*="logo"], .logo img, #logo img');
                if (logoImg) logoUrl = logoImg.src || '';
            }
            
            // Get favicon
            let faviconUrl = '';
            const favicon = document.querySelector('link[rel*="icon"]');
            if (favicon) {
                faviconUrl = favicon.href || '';
            } else {
                faviconUrl = window.location.origin + '/favicon.ico';
            }
            
            // Extract social media handles/links
            let twitterHandle = '';
            let linkedinUrl = '';
            let facebookUrl = '';
            let instagramUrl = '';
            
            // Check meta tags for Twitter
            const twitterSite = document.querySelector('meta[name="twitter:site"]');
            if (twitterSite) {
                twitterHandle = (twitterSite.getAttribute('content') || '').replace('@', '');
            }
            
            // Find social media links
            const allLinks = document.querySelectorAll('a[href]');
            allLinks.forEach(link => {
                const href = link.href.toLowerCase();
                if (href.includes('twitter.com') && !twitterHandle) {
                    twitterHandle = href.split('twitter.com/')[1]?.split('?')[0]?.split('/')[0] || '';
                } else if (href.includes('linkedin.com') && !linkedinUrl) {
                    linkedinUrl = link.href;
                } else if (href.includes('facebook.com') && !facebookUrl) {
                    facebookUrl = link.href;
                } else if (href.includes('instagram.com') && !instagramUrl) {
                    instagramUrl = link.href;
                }
            });
            
            // Find contact page
            let contactPage = '';
            allLinks.forEach(link => {
                const href = link.href.toLowerCase();
                const text = link.textContent.toLowerCase();
                if ((href.includes('contact') || text.includes('contact') || 
                     href.includes('about') || text.includes('about')) && !contactPage) {
                    contactPage = link.href;
                }
            });
            
            // Get keywords
            let keywords = '';
            const metaKeywords = document.querySelector('meta[name="keywords"]');
            if (metaKeywords) {
                keywords = metaKeywords.getAttribute('content') || '';
            }
            
            // Get language
            let language = 'en';
            const htmlTag = document.querySelector('html');
            if (htmlTag && htmlTag.lang) {
                language = htmlTag.lang;
            }
            
            return {
                title: title.trim() || 'No title found',
                description: description.trim() || 'No description found',
                email: email,
                phone: phone,
                logo_url: logoUrl,
                favicon_url: faviconUrl,
                twitter_handle: twitterHandle,
                linkedin_url: linkedinUrl,
                facebook_url: facebookUrl,
                instagram_url: instagramUrl,
                contact_page: contactPage,
                industry_keywords: keywords,
                language: language
            };
        }
    });
    
    const data = results[0].result;
    scrapedData = {
        url: tab.url,
        title: data.title,
        description: data.description,
        email: data.email,
        phone: data.phone,
        logo_url: data.logo_url,
        favicon_url: data.favicon_url,
        twitter_handle: data.twitter_handle,
        linkedin_url: data.linkedin_url,
        facebook_url: data.facebook_url,
        instagram_url: data.instagram_url,
        contact_page: data.contact_page,
        industry_keywords: data.industry_keywords,
        language: data.language
    };
    
    // Display the scraped data
    document.getElementById('url').textContent = scrapedData.url;
    document.getElementById('title').textContent = scrapedData.title || 'No title found';
    document.getElementById('description').textContent = scrapedData.description || 'No description found';
    
    // Display contact info if available
    const contactInfo = [];
    if (scrapedData.email) contactInfo.push(`📧 ${scrapedData.email}`);
    if (scrapedData.phone) contactInfo.push(`📞 ${scrapedData.phone}`);
    if (scrapedData.contact_page) contactInfo.push(`📄 Contact page found`);
    
    if (contactInfo.length > 0) {
        document.getElementById('contactSection').style.display = 'block';
        document.getElementById('contact').innerHTML = contactInfo.join('<br>');
    }
    
    // Display social media if available
    const socialInfo = [];
    if (scrapedData.twitter_handle) socialInfo.push(`🐦 @${scrapedData.twitter_handle}`);
    if (scrapedData.linkedin_url) socialInfo.push(`💼 LinkedIn`);
    if (scrapedData.facebook_url) socialInfo.push(`📘 Facebook`);
    if (scrapedData.instagram_url) socialInfo.push(`📷 Instagram`);
    
    if (socialInfo.length > 0) {
        document.getElementById('socialSection').style.display = 'block';
        document.getElementById('social').innerHTML = socialInfo.join(' • ');
    }
    
    // Display extra info
    const extraInfo = [];
    if (scrapedData.language) extraInfo.push(`Language: ${scrapedData.language}`);
    if (scrapedData.logo_url) extraInfo.push(`Logo found`);
    
    if (extraInfo.length > 0) {
        document.getElementById('extraInfo').textContent = extraInfo.join(' • ');
    }
}

// Function to save lead to backend
async function saveLead() {
    const statusDiv = document.getElementById('status');
    const saveBtn = document.getElementById('saveBtn');
    
    // Show loading state
    statusDiv.style.display = 'block';
    statusDiv.className = 'status loading';
    statusDiv.textContent = 'Saving...';
    saveBtn.disabled = true;
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(scrapedData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.className = 'status success';
            statusDiv.textContent = '✅ Lead saved successfully!';
            saveBtn.textContent = '✓ Saved';
        } else {
            throw new Error(result.error || 'Failed to save lead');
        }
    } catch (error) {
        statusDiv.className = 'status error';
        statusDiv.textContent = `❌ Error: ${error.message}`;
        saveBtn.disabled = false;
    }
}

// Initialize when popup opens
document.addEventListener('DOMContentLoaded', async () => {
    await scrapeCurrentPage();
    
    // Add click handler to save button
    document.getElementById('saveBtn').addEventListener('click', saveLead);
});
