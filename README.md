# Commercial Inventory Monthly Scraper

An automated Python web scraper running on GitHub Actions that tracks nationwide commercial vehicle and trailer listing counts from Commercial Truck Trader. 

The script runs automatically on the 1st of every month, extracting the total number of listings and saving the historical data directly to a CSV file within this repository. It requires zero external cloud hosting or database fees.

## 🚀 Features
* **Automated Scheduling:** Uses GitHub Actions cron jobs to run automatically once a month.
* **Anti-Bot Bypass:** Implements a try-except block that automatically routes requests through [ScraperAPI](https://www.scraperapi.com/) if the target site returns a `403 Forbidden` error.
* **Local CSV Storage:** Appends new data to `truck_data.csv` and commits the updated file straight back to the repository.

## 📂 Repository Structure
* `main.py`: The core Python scraping script using `requests` and `BeautifulSoup`.
* `requirements.txt`: Python dependencies.
* `.github/workflows/scrape.yml`: The GitHub Actions configuration file that dictates the schedule and permissions.
* `truck_data.csv`: The generated data file containing the historical scrape records (Date, Total Vehicles, Total Trailers). *(This file is generated automatically upon the first successful run).*

## 🛠️ Setup & Configuration

To run this in your own repository, you need to configure a single secret for the ScraperAPI fallback to work.

### 1. Add Your API Key
1. Get a free API key from ScraperAPI.
2. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret**.
4. Name the secret exactly `SCRAPER_API_KEY` and paste your key into the value field.

### 2. Check Repository Permissions
For the GitHub Action to save the CSV file back to the repository, it needs write access.
1. Go to **Settings** > **Actions** > **General**.
2. Scroll down to **Workflow permissions**.
3. Ensure **Read and write permissions** is selected. 

*(Note: The `scrape.yml` file also explicitly requests `contents: write` permissions to ensure this works smoothly).*

## ⚡ Running Manually
You do not have to wait for the 1st of the month to run the script. You can trigger it manually at any time:
1. Click on the **Actions** tab at the top of the repository.
2. Select **Monthly Truck Trader Scraper** from the left sidebar.
3. Click the **Run workflow** dropdown on the right and click the green **Run workflow** button.
4. Once completed, return to the `<> Code` tab to view the newly updated `truck_data.csv` file!
