# README: Robust Scraper for gov.il List Pages

This Python-based scraper is designed to robustly extract data from list pages on the **gov.il** website. It utilizes Selenium for dynamic content interaction and BeautifulSoup for structured data parsing, enabling detailed extraction of itemized content, including links, values, and titles.

## Features

1. **Dynamic Content Handling**:
   - Expands collapsible sections (e.g., "Show More" or "פרטים נוספים") automatically.

2. **Content Parsing**:
   - Extracts individual items from a structured list on a webpage.
   - Saves the extracted content into a CSV file (`filtered_content.csv`).
   - Supports extraction of associated metadata, including:
     - Item number.
     - Text content.
     - Links (if present).

3. **Multi-Page Navigation**:
   - Calculates and logs the next page URL to facilitate continuous scraping.

4. **Output Files**:
   - **`filtered_content.csv`**: Contains the structured content of each item.
   - **`parsed_items.csv`**: Includes parsed details, such as item numbers, titles, values, and links.

## Requirements

- Python 3.8 or higher.
- Google Chrome installed.
- Required Python libraries:
  - selenium
  - webdriver_manager
  - beautifulsoup4
  - pandas

Install the required libraries using pip:
```bash
pip install selenium webdriver_manager beautifulsoup4 pandas
```

## Usage

1. **Setup**:
   - Update the `URL` variable with the target list page URL from **gov.il**.

2. **Run the Script**:
   Execute the script using Python:
   ```bash
   python scraper.py
   ```

3. **Outputs**:
   - `filtered_content.txt`: Full HTML content of the page after dynamic expansion.
   - `filtered_content.csv`: Cleaned, structured table of content items.
   - `parsed_items.csv`: Further parsed details, including extracted links and metadata.

## How It Works

### Initialization
- The script initializes a Selenium WebDriver to handle dynamic loading of content.

### Content Extraction
- The script locates and expands all "Show More" buttons to load all items on the page.
- Extracted content is cleaned and structured into separate items based on unique markers.

### Parsing and Output
- Each item is processed with BeautifulSoup to identify titles, values, and links.
- Extracted data is saved to CSV files for further analysis.

### Multi-Page Support
- The script calculates the URL for the next page using the current page's `skip` parameter and logs it for subsequent use.

## Customization

1. **Modify Parsing Logic**:
   Adjust the BeautifulSoup parsing logic in the `parse_items_from_csv` function to accommodate specific changes in the HTML structure.

2. **Output Structure**:
   Customize the fields and output format in the `parsed_items.csv` file by modifying the relevant functions.

## Error Handling
- Robust exception handling ensures graceful handling of unexpected issues, such as missing elements or network errors.
- Logs warnings when extracted item counts do not match the expected totals.

## Limitations
- The scraper is designed for structured list pages. Significant changes to the page layout may require adjustments to the parsing logic.

## Future Enhancements
- Support for recursive scraping across all pages automatically.
- Improved error recovery for failed page loads or content expansion.
- Enhanced logging with detailed timestamps.

---
For further assistance or customization, feel free to contact the developer!

