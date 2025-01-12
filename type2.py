from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import csv

# Function to initialize Selenium WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless for faster execution
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to fetch page source using Selenium
def fetch_page_source(url):
    print(f"Fetching content from: {url}")

    driver = init_driver()
    try:
        driver.get(url)
        time.sleep(5)  # Allow the page to load
        return driver.page_source
    finally:
        driver.quit()

# Function to parse titles and links from page source
def parse_titles_and_links(page_source, page_url):
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Remove header and footer
    header = soup.find('header')
    footer = soup.find('footer')
    if header:
        header.decompose()
    if footer:
        footer.decompose()

    # Extract titles and associated file links
    parsed_data = []
    for row in soup.find_all('div', class_='row row-gov'):
        # Find the title
        h3 = row.find('h3', class_='txt bold ng-binding')
        if h3:
            title_text = h3.get_text(strip=True)

            # Find all links within the same row
            file_links = []
            for a in row.find_all('a', href=True):
                file_href = a['href']
                if file_href.startswith("/"):
                    file_href = "https://www.gov.il" + file_href  # Convert relative links to absolute

                # Ensure valid links and extract file titles
                if file_href != "#" and "BlobFolder" in file_href:
                    file_title = a.find('span', class_='xs-pr-5 width-88 ng-binding')
                    file_title_text = file_title.get_text(strip=True) if file_title else "N/A"
                    file_links.append((file_href, file_title_text))

            # Avoid adding rows without valid links
            if file_links:
                for link, file_title in file_links:
                    parsed_data.append((title_text, page_url, file_title, link, page_url))

    return parsed_data

# Function to iterate through pages

def scrape_all_pages(base_url):
    all_data = []
    skip = 0

    while True:
        page_url = f"{base_url}?skip={skip}"
        page_source = fetch_page_source(page_url)
        parsed_data = parse_titles_and_links(page_source, page_url)

        if not parsed_data:
            break  # Stop if no data is found on the page

        all_data.extend(parsed_data)
        skip += 20

    return all_data

# Main function
if __name__ == "__main__":
    # URLs to fetch
    urls = [
        "https://www.gov.il/he/Departments/DynamicCollectors/income-tax-represent-info-a",
        "https://www.gov.il/he/Departments/DynamicCollectors/guidelines-state-attorney"
    ]

    # File to save results
    output_file = "parsed_results.csv"

    # Write results to CSV
    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Page Link", "File Title", "File Link", "Source Page"])

        for base_url in urls:
            data = scrape_all_pages(base_url)
            writer.writerows(data)

    print(f"Results written to {output_file}")
