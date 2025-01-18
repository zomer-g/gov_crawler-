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

        # Adjust the last item's end using the specified boundary phrase
        if items:
            last_item_boundary = "</li><!-- end ngRepeat: item in dynamicCtrl.ViewModel.dataResults -->"
            if last_item_boundary in items[-1]:
                items[-1] = items[-1].split(last_item_boundary)[0]

        # Save the content as a structured table with URL, item number, and content
        with open(csv_output_file, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(["URL", "Item Number", "Content"])

            # Extract content starting only after the relevant marker
            content_start = re.search(r"פריט מספר \d+ מתוך \d+ תוצאות", items_content)
            if content_start:
                items_content = items_content[content_start.start():]  # Trim content before the first valid item

            items = re.split(r"פריט מספר \d+ מתוך \d+ תוצאות", items_content)
            items = [item.strip() for item in items if item.strip()]  # Remove empty items

            for i, item in enumerate(items, start=1):
                # Ensure content is properly sanitized and aligned
                item_content = " ".join(item.splitlines()).strip()  # Flatten multi-line content into a single line
                if item_content:  # Skip empty or invalid content
                    csv_writer.writerow([URL, i, item_content])

        print(f"Content successfully written to {csv_output_file}")

        # Log the last item
        if items:
            print(f"Last item on the page (refined):\n{items[-1]}")
        else:
            print("No items found.")

        return total_items

    except Exception as e:
        print(f"Failed to write content to file: {e}")
        return 0


# Function to calculate and log the next page link
def calculate_next_page_link(current_url, total_items):
    try:
        if "?skip=" in current_url:
            current_skip = int(re.search(r"skip=(\d+)", current_url).group(1))
            next_skip = current_skip + total_items
            next_url = re.sub(r"skip=\d+", f"skip={next_skip}", current_url)
        else:
            next_url = f"{current_url}?skip={total_items}"
        print(f"Next page link: {next_url}")
        return next_url
    except Exception as e:
        print(f"Could not calculate next page link: {e}")
        return None


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
        total_items = extract_content_to_txt_and_csv(driver, txt_output_file, csv_output_file)

        # Calculate the next page link
        if total_items > 0:
            calculate_next_page_link(URL, total_items)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
