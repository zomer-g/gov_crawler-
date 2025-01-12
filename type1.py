# Ultimate Crawler Script
# Purpose: Crawl through multiple webpages and extract titles and links that are connected to each other, navigating through pages using a skip parameter. For each link, navigate to the page and extract file links. Ignore header and footer content, and write the results to a CSV file.

import csv
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

    # Ignore header and footer sections
    header = soup.find('header')
    footer = soup.find('footer')
    if header:
        header.decompose()
    if footer:
        footer.decompose()

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

# Function to extract file links from a given page
def extract_file_links(page_url):
    print(f"Visiting link: {page_url}")
    driver.get(page_url)
    time.sleep(3)  # Allow time for the page to load

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    file_links = []

    # Look for file download links
    file_anchors = soup.find_all('a', class_='files-groups_files_group_link__mCbGz', href=True)
    for file_anchor in file_anchors:
        file_title = file_anchor.get('title', 'No Title').strip()
        file_href = file_anchor['href']
        if file_href.startswith("/"):
            file_href = "https://www.gov.il" + file_href  # Prepend base URL for relative links
        file_links.append((file_title, file_href))

    return file_links

# Process pages using skip logic
def process_pages(base_url, csv_writer):
    skip = 0
    while True:  # Process all pages until no data is found
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

            # Visit the link and extract file links
            file_links = extract_file_links(link)
            for file_idx, (file_title, file_link) in enumerate(file_links, 1):
                print(f"  File {file_idx}: {file_title} -> Link: {file_link}")
                # Write to CSV
                csv_writer.writerow([title, link, file_title, file_link, current_url])

        # Increment skip for the next page
        skip += 10

if __name__ == "__main__":
    # List of base URLs to process
    base_urls = [
        "https://www.gov.il/he/collectors/policies?officeId=c0d8ba69-e309-4fe5-801f-855971774a90&Type=2efa9b53-5df9-4df9-8e9d-21134511f368",
        "https://www.gov.il/he/collectors/policies?officeId=c0d8ba69-e309-4fe5-801f-855971774a90&limit=10&Type=84b81ddd-89fd-4f94-9121-1b69a307407f",
        "https://www.gov.il/he/collectors/publications?officeId=c0d8ba69-e309-4fe5-801f-855971774a90"
    ]

    # Initialize the driver
    driver = init_driver()

    # Open CSV file for writing
    with open('output.csv', mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header row
        csv_writer.writerow(['Title', 'Page Link', 'File Title', 'File Link', 'Source Page'])

        try:
            for base_url in base_urls:
                process_pages(base_url, csv_writer)
        finally:
            driver.quit()
