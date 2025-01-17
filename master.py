# Purpose of the script: Extract specific visible content after "<!-- Items -->", log object counts, log the link of the "הבא" button, and create a CSV with split content.
# The script ensures all expandable sections are opened before extracting content.

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# Define the URL to extract
URL = "https://www.gov.il/he/departments/dynamiccollectors/conditionalagreements?skip=0"

# Initialize the WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to expand all expandable content
def expand_content(driver):
    try:
        while True:
            # Find "Show More" or "פרטים נוספים" buttons
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Show More') or contains(text(), 'פרטים נוספים')]")
            if not buttons:
                break

            for button in buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", button)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
                    time.sleep(1)  # Allow content to load
                except Exception as e:
                    print(f"Could not click button: {e}")
    except Exception as e:
        print(f"Error while expanding content: {e}")

# Function to extract content after "<!-- Items -->" and log object counts
def extract_content_to_txt_and_csv(driver, txt_output_file, csv_output_file):
    try:
        # Remove header and footer before extracting content
        driver.execute_script(
            "document.querySelector('header').remove(); document.querySelector('footer').remove();"
        )

        # Get the rendered HTML of the page
        content = driver.execute_script("return document.documentElement.outerHTML;")
        
        # Extract content after "<!-- Items -->"
        items_content = content.split("<!-- Items -->")[1]
        
        # Find and log the number of objects and total results
        match = re.search(r"פריט מספר \d+ מתוך (\d+) תוצאות", items_content)
        if match:
            total_items = int(match.group(1))
            print(f"Total items: {total_items}")
        else:
            print("No item count found.")

        # Save full content to TXT file
        with open(txt_output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(items_content)
        print(f"Content successfully written to {txt_output_file}")

        # Split content into individual items
        items = re.split(r"פריט מספר \d+ מתוך \d+ תוצאות", items_content)
        items = [item.strip() for item in items if item.strip()]  # Remove empty items

        if len(items) != total_items:
            print("Warning: Number of extracted items does not match the total items.")

        # Save split content to CSV file
        with open(csv_output_file, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Item Content"])
            for i, item in enumerate(items, start=1):
                csv_writer.writerow([item])

        print(f"Content successfully written to {csv_output_file}")

    except Exception as e:
        print(f"Failed to write content to file: {e}")

# Function to log the link of the "הבא" button
def log_next_button_link(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[@ng-click='gotoPage(currentPage + 1)']")
            )
        )
        # Log the link, even if href is empty (Angular handles the logic)
        next_link = next_button.get_attribute("href")
        if not next_link:
            current_url = driver.current_url
            next_link = re.sub(r"skip=\d+", lambda x: f"skip={int(x.group(0).split('=')[1]) + 10}", current_url)
        print(f"Next button link: {next_link}")
    except Exception as e:
        print(f"Could not find the 'הבא' button: {e}")

# Main script
def main():
    driver = setup_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Expand all content
        expand_content(driver)

        # Extract and save content to TXT and CSV files
        txt_output_file = "filtered_content.txt"
        csv_output_file = "filtered_content.csv"
        extract_content_to_txt_and_csv(driver, txt_output_file, csv_output_file)

        # Log the link of the "הבא" button
        log_next_button_link(driver)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
