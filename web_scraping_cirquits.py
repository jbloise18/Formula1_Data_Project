# ---------------------------------------
# F1 Circuits Scraper & Cleaner
# ---------------------------------------
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Fetch and parse the Wikipedia page
def fetch_page(url):
    """
    Fetches HTML content from the given URL and parses it using BeautifulSoup.
    Args:
        url (str): URL.
    Returns:
        BeautifulSoup object of the page content.
    """
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

# Find the table containing circuit data
def find_circuits_table(soup):
    """
    Searches for the table containing F1 circuit information.
    Args:
        soup: Parsed HTML page.
    Returns:
        BeautifulSoup table object or None if not found.
    """
    tables = soup.find_all('table', {'class': 'wikitable'})
    for t in tables:
        headers = [th.get_text(strip=True) for th in t.find_all('th')]
        if "Circuit" in headers:
            return t
    return None

# Parse the table into a DataFrame
def parse_circuits_table(table):
    """
    Extracts circuits data table into a DataFrame.
    Args:
        table (BeautifulSoup): Table containing circuits data.
    Returns:
        pandas.DataFrame with columns: circuit, location, country,
        last_length_used, circuit_laps, seasons
    """
    circuits, locations, countries, last_lengths, circuit_laps, seasons = [], [], [], [], [], []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 10:
            circuits.append(cols[0].get_text(strip=True))
            locations.append(cols[4].get_text(strip=True))
            countries.append(cols[5].get_text(strip=True))
            last_lengths.append(cols[6].get_text(strip=True))
            circuit_laps.append(cols[7].get_text(strip=True))
            seasons.append(cols[9].get_text(strip=True))
    df = pd.DataFrame({
        'circuit': circuits,
        'location': locations,
        'country': countries,
        'last_length_used': last_lengths,
        'circuit_laps': circuit_laps,
        'seasons': seasons
    })
    return df

# Clean the DataFrame (optional)
def clean_data(df):
    """
    Cleans the circuits DataFrame:
    - Standardizes column names
    - Strips whitespace
    """
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Main execution
def main():
    """
    Main function to:
    1. Fetch the web page
    2. Locate the circuits table
    3. Parse it into a DataFrame
    4. Clean and save the DataFrame as a CSV
    """
    url = 'https://'
    soup = fetch_page(url)
    table = find_circuits_table(soup)
    if table:
        df_circuits = parse_circuits_table(table)
        df_circuits = clean_data(df_circuits)
        df_circuits.to_csv('.csv', index=False)
        print("SAVED: '.csv'")
        print(df_circuits.head())
    else:
        print("No table found.")

if __name__ == "__main__":
    main()