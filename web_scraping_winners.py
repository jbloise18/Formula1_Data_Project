# ---------------------------------------
# F1 Race Results Scraper & Cleaner
# ---------------------------------------
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from io import StringIO

# Initialize Selenium driver
def init_driver():
    """
    Initializes a Selenium Chrome WebDriver.
    Returns:
        Selenium WebDriver object
    """
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

# Scrape a single year's races
def scrape_year(driver, year):
    """
    Scrapes race results for a specific year from web page.
    Args:
        driver: Selenium WebDriver object
        year: int, the year to scrape
    Returns:
        pandas.DataFrame with race results for the year
        or None if no table found.
    """
    print(f"Saving data for: {year}...")
    url = f"https://"
    driver.get(url)
    time.sleep(5)  # Wait for page to load completely
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='f1-table')
    if table:
        df = pd.read_html(StringIO(str(table)))[0]  # Avoid FutureWarning
        df['year'] = year
        return df
    else:
        print(f"No data for: {year}.")
        return None

# Scrape multiple years
def scrape_all(years):
    """
    Scrapes race results for multiple years.
    Args:
        years: iterable of years to scrape
    Returns:
        pandas.DataFrame concatenating all years
    """
    driver = init_driver()
    all_races = []
    for year in years:
        df_year = scrape_year(driver, year)
        if df_year is not None:
            all_races.append(df_year)
    driver.quit()
    return pd.concat(all_races, ignore_index=True) if all_races else pd.DataFrame()

# Clean the scraped data
def clean_data(df):
    """
    Cleans the scraped race results:
    - Standardizes column names
    - Converts laps to numeric
    - Combines date and year into full datetime
    """
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    if 'laps' in df.columns:
        df['laps'] = pd.to_numeric(df['laps'], errors='coerce')
    if 'date' in df.columns and 'year' in df.columns:
        df['full_date'] = df['date'].astype(str) + ' ' + df['year'].astype(str)
        df['date'] = pd.to_datetime(df['full_date'], format='%d %b %Y', errors='coerce')
        df.drop(columns=['full_date'], inplace=True)
    return df

# Main execution
def main():
    """
    Main function to:
    1. Initialize Selenium WebDriver
    2. Scrape race results for the specified years
    3. Clean the data
    4. Save the DataFrame as a CSV
    """
    years = range(1950, 2025)  # Example: scrape 1950-1959
    df_all_races = scrape_all(years)
    if not df_all_races.empty:
        df_all_races = clean_data(df_all_races)
        df_all_races.to_csv('.csv', index=False)
        print("SAVED: '.csv'.")
    else:
        print("No data found.")

if __name__ == "__main__":
    main()