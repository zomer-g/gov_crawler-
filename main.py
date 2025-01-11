# Ultimate Crawler Script
# Purpose: Crawl through multiple webpages and extract titles and links that are connected to each other, navigating through pages using a skip parameter.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Initialize Selenium WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless browser for faster execution
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to extract connected titles and links from the page
def extract_titles_and_links(soup):
    title_link_pairs = []

    # Look for <a> tags that wrap titles (e.g., h3 elements)
    links = soup.find_all('a', href=True)
    for link in links:
        # Check if the <a> tag contains a title element
        title = link.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if title:
            title_text = title.get_text(strip=True)
            link_href = link['href']
            if link_href.startswith("/"):
                link_href = "https://www.gov.il" + link_href  # Prepend base URL for relative links
            title_link_pairs.append((title_text, link_href))

    return title_link_pairs

# Process pages using skip logic
def process_pages(base_url):
    skip = 0
    page_count = 0
    while page_count < 3:  # Stop after processing the first 3 pages
        current_url = f"{base_url}&skip={skip}"
        print(f"Processing: {current_url}")

        # Load page in Selenium
        driver.get(current_url)
        time.sleep(3)  # Allow time for the page to load

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract connected titles and links
        title_link_pairs = extract_titles_and_links(soup)

        # Stop if no data is found on the page
        if not title_link_pairs:
            print("No data found on the page. Stopping.")
            break

        print(f"Found {len(title_link_pairs)} connected titles and links on the page.")
        for idx, (title, link) in enumerate(title_link_pairs, 1):
            print(f"Title {idx}: {title} -> Link: {link}")

        # Increment skip for the next page and update page count
        skip += 10
        page_count += 1

if __name__ == "__main__":
    # List of base URLs to process
    base_urls = [
        "https://www.gov.il/he/collectors/policies?officeId=c0d8ba69-e309-4fe5-801f-855971774a90&Type=2efa9b53-5df9-4df9-8e9d-21134511f368",
        "https://www.gov.il/he/collectors/policies?officeId=c0d8ba69-e309-4fe5-801f-855971774a90&limit=10&Type=84b81ddd-89fd-4f94-9121-1b69a307407f",
        "https://www.gov.il/he/collectors/publications?officeId=c0d8ba69-e309-4fe5-801f-855971774a90"
    ]

    # Initialize the driver
    driver = init_driver()

    try:
        for base_url in base_urls:
            process_pages(base_url)
    finally:
        driver.quit()
