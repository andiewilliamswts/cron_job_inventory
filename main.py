import os
import requests
from bs4 import BeautifulSoup
import datetime
import re

def get_ctt_count(url, scraper_api_key):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    try:
        # Added timeout so it doesn't hang forever
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"CTT Request failed. Switching to ScraperAPI...")
        try:
            # &render=true helps bypass advanced bot protection
            fallback_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}&render=true"
            fallback_response = requests.get(fallback_url, timeout=60)
            fallback_response.raise_for_status()
            html_content = fallback_response.text
        except Exception as fallback_e:
            print(f"ScraperAPI also failed for CTT: {fallback_e}")
            return "API Error"
            
    soup = BeautifulSoup(html_content, 'html.parser')
    results_header = soup.find(lambda tag: tag.name == "h3" and "For Sale" in tag.text)
    
    if results_header:
        match = re.search(r'[\d,]+', results_header.text.strip())
        return match.group(0) if match else "Count not found"
    return "Header not found"

def get_comvoy_count(url, scraper_api_key):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Blocked by Comvoy. Switching to ScraperAPI...")
        try:
            # &render=true is critical here for Comvoy
            fallback_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}&render=true"
            fallback_response = requests.get(fallback_url, timeout=60)
            fallback_response.raise_for_status()
            html_content = fallback_response.text
        except Exception as fallback_e:
            print(f"ScraperAPI also failed for Comvoy: {fallback_e}")
            return "API Error"
            
    soup = BeautifulSoup(html_content, 'html.parser')
    
    headings = soup.find_all(['h1', 'h2', 'span'])
    for heading in headings:
        text = heading.text.strip()
        if ("Truck" in text or "Vehicle" in text or "Trailer" in text or "Found" in text) and any(char.isdigit() for char in text):
            match = re.search(r'[\d,]+', text)
            if match:
                return match.group(0)
                
    return "Header not found"

def main():
    scraper_api_key = os.environ.get("SCRAPER_API_KEY")
    webhook_url = os.environ.get("WEBHOOK_URL")
    
    url_ctt_vehicles = "https://github.com/andiewilliamswts/cron_job_inventory/actions/runs/41289152258/job/124796590376#step:5:22" 
    url_ctt_trailers = "https://www.commercialtrucktrader.com/trucks-for-sale?class=TRAILER%7C9"
    
    url_comvoy_vehicles = "https://www.comvoy.com/vehicles"
    url_comvoy_trailers = "https://github.com/andiewilliamswts/cron_job_inventory2?body_type=Trailer" 
    
    print("Fetching Commercial Truck Trader data...")
    ctt_vehicles = get_ctt_count(url_ctt_vehicles, scraper_api_key)
    ctt_trailers = get_ctt_count(url_ctt_trailers, scraper_api_key)
    
    print("Fetching Comvoy data...")
    comvoy_vehicles = get_comvoy_count(url_comvoy_vehicles, scraper_api_key)
    comvoy_trailers = get_comvoy_count(url_comvoy_trailers, scraper_api_key)
    
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
