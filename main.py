import os
import requests
from bs4 import BeautifulSoup
import datetime
import re
import time

def fetch_with_retries(url, scraper_api_key, retries=4, use_render=False):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
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
                }
                
                # Only activate the virtual browser if the specific site requires it
                if use_render:
                    payload['render'] = 'true'
                    
                # Increased timeout to 90s to give the virtual browser time to apply JS filters
                fallback_response = requests.get('http://api.scraperapi.com/', params=payload, timeout=90)
                fallback_response.raise_for_status()
                return fallback_response.text
            except Exception as fallback_e:
                print(f"ScraperAPI attempt {attempt + 1} failed: {fallback_e}")
                if attempt < retries - 1:
                    print("Waiting 10 seconds and retrying...")
                    time.sleep(10)
                else:
                    return None

def get_count_from_html(html_content):
    if not html_content:
        return "API Error"
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Prioritize H1 tags: The actual search result count is almost always in the H1 tag
    h1_tags = soup.find_all('h1')
    for tag in h1_tags:
        match = re.search(r'\b\d{1,3}(?:,\d{3})+\b', tag.text)
        if match:
            return match.group(0)
            
    # 2. Fallback to other elements only if an H1 number isn't found
    elements = soup.find_all(['h2', 'h3', 'h4', 'span', 'strong'])
    for element in elements:
        text = element.text.strip()
        match = re.search(r'\b\d{1,3}(?:,\d{3})+\b', text)
        
        if match:
            lower_text = text.lower()
            if any(keyword in lower_text for keyword in ["truck", "trailer", "vehicle", "found", "result", "for sale", "listing"]):
                return match.group(0)
                
    return "Count not found"

def main():
    scraper_api_key = os.environ.get("SCRAPER_API_KEY")
    webhook_url = os.environ.get("WEBHOOK_URL")
    
    url_ctt_vehicles = "https://www.commercialtrucktrader.com/trucks-for-sale" 
    url_ctt_trailers = "https://www.commercialtrucktrader.com/trucks-for-sale?class=TRAILER%7C9"
    
    url_comvoy_vehicles = "https://www.comvoy.com/vehicles"
    url_comvoy_trailers = "https://www.comvoy.com/vehicles?listing_type=trailer" 
    
    # CTT does not need JavaScript rendering
    print("Fetching Commercial Truck Trader Vehicles...")
    ctt_vehicles = get_count_from_html(fetch_with_retries(url_ctt_vehicles, scraper_api_key, use_render=False))
    
    print("Fetching Commercial Truck Trader Trailers...")
    ctt_trailers = get_count_from_html(fetch_with_retries(url_ctt_trailers, scraper_api_key, use_render=False))
    
    # Comvoy requires JavaScript rendering to apply the trailer filters properly
    print("Fetching Comvoy Vehicles...")
    comvoy_vehicles = get_count_from_html(fetch_with_retries(url_comvoy_vehicles, scraper_api_key, use_render=True))
    
    print("Fetching Comvoy Trailers...")
    comvoy_trailers = get_count_from_html(fetch_with_retries(url_comvoy_trailers, scraper_api_key, use_render=True))
    
    today = str(datetime.date.today())
    
    payload = {
        "date": today,
        "ctt_vehicles": ctt_vehicles,
        "ctt_trailers": ctt_trailers,
        "comvoy_vehicles": comvoy_vehicles,
        "comvoy_trailers": comvoy_trailers
    }
    
    try:
        response = requests.post(webhook_url, data=payload)
        if response.text == "Success":
            print(f"Success! Appended data for {today}:")
            print(f"CTT Vehicles: {ctt_vehicles} | CTT Trailers: {ctt_trailers}")
            print(f"Comvoy Vehicles: {comvoy_vehicles} | Comvoy Trailers: {comvoy_trailers}")
        else:
            print(f"Failed to append. Response: {response.text}")
    except Exception as e:
        print(f"Webhook request failed: {e}")

if __name__ == "__main__":
    main()
