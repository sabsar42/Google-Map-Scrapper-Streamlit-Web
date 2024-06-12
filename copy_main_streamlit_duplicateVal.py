import streamlit as st
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import os
import logging
from dataclasses import dataclass, asdict, field
import datetime
import pytz

asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class Business:
    """holds business data"""
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None


@dataclass
class BusinessList:
    """holds list of Business objects, and save to both excel and csv"""
    business_list: list[Business] = field(default_factory=list)
    save_at = 'output'

    def dataframe(self):
        """transform business_list to pandas dataframe"""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_")

    def save_to_excel(self, filename):
        """saves pandas dataframe to excel (xlsx) file and returns file path"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        file_path = f"{self.save_at}/{filename}.xlsx"
        try:
            self.dataframe().to_excel(file_path, index=False)
            logging.info(f"Saved data to {file_path}")
            return file_path  # Return the file path after saving
        except Exception as e:
            logging.error(f"Failed to save data to Excel: {e}")
            return None

    def save_to_csv(self, filename):
        """saves pandas dataframe to csv file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        file_path = f"{self.save_at}/{filename}.csv"
        try:
            self.dataframe().to_csv(file_path, index=False)
            logging.info(f"Saved data to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save data to CSV: {e}")


async def scrape_business(search_term, total):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("https://www.google.com/maps", timeout=60000)
            await page.wait_for_timeout(5000)

            await page.fill('//input[@id="searchboxinput"]', search_term)
            await page.wait_for_timeout(3000)

            await page.keyboard.press("Enter")
            await page.wait_for_timeout(5000)

            await page.hover(
                '//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            listings = []

            while True:
                await page.mouse.wheel(0, 10000)
                await page.wait_for_timeout(2000)

                current_count = await page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()
                if current_count >= total:
                    # Await the locator and get all elements first
                    all_listings = await page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()

                    # Slice the desired number of listings
                    listings = all_listings[:total]

                    break

                elif current_count == previously_counted:
                    # Similarly, await the locator to get all elements
                    listings = await page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()

                    break

                else:
                    previously_counted = current_count

            business_list = BusinessList()

            for listing in listings:
                try:
                    await listing.click()
                    await page.wait_for_timeout(
                        3000)  # Adjust this timeout as needed

                    name_css_selector = 'h1.DUwDvf.lfPIob'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                    business = Business()

                    if await page.locator(name_css_selector).count() > 0:
                        business.name = await page.locator(name_css_selector
                                                           ).inner_text()
                    else:
                        business.name = ""

                    if await page.locator(address_xpath).count() > 0:
                        address_elements = await page.locator(address_xpath
                                                              ).all()
                        if address_elements:
                            business.address = await address_elements[
                                0].inner_text()
                        else:
                            business.address = ""
                    else:
                        business.address = ""

                    if await page.locator(website_xpath).count() > 0:
                        website_elements = await page.locator(website_xpath
                                                              ).all()
                        if website_elements:
                            business.website = await website_elements[
                                0].inner_text()
                        else:
                            business.website = ""
                    else:
                        business.website = ""

                    if await page.locator(phone_number_xpath).count() > 0:
                        phone_elements = await page.locator(phone_number_xpath
                                                            ).all()
                        if phone_elements:
                            business.phone_number = await phone_elements[
                                0].inner_text()
                        else:
                            business.phone_number = ""
                    else:
                        business.phone_number = ""

                    if await page.locator(review_count_xpath).count() > 0:
                        review_count_text = await page.locator(
                            review_count_xpath).inner_text()
                        business.reviews_count = int(
                            review_count_text.split()[0].replace(',',
                                                                 '').strip())
                    else:
                        business.reviews_count = None

                    if await page.locator(reviews_average_xpath).count() > 0:
                        reviews_average_text = await page.locator(
                            reviews_average_xpath).get_attribute('aria-label')
                        if reviews_average_text:
                            business.reviews_average = float(
                                reviews_average_text.split()[0].replace(
                                    ',', '.').strip())
                        else:
                            business.reviews_average = None
                    else:
                        business.reviews_average = None

                    business_list.business_list.append(business)
                except Exception as e:
                    logging.error(
                        f'Error occurred while scraping listing: {e}')

            await browser.close()
            return business_list

        except Exception as e:
            logging.error(f'Error occurred during scraping: {e}')
            await browser.close()
            return BusinessList()


async def main():
    st.title("Google Maps Business Scraper")

    search_term = st.text_input("Enter search term")
    total_results = st.number_input("Enter number of results",
                                    min_value=1,
                                    max_value=1000,
                                    value=300)

    if st.button("Scrape"):
        if not search_term:
            st.error("Please enter a search term")
        else:
            with st.spinner("Scraping data..."):
                business_list = await scrape_business(search_term,
                                                      total_results)
                bangladesh_timezone = pytz.timezone('Asia/Dhaka')

                current_datetime = datetime.datetime.now(
                    bangladesh_timezone).strftime("%Y%m%d_%H%M%S")
                search_for_filename = search_term.replace(' ', '_')

                excel_filename = f"{current_datetime}_rows_{search_for_filename}"

                # Save to Excel and get the file path
                excel_file_path = business_list.save_to_excel(excel_filename)

                if excel_file_path:
                    # Display the file path in a styled box
                    st.info(f"Download your file from the button below:")
                    st.markdown("---")
                    st.markdown(f"**File Location:** `{excel_file_path}`")
                    st.markdown("---")

                    # Provide a download button for the Excel file
                    st.download_button(label="Download Excel File",
                                       data=open(excel_file_path, 'rb').read(),
                                       file_name=f"{excel_filename}.xlsx",
                                       mime="application/octet-stream")

                st.success("Scraping completed!")
                st.dataframe(business_list.dataframe())


if __name__ == "__main__":
    asyncio.run(main())
