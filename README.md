# Google Maps Business Scraper Streamlit Web App

## Overview

Google Maps Business Scraper is a Streamlit application designed to scrape business details from Google Maps based on a search term. It extracts business names, addresses, websites, phone numbers, review counts, and average reviews. The scraped data is then saved in an Excel file for easy access and download.

## Features

- **User Input**: Enter a search term and specify the number of results to scrape.
- **Progress Indicator**: A progress bar and elapsed time indicator to show the scraping process.
- **Data Export**: Export the scraped data to an Excel file and download it directly from the app.
- **Styled Interface**: Custom background color and personalized branding.

## Installation

1. **Clone the Repository**
    ```sh
    git clone https://github.com/sabsar42/Google-Map-Scrapper-Streamlit.git
    cd Google-Map-Scrapper-Streamlit
    ```

2. **Create a Virtual Environment**
    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment**

    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. **Install Required Packages**
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Streamlit App**
    ```sh
    streamlit run main.py
    ```

2. **Open the App in a Browser**
    After running the command, Streamlit will display a URL in the terminal (usually `http://localhost:8501`). Open this URL in your browser.

3. **Enter Search Term and Number of Results**
    - Enter the desired search term.
    - Specify the number of results to scrape.

4. **Scrape and Download Data**
    - Click on the **Scrape** button to start scraping.
    - After completion, download the Excel file containing the scraped data.

## Code Structure

- **main.py**: Contains the main Streamlit application code.
- **scraper.py**: Handles the scraping logic using Playwright.
- **models.py**: Defines data models using Python's `dataclass`.

## Example

1. **Enter Search Term**: "Coffee Shops in New York"
2. **Specify Number of Results**: 100
3. **Click Scrape**: The app scrapes data and displays progress.
4. **Download Excel File**: Click the download button to get the results.

## Contributions

Contributions are welcome! Feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Author

Developed by Shakib Asbar.
