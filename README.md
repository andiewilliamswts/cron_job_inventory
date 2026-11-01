# Commercial Vehicle Inventory Scraper

An automated Python web scraper running on GitHub Actions that tracks nationwide commercial vehicle and trailer listing counts from **Commercial Truck Trader** and **Comvoy**. 

The script runs automatically at the end of every month, extracting the total number of listings and pushing the historical data directly into a Google Sheet via a webhook. It bypasses aggressive enterprise anti-bot protections (like Datadome and Cloudflare) and requires zero external cloud hosting fees.

## 🚀 Features
* **Automated Scheduling:** Uses GitHub Actions cron jobs to run automatically on the 1st of the month at 01:00 UTC (which equals 5:00 PM PST on the last day of the previous month).
* **Advanced Anti-Bot Bypass:** Utilizes Chrome header spoofing and URL signature manipulation to bypass initial firewalls, with a resilient fallback routing system through [ScraperAPI](https://www.scraperapi.com/) using US-based premium residential proxies.
* **Direct Google Sheets Integration:** Sends data instantly to a Google Sheet using a lightweight Google Apps Script Webhook (No Google Cloud Service Accounts or authentication keys required).
* **Multi-Site Scraping:** Reliably extracts 4 distinct metrics: CTT Total Vehicles, CTT Trailers, Comvoy Total Vehicles, and Comvoy Trailers.

## 📂 Repository Structure
* `main.py`: The core Python scraping script using `requests` and `BeautifulSoup4` with advanced Regex parsing.
* `requirements.txt`: Python dependencies (`requests`, `beautifulsoup4`).
* `.github/workflows/scrape.yml`: The GitHub Actions configuration file that manages the cron schedule and execution environment.

## 🛠️ Setup & Configuration

To run this in your own environment, you need to configure two GitHub Secrets.

### 1. Configure GitHub Secrets
In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions**, click **New repository secret**, and add the following:
* `SCRAPER_API_KEY`: Your API key from ScraperAPI to handle bot-protection fallbacks.
* `WEBHOOK_URL`: The deployed Web App URL from your Google Apps Script.

### 2. Google Sheets Webhook Setup
To receive the data, your target Google Sheet must have a tab named `Inventory` and an attached Apps Script:
1. In Google Sheets, click **Extensions** > **Apps Script**.
2. Paste the following receiver code (replace the placeholder ID with your actual Spreadsheet ID found in its URL):
```javascript
function doPost(e) {
  // Hardcoded to your exact spreadsheet ID for a guaranteed connection
  var sheet = SpreadsheetApp.openById("YOUR_SPREADSHEET_ID_HERE").getSheetByName("Inventory");
  
  var date = e.parameter.date;
  var ctt_vehicles = e.parameter.ctt_vehicles;
  var ctt_trailers = e.parameter.ctt_trailers;
  var comvoy_vehicles = e.parameter.comvoy_vehicles;
  var comvoy_trailers = e.parameter.comvoy_trailers;
  
  sheet.appendRow([date, ctt_vehicles, ctt_trailers, comvoy_vehicles, comvoy_trailers]);
  
  return ContentService.createTextOutput("Success");
}
