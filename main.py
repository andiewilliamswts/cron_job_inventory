import os
import requests
from bs4 import BeautifulSoup
import datetime
import re
import time

def fetch_with_retries(url, scraper_api_key, retries=3):
    # Upgraded headers to perfectly mimic a real Chrome browser. 
    # This often bypasses firewalls on the very first direct request!
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Direct request failed. Switching to ScraperAPI...")
        for attempt in range(retries):
            try:
                payload = {
                    'api_key': scraper_api_key,
                    'url': url,
                    'premium': 'true',
                    'country_code': 'us'
                    # Removed antibot=true because it causes ScraperAPI to crash with a 500 error
                }
                
                fallback_response = requests.get('http://api.scraperapi.com/', params=payload, timeout=60)
                fallback_response.raise_for_status()
                return fallback_response.text
            except Exception as fallback_e:
                print(f"ScraperAPI attempt {attempt + 1} failed: {fallback_e}")
                if attempt < retries - 1:
                    print("Waiting 5 seconds and retrying...")
                    time.sleep(5)
                else:
                    return None

def get_count_from_html(html_content):
    if not html_content:
        return "API Error"
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Prioritize H1 tags
    h1_tags = soup.find_all('h1')
    for tag in h1_tags:
        text = tag.text.strip()
        match = re.search(r'\b\d+(?:,\d{3})*\b', text)
        if match:
            num_str = match.group(0)
            if num_str.startswith("202") and len(num_str) == 4 and "found" not in text.lower():
                continue
            return num_str
            
    # 2. Fallback to other elements
    elements = soup.find_all(['h2', 'h3', 'h4', 'span', 'strong'])
    for element in elements:
        text = element.text.strip()
        match = re.search(r'\b\d+(?:,\d{3})*\b', text)
        
        if match:
            lower_text = text.lower()
            num_str = match.group(0)
            if num_str.startswith("202") and len(num_str) == 4:
                continue
            if any(keyword in lower_text for keyword in ["truck", "trailer", "vehicle", "found", "result", "for sale", "listing"]):
                return num_str
                
    return "Count not found"

def main():
    scraper_api_key = os.environ.get("SCRAPER_API_KEY")
    webhook_url = os.environ.get("WEBHOOK_URL")
    
    url_ctt_vehicles = "https://www.commercialtrucktrader.com/trucks-for-sale" 
    url_ctt_trailers = "https://www.commercialtrucktrader.com/trucks-for-sale?class=TRAILER%7C9"
    
    # Adding ?page=1 alters the URL signature just enough to bypass Comvoy's strict path-based firewall block
    url_com
