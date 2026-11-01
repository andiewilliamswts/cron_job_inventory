import os
import requests
from bs4 import BeautifulSoup
import datetime
import re

def get_ctt_count(url, scraper_api_key):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print(f"403 Forbidden for CTT. Switching to ScraperAPI...")
            fallback_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}"
            fallback_response = requests.get(fallback_url)
            fallback_response.raise_for_status()
            html_content = fallback_response.text
        else:
            return "Error"
            
    soup = BeautifulSoup(html_content, 'html.parser')
    results_header = soup.find(lambda tag: tag.name == "h3" and "For Sale" in tag.text)
    
    if results_header:
        match = re.search(r'[\d,]+', results_header.text.strip())
        return match.group(0) if match else "Count not found"
    return "Header not found"

def get_comvoy_count(url, scraper_api_key):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.HTTPError as e:
        if response.status_code in [403, 401]:
            print(f"Blocked by Comvoy. Switching to ScraperAPI...")
            fallback_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}"
            fallback_response = requests.get(fallback_url)
            fallback_response.raise_for_status()
            html_content = fallback_response.text
        else:
            return "Error"
            
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Comvoy usually puts their total count in an H1 or H2 tag containing words like "Trucks", "Vehicles", or "Found"
    # We will search the page for the first major heading that contains a formatted number
    headings = soup.find_all(['h1', 'h2', 'span'])
    for heading in headings:
        text = heading.text.strip()
        # Look for a number pattern like "15,000" inside text that might say "15,000 Work Trucks"
        if ("Truck" in text or "Vehicle" in text or "Trailer" in text) and any(char.isdigit() for char in text):
            match = re.search(r'[\d,]+', text)
            if match:
                return match.group(0)
                
    return "Header not found"

def main():
    scraper_api_key = os.environ.get("SCRAPER_API_KEY")
    webhook_url = os.environ.get("WEBHOOK_URL")
    
    # Target URLs
    url_ctt_vehicles = "https://github.com/andiewilliamswts/cron_job_inventory1" 
    url_ctt_trailers = "https://www.commercialtrucktrader.com/trucks-for-sale?class=TRAILER%7C9"
    
    # Using clean Comvoy URLs (removing the temporary security tokens you provided so it doesn't expire)
    url_comvoy_vehicles = "https://www.comvoy.com/vehicles"
    # Adjust this URL if Comvoy uses a specific query parameter for trailers, e.g., ?body_type=Trailer
    url_comvoy_trailers = "https://www.comvoy.com/vehicles?body_type=Trailer" 
    
    print("Fetching Commercial Truck Trader data...")
    ctt_vehicles = get_ctt_count(url_ctt_vehicles, scraper_api_key)
    ctt_trailers = get_ctt_count(url_ctt_trailers, scraper_api_key)
    
    print("Fetching Comvoy data...")
    comvoy_vehicles = get_comvoy_count(url_comvoy_vehicles, scraper_api_key)
    comvoy_trailers = get_comvoy_count(url_comvoy_trailers, scraper_api_key)
    
    today = str(datetime.date.today())
    
    # Payload matching the updated Apps Script Webhook
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
