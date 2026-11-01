import os
import requests
from bs4 import BeautifulSoup
import datetime
import re
import csv

def get_listing_count(url, scraper_api_key):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print(f"403 Forbidden. Switching to ScraperAPI...")
            fallback_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}"
            fallback_response = requests.get(fallback_url)
            fallback_response.raise_for_status()
            html_content = fallback_response.text
        else:
            print(f"HTTP Error: {e}")
            return "Error"
            
    soup = BeautifulSoup(html_content, 'html.parser')
    
    results_header = soup.find(lambda tag: tag.name == "h3" and "For Sale" in tag.text)
    
    if results_header:
        text = results_header.text.strip()
        match = re.search(r'[\d,]+', text)
        return match.group(0) if match else "Count not found"
    
    return "Header not found"

def main():
    scraper_api_key = os.environ.get("SCRAPER_API_KEY")
    
    url_all_vehicles = "https://www.commercialtrucktrader.com/trucks-for-sale"
    url_all_trailers = "https://www.commercialtrucktrader.com/trucks-for-sale?class=TRAILER%7C9"
    
    print("Fetching total vehicles nationwide...")
    total_vehicles = get_listing_count(url_all_vehicles, scraper_api_key)
    
    print("Fetching total trailers nationwide...")
    total_trailers = get_listing_count(url_all_trailers, scraper_api_key)
    
    today = str(datetime.date.today())
    file_exists = os.path.isfile('truck_data.csv')
    
    # Write data to a local CSV file
    with open('truck_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write headers if the file is brand new
        if not file_exists:
            writer.writerow(['Date', 'Total Vehicles', 'Total Trailers'])
        
        writer.writerow([today, total_vehicles, total_trailers])
        
    print(f"Successfully appended to CSV: {today} | Vehicles: {total_vehicles} | Trailers: {total_trailers}")

if __name__ == "__main__":
    main()