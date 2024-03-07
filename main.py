import time
import logging
import csv
import urllib.parse
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDriver:

    location_data = {}

    def __init__(self, headless=False):
        self.driver = self._driver(headless=headless)

        self.location_data["name"] = "NA"
        self.location_data["rating"] = "NA"
        self.location_data["reviews_count"] = "NA"
        self.location_data["location"] = "NA"
        self.location_data["contact"] = "NA"
        self.location_data["website"] = "NA"
        self.location_data["booking_link"] = "NA"
        self.location_data["Time"] = {
            "Monday": "NA",
            "Tuesday": "NA",
            "Wednesday": "NA",
            "Thursday": "NA",
            "Friday": "NA",
            "Saturday": "NA",
            "Sunday": "NA",
        }
        # self.location_data["Reviews"] = []
        # self.location_data["Popular Times"] = {
        #     "Monday": [],
        #     "Tuesday": [],
        #     "Wednesday": [],
        #     "Thursday": [],
        #     "Friday": [],
        #     "Saturday": [],
        #     "Sunday": [],
        # }

    def _driver(self, headless=False) -> webdriver.Chrome:
        logger.info("Creating a new webdriver instance", extra={"headless": headless})
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("headless")
        options.add_argument("window-size=1200x600")
        driver = webdriver.Chrome(options=options)
        logger.info("Webdriver instance created")
        return driver

    def click_open_close_time(self):
        logger.info("Clicking open close time button")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "WVXvdc"))
        )

        element = self.driver.find_element(By.CLASS_NAME, "WVXvdc")
        ActionChains(self.driver).move_to_element(element).click(element).perform()
        logger.info("Open close time button clicked")

    def click_all_reviews_button(self):
        logger.info("Clicking all reviews button")

        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "allxGeDnJMl__button"))
            )

            element = self.driver.find_element_by_class_name("allxGeDnJMl__button")
            element.click()
        except Exception as e:
            logger.info(
                "All reviews button not found", extra={"error": e}, exc_info=True
            )
            self.driver.quit()
            return False
        logger.info("All reviews button clicked")
        return True

    def get_location_data(self):
        logger.info("Getting location data")
        try:
            name = self.driver.find_element(By.CLASS_NAME, "zvLtDc")
            self.location_data["name"] = name.text
        except Exception as e:
            logger.info("Name not found", extra={"error": e}, exc_info=True)
        try:
            avg_rating = self.driver.find_element(By.CLASS_NAME, "fontDisplayLarge")
            self.location_data["rating"] = avg_rating.text
        except Exception as e:
            logger.info("Avg rating not found", extra={"error": e}, exc_info=True)
        try:
            total_reviews = self.driver.find_element(By.CLASS_NAME, "HHrUdb")
            self.location_data["reviews_count"] = total_reviews.text.split()[0]
        except Exception as e:
            logger.info("Total reviews not found", extra={"error": e}, exc_info=True)
        try:
            extra_info = self.driver.find_element(
                By.CSS_SELECTOR, "[aria-label*='Information for']"
            )

        except Exception as e:
            logger.info("Extra info not found", extra={"error": e}, exc_info=True)
            return

        try:
            address = extra_info.find_element(
                By.CSS_SELECTOR, "[data-tooltip='Copy address']"
            )
            self.location_data["location"] = address.get_attribute("aria-label")
        except Exception as e:
            logger.info("Address not found", extra={"error": e}, exc_info=True)

        try:
            phone_number = extra_info.find_element(
                By.CSS_SELECTOR, "[data-tooltip='Copy phone number']"
            )
            self.location_data["contact"] = phone_number.get_attribute("aria-label")
        except Exception as e:
            logger.info("Phone number not found", extra={"error": e}, exc_info=True)

        try:
            website = extra_info.find_element(
                By.CSS_SELECTOR, "[data-tooltip='Open website']"
            )
            self.location_data["website"] = website.get_attribute("href")
        except Exception as e:
            logger.info("Website not found", extra={"error": e}, exc_info=True)

        try:
            booking_link = extra_info.find_element(
                By.CSS_SELECTOR, "[data-tooltip='Open booking link']"
            )
            self.location_data["booking_link"] = booking_link.get_attribute("href")
        except Exception as e:
            logger.info("Booking link not found", extra={"error": e}, exc_info=True)

        logger.info("Location data fetched")

    def get_location_open_close_time(self):

        try:
            location_element = self.driver.find_element(By.CLASS_NAME, "eK4R0e")
        except Exception as e:
            logger.info("Location element not found", extra={"error": e}, exc_info=True)
            return

        try:
            days = location_element.find_elements(By.CLASS_NAME, "ylH6lf")
            times = location_element.find_elements(By.CLASS_NAME, "mxowUb")

            day = [a.text for a in days]
            open_close_time = [
                a.text.replace("\u202f", "").replace("\u2013", " - ") for a in times
            ]

            for i, j in zip(day, open_close_time):
                self.location_data["Time"][i] = j
        except Exception as e:
            logger.info("Open close time not found", extra={"error": e}, exc_info=True)

    def get_companies_from_search(self, search_string, scroll_count=10):
        logger.info("Getting companies from search")
        google_maps_url = (
            "https://www.google.com/maps/search/"
            + urllib.parse.quote_plus(search_string)
            + "?hl=en"
        )
        self.driver.get(google_maps_url)

        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"div[aria-label='Results for {search_string}']")
                )
            )
        except Exception as e:
            logger.info("Search results not found", extra={"error": e}, exc_info=True)
            self.driver.quit()
            return
        div_side_bar = self.driver.find_element(
            By.CSS_SELECTOR, f"div[aria-label='Results for {search_string}']"
        )
        pause_time = 2
        max_count = scroll_count
        x = 0
        logger.info("Scrolling the page")
        while x < max_count:
            try:
                div_side_bar.send_keys(Keys.PAGE_DOWN)
            except Exception as e:
                logger.info("Page not scrolled", extra={"error": e}, exc_info=True)
            time.sleep(pause_time)
            x = x + 1

        logger.info("Page scrolled")

        try:
            companies = self.driver.find_elements(By.CLASS_NAME, "lI9IFe")
        except Exception as e:
            logger.info("Companies not found", extra={"error": e}, exc_info=True)
            self.driver.quit()
            return
        logger.info(f"Found {len(companies)} companies")

        links = []
        for company in companies:
            company_data = {}
            try:
                name = company.find_element(
                    By.CSS_SELECTOR, "div.qBF1Pd.fontHeadlineSmall"
                )
                company_data["name"] = name.text
            except Exception as e:
                logger.info("Company name not found", extra={"error": e}, exc_info=True)
                company_data["name"] = "NA"
            try:
                rating = company.find_element(By.CSS_SELECTOR, "span.MW4etd")
                company_data["rating"] = rating.text
            except Exception as e:
                logger.info(
                    "Company rating not found", extra={"error": e}, exc_info=True
                )
                company_data["rating"] = "NA"
            try:
                reviews = company.find_element(By.CSS_SELECTOR, "span.UY7F9")
                company_data["reviews"] = reviews.text.replace("(", "").replace(")", "")
            except Exception as e:
                logger.info(
                    "Company reviews not found", extra={"error": e}, exc_info=True
                )
                company_data["reviews"] = "NA"
            try:
                phone_number = company.find_element(
                    By.CSS_SELECTOR, "div.W4Efsd:nth-child(2) > span:nth-child(2)"
                )
                company_data["phone_number"] = phone_number.text.split("·")[1].strip()
            except Exception as e:
                try:
                    phone_number = company.find_element(
                        By.CSS_SELECTOR, "div.W4Efsd:nth-child(2) > span:nth-child(1)"
                    )
                    company_data["phone_number"] = phone_number.text.strip()
                except Exception as e:
                    logger.info(
                        "Company phone number not found",
                        extra={"error": e},
                        exc_info=True,
                    )
                    company_data["phone_number"] = "NA"
            try:
                address = company.find_element(
                    By.CSS_SELECTOR, "div.W4Efsd:nth-child(1) > span:nth-child(2)"
                )
                company_data["address"] = address.text.split("·")[1].strip()
            except Exception as e:
                logger.info(
                    "Company address not found", extra={"error": e}, exc_info=True
                )
                company_data["address"] = "NA"
            try:
                website = company.find_element(
                    By.CSS_SELECTOR, "a[data-value='Website']"
                ).get_attribute("href")
                company_data["website"] = website
            except Exception as e:
                logger.info(
                    "Company website not found", extra={"error": e}, exc_info=True
                )
                company_data["website"] = "NA"
            try:
                google_map_link = company.find_element(
                    By.XPATH, f"//a[contains(@aria-label, '{company_data['name']}')]"
                ).get_attribute("href")
                company_data["google_map_link"] = google_map_link
            except Exception as e:
                logger.info(
                    "Company google map link not found",
                    extra={"error": e},
                    exc_info=True,
                )
                company_data["google_map_link"] = "NA"
            links.append(company_data)

        logger.info("Companies data fetched")
        return links

    def get_popular_times(self):
        breakpoint()
        logger.info("Getting popular times")
        try:
            a = self.driver.find_elements_by_class_name("section-popular-times-graph")
            dic = {
                0: "Sunday",
                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
            }
            l = {
                "Sunday": [],
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
            }
            count = 0

            for i in a:
                b = i.find_elements_by_class_name("section-popular-times-bar")
                for j in b:
                    x = j.get_attribute("aria-label")
                    l[dic[count]].append(x)
                count = count + 1

            for i, j in l.items():
                self.location_data["Popular Times"][i] = j
        except:
            pass

    def scroll_the_page(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "section-layout-root"))
            )

            pause_time = 2
            max_count = 10
            x = 0

            while x < max_count:
                scrollable_div = self.driver.find_element_by_css_selector(
                    "div.section-layout.section-scrollbox.scrollable-y.scrollable-show"
                )
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight",
                        scrollable_div,
                    )
                except:
                    pass
                time.sleep(pause_time)
                x = x + 1
        except:
            self.driver.quit()

    def expand_all_reviews(self):
        try:
            element = self.driver.find_elements_by_class_name("section-expand-review")
            for i in element:
                i.click()
        except:
            pass

    def get_reviews_data(self):
        try:
            review_names = self.driver.find_elements_by_class_name(
                "section-review-title"
            )
            review_text = self.driver.find_elements_by_class_name(
                "section-review-review-content"
            )
            review_dates = self.driver.find_elements_by_css_selector(
                "[class='section-review-publish-date']"
            )
            review_stars = self.driver.find_elements_by_css_selector(
                "[class='section-review-stars']"
            )

            review_stars_final = []

            for i in review_stars:
                review_stars_final.append(i.get_attribute("aria-label"))

            review_names_list = [a.text for a in review_names]
            review_text_list = [a.text for a in review_text]
            review_dates_list = [a.text for a in review_dates]
            review_stars_list = [a for a in review_stars_final]

            for a, b, c, d in zip(
                review_names_list,
                review_text_list,
                review_dates_list,
                review_stars_list,
            ):
                self.location_data["Reviews"].append(
                    {"name": a, "review": b, "date": c, "rating": d}
                )

        except Exception as e:
            pass

    def scrape(self, url):
        try:
            self.driver.get(url)
        except Exception as e:
            logger.info("URL not found", extra={"error": e}, exc_info=True)
            self.driver.quit()

        self.click_open_close_time()
        self.get_location_data()
        self.get_location_open_close_time()
        # self.get_popular_times()
        # if self.click_all_reviews_button() == False:
        #     return
        # time.sleep(5)
        # self.scroll_the_page()
        # self.expand_all_reviews()
        # self.get_reviews_data()
        self.driver.quit()

        return self.location_data


if __name__ == "__main__":
    scrapper = WebDriver(headless=False)

    search_string = "travel agencies in kenya"
    scroll_count = 20

    companies_data = scrapper.get_companies_from_search(search_string=search_string, scroll_count=scroll_count)

    current_time = time.strftime("%Y%m%d-%H%M%S")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_dir = os.path.join(
        base_dir, "data", f"{current_time}-{search_string.replace(' ', '_')}.csv"
    )

    if not companies_data:
        logger.info("No companies found")
    else:
        with open(csv_file_dir, "w", newline="") as csvfile:
            fieldnames = companies_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for company in companies_data:
                writer.writerow(company)
        logger.info("Companies data written to csv file")
