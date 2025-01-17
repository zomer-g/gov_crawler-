# Purpose of the script: Extract specific visible content after "<!-- Items -->", log object counts, and log the link of the "הבא" button.
# The script ensures all expandable sections are opened before extracting content.

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
            buttons = driver.find_elements(By.XPATH,
                                           "//button[contains(text(), 'Show More') or contains(text(), 'פרטים נוספים')]")
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
def extract_content_to_txt(driver, output_file):
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
        match = re.search(r"פריט מספר (\d+) מתוך (\d+) תוצאות", items_content)
        if match:
            current_item = match.group(1)
            total_items = match.group(2)
            print(f"Current item: {current_item}, Total items: {total_items}")
        else:
            print("No item count found.")

        # Save extracted content to TXT file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(items_content)
        print(f"Content successfully written to {output_file}")
    except Exception as e:
        print(f"Failed to write content to file: {e}")


# Function to log the link of the "הבא" button
def log_next_button_link(driver):
    try:
        # Retrieve the current URL
        current_url = driver.current_url

        # Extract the current skip value and increment it
        match = re.search(r"skip=(\d+)", current_url)
        if match:
            current_skip = int(match.group(1))
            next_skip = current_skip + 10  # Assuming 10 items per page
            next_url = re.sub(r"skip=\d+", f"skip={next_skip}", current_url)
            print(f"Next page URL: {next_url}")
        else:
            print("Could not determine the next page URL from the current URL.")
    except Exception as e:
        print(f"An error occurred while determining the next page URL: {e}")



# Main script
def main():
    driver = setup_driver()
    try:
        driver.get(URL)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Expand all content
        expand_content(driver)

        # Extract and save content to TXT file
        output_file = "filtered_content.txt"
        extract_content_to_txt(driver, output_file)

        # Log the link of the "הבא" button
        log_next_button_link(driver)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
