import os
import re
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
import traceback
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from dotenv import load_dotenv  # Add this import for .env file support
from datetime import datetime, timedelta


# Load environment variables from .env file
load_dotenv()

# Get LinkedIn credentials from environment variables
LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
]


def convert_relative_date(relative_date_text):
    """
    Convert LinkedIn's relative date text (e.g., '1 week ago', '2 days ago')
    to an actual calendar date.
    """
    today = datetime.now()
    relative_date_text = relative_date_text.lower().strip()

    # Handle different time periods
    if "just now" in relative_date_text or "moments ago" in relative_date_text:
        return today.strftime("%Y-%m-%d")

    if "hour" in relative_date_text:
        hours = int(relative_date_text.split()[0])
        post_date = today - timedelta(hours=hours)
        return post_date.strftime("%Y-%m-%d")

    if "day" in relative_date_text:
        days = int(relative_date_text.split()[0])
        post_date = today - timedelta(days=days)
        return post_date.strftime("%Y-%m-%d")

    if "week" in relative_date_text:
        weeks = int(relative_date_text.split()[0])
        post_date = today - timedelta(weeks=weeks)
        return post_date.strftime("%Y-%m-%d")

    if "month" in relative_date_text:
        # Approximate a month as 30 days
        months = int(relative_date_text.split()[0])
        post_date = today - timedelta(days=30 * months)
        return post_date.strftime("%Y-%m-%d")

    if "year" in relative_date_text:
        years = int(relative_date_text.split()[0])
        post_date = today - timedelta(days=365 * years)
        return post_date.strftime("%Y-%m-%d")

    # If we couldn't parse it, return the original text
    return relative_date_text

def human_like_delay():
    """Add a random human-like delay between actions."""
    time.sleep(random.uniform(3, 7))


def longer_delay():
    """Add a longer delay between page navigations."""
    time.sleep(random.uniform(15, 30))


def scroll_like_human(driver):
    """Simulate human-like scrolling behavior."""
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    current_position = 0
    while current_position < total_height:
        scroll_amount = random.randint(100, viewport_height - 200)
        current_position += scroll_amount
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.2:
            time.sleep(random.uniform(0.5, 1))


def dismiss_modals(driver):
    """
    Look for and dismiss various LinkedIn modals that might appear.
    """
    modal_selectors = [
        "button.artdeco-modal__dismiss",
        "button.modal__dismiss",
        "button.contextual-sign-in-modal__modal-dismiss",
        "button[aria-label='Dismiss']",
        "button.sign-in-modal__dismiss-btn",
        "button.alert-dismiss",
        "button:has(> icon.contextual-sign-in-modal__modal-dismiss-icon)",
        "button.artdeco-button.artdeco-button--muted"
    ]

    for selector in modal_selectors:
        try:
            dismiss_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"Found modal dismiss button with selector: {selector}")
            dismiss_button.click()
            print("Modal dismissed")
            time.sleep(1)
            return True
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException):
            continue

    try:
        dismiss_icon = driver.find_element(By.XPATH, "//button[@data-test-modal-close-btn]")
        dismiss_icon.click()
        print("Modal dismissed via close button")
        return True
    except (NoSuchElementException, ElementNotInteractableException):
        pass

    print("No dismissable modals found or unable to dismiss")
    return False


def open_url_with_captcha(driver, url, retries=4):
    """
    Use SeleniumBase's methods to open a URL with reconnect and
    try clicking Cloudflare captcha if detected.
    """
    try:
        driver.uc_open_with_reconnect(url, retries)
        page_source = driver.get_page_source()
        if "Additional Verification Required" in page_source or "Just a moment" in page_source:
            print("Cloudflare CAPTCHA detected, attempting to click it...")
            driver.uc_gui_click_captcha()
            time.sleep(10)
            driver.uc_gui_click_captcha()
        return True
    except Exception:
        traceback.print_exc()
        return False


def get_driver():
    """Initialize driver with proper anti-detection settings."""
    return Driver(
        uc=True,
        headless=False,  # Change to True for headless operation if needed.
        incognito=True,
        disable_gpu=True,
        no_sandbox=True,
        page_load_strategy='eager',
        agent=random.choice(USER_AGENTS)
    )


def login_to_linkedin(driver):
    """
    Log in to LinkedIn with credentials from environment variables.
    Returns True if login successful, False otherwise.
    """
    # Check if we have credentials available
    if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
        print("LinkedIn credentials not found in environment variables")
        return False

    try:
        # Navigate to the LinkedIn login page
        print("Navigating to LinkedIn login page")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)

        # Enter username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.clear()
        username_field.send_keys(LINKEDIN_USERNAME)
        print("Username entered")

        # Enter password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        password_field.clear()
        password_field.send_keys(LINKEDIN_PASSWORD)
        print("Password entered")

        # Click login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_button.click()
        print("Login button clicked")

        # Wait for successful login (check for feed or home page)
        success_indicators = [
            "div.feed-identity-module",
            "div.feed-container",
            "aside.scaffold-layout__aside",
            "nav.global-nav"
        ]

        login_successful = False
        for selector in success_indicators:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                login_successful = True
                break
            except TimeoutException:
                continue

        if login_successful:
            print("Successfully logged in to LinkedIn")
            return True
        else:
            # Check for verification challenges
            if "security verification" in driver.page_source.lower() or "verify" in driver.page_source.lower():
                print("LinkedIn is requesting additional verification")
                print("Please complete the verification manually in the browser window")
                # Wait for manual verification (up to 2 minutes)
                time.sleep(120)
                return True
            else:
                print("Login unsuccessful")
                return False

    except Exception as e:
        print(f"Error during LinkedIn login: {e}")
        traceback.print_exc()
        return False

def handle_login_wall(driver):
    """Handle LinkedIn login wall by actually logging in."""
    login_wall_detected = check_for_login_wall(driver)

    if login_wall_detected:
        print("Login wall detected, attempting to log in")
        current_url = driver.current_url
        login_success = login_to_linkedin(driver)

        if login_success:
            # Navigate back to the original URL if needed
            if "linkedin.com/login" in driver.current_url:
                print(f"Navigating back to: {current_url}")
                driver.get(current_url)
                time.sleep(5)
            return True
        else:
            print("Failed to log in to LinkedIn")
            return False

    return True  # No login wall detected


def wait_for_job_results(driver, timeout=30):
    """
    Try multiple CSS selectors for job results list until one is found.
    Returns True if any selector is found, False otherwise.
    """
    selectors = [
        "ul.jobs-search-results__list",
        "div.jobs-search-results-list",
        "div.jobs-search__results-list",
        "section.two-pane-serp-page__results-list",
        "div.scaffold-layout__list",
        "div.jobs-search-two-pane__wrapper"
    ]

    for selector in selectors:
        try:
            WebDriverWait(driver, timeout // len(selectors)).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print(f"Job results loaded with selector: {selector}")
            return True
        except TimeoutException:
            print(f"Selector '{selector}' not found, trying next...")

    # If we've reached here, try looking for any job card element
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "li.jobs-search-results__list-item, div.job-card-container"))
        )
        print("Found job cards directly")
        return True
    except TimeoutException:
        print("No job results found with any selector")
        return False


def wait_for_job_details(driver, timeout=15):
    """
    Try multiple CSS selectors until one of them indicates that the job details
    have loaded. Returns True if found, False otherwise.
    """
    selectors = [
        "div.jobs-details__main-content",
        "div.job-details__content",
        "div.jobs-description",
        "div.jobs-description-content",
        "section.core-section-container"
    ]

    for selector in selectors:
        try:
            WebDriverWait(driver, timeout // len(selectors)).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print(f"Job details loaded with selector: {selector}")
            return True
        except TimeoutException:
            continue

    print("Job details did not load with any of the selectors")
    return False


def check_for_login_wall(driver):
    """Check if LinkedIn is showing a sign-in wall."""
    login_indicators = [
        "//h1[contains(text(), 'Sign in to continue')]",
        "//p[contains(text(), 'See who you already know at')]",
        "//button[contains(text(), 'Sign in')]",
        "//h2[contains(text(), 'Join your colleagues, classmates, and friends')]",
        "//p[contains(text(), 'Log in to continue')]",
        "//h1[contains(text(), 'Log in to LinkedIn')]"
    ]

    for xpath in login_indicators:
        try:
            if driver.find_element(By.XPATH, xpath):
                print("Login wall detected")
                return True
        except NoSuchElementException:
            continue

    return False


def extract_job_card_info(driver, job_cards, df):
    """Extract job information from job cards."""
    original_window = driver.current_window_handle  # Store the handle to the search results window

    for index, card in enumerate(job_cards[:min(len(job_cards), 10)]):  # Limit to 10 jobs for testing
        try:
            print(f"Processing job card {index + 1}/{min(len(job_cards), 10)}")

            # Enhanced link finding to handle more HTML structures
            job_link = None

            # Try multiple approaches to find the job link
            # First try the base-card__full-link approach
            try:
                job_link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                job_link = job_link_elem.get_attribute("href")
                print(f"Found job detail link with base-card__full-link: {job_link}")
            except NoSuchElementException:
                pass

            # Try job-card-container__link approach (from your example HTML)
            if not job_link:
                try:
                    job_link_elem = card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                    job_link = job_link_elem.get_attribute("href")
                    print(f"Found job detail link with job-card-container__link: {job_link}")
                except NoSuchElementException:
                    pass

            # Try finding any anchor tag with href containing "jobs/view"
            if not job_link:
                try:
                    job_link_elem = card.find_element(By.XPATH, ".//a[contains(@href, '/jobs/view/')]")
                    job_link = job_link_elem.get_attribute("href")
                    print(f"Found job detail link with xpath '/jobs/view/': {job_link}")
                except NoSuchElementException:
                    pass

            # Fall back to other selectors only if the preferred ones aren't found
            if not job_link:
                link_selectors = [
                    "a.job-card-list__title",
                    "h3.base-search-card__title a",
                    "a[data-tracking-control-name='public_jobs_jserp-result_search-card']",
                    "a[aria-label]"  # Try any anchor with aria-label which might contain job titles
                ]

                for selector in link_selectors:
                    try:
                        job_link_elem = card.find_element(By.CSS_SELECTOR, selector)
                        job_link = job_link_elem.get_attribute("href")
                        if job_link:
                            print(f"Found job link with alternate selector: {job_link}")
                            break
                    except NoSuchElementException:
                        continue

            if not job_link:
                print(f"Could not find job link for card {index + 1}, skipping")
                continue

            print(f"Opening job link: {job_link}")

            # Open the job link in a new tab
            driver.execute_script("window.open(arguments[0]);", job_link)
            time.sleep(3)  # Allow time for the new tab to open

            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])

            # Check if we hit a login wall on the job details page and handle it
            if check_for_login_wall(driver):
                print("Encountered login wall on job details page")
                if not handle_login_wall(driver):
                    # Close current tab and return to search page if login failed
                    driver.close()
                    driver.switch_to.window(original_window)  # Use the stored handle
                    continue

            # Wait for job details to load
            if not wait_for_job_details(driver):
                print("Job details didn't load, skipping this job")
                driver.close()
                driver.switch_to.window(original_window)  # Use the stored handle
                continue

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract job information using multiple possible selectors
            title_selectors = ["h1.topcard__title", "h1.job-details-top-card__job-title",
                               "h1.t-24", "h1.job-title"]

            # Get job title
            job_title_text = "Unknown Title"
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    job_title_text = title_elem.get_text(strip=True)
                    break

            company_text = "Unknown Company"
            company_container_selectors = [
                "div.job-details-jobs-unified-top-card__company-name",
                "span.job-details-top-card__company-name",
                "a.topcard__org-name-link",
                "span.jobs-unified-top-card__company-name"
            ]

            for container_selector in company_container_selectors:
                company_container = soup.select_one(container_selector)
                if company_container:
                    # First, try to find a link inside the container
                    company_link = company_container.find('a')
                    if company_link:
                        company_text = company_link.get_text(strip=True)
                    else:
                        # If no link, get the text directly from the container
                        # This handles the case where the company name is plain text
                        company_text = company_container.get_text(strip=True)
                    break

            # Get location
            location_text = "Unknown Location"
            try:
                # First try the specific container from your example
                primary_container = soup.select_one(
                    "div.job-details-jobs-unified-top-card__primary-description-container")
                if primary_container:
                    # Find all spans with the specific class
                    low_emphasis_spans = primary_container.select("span.tvm__text.tvm__text--low-emphasis")
                    if low_emphasis_spans:
                        # The first span usually contains the location
                        location_text = low_emphasis_spans[0].get_text(strip=True)

                # If location is still unknown, try other selectors as fallback
                if location_text == "Unknown Location":
                    fallback_selectors = [
                        "span.topcard__flavor--bullet",
                        "span.job-details-top-card__job-criteria-text--location",
                        "span.jobs-unified-top-card__bullet",
                        "span.jobs-unified-top-card__location"
                    ]

                    for selector in fallback_selectors:
                        location_elem = soup.select_one(selector)
                        if location_elem:
                            location_text = location_elem.get_text(strip=True)
                            break

            except Exception as e:
                print(f"Error extracting location: {e}")

            relative_date_text = "Unknown Date"
            try:
                # Look in the primary container
                primary_container = soup.select_one(
                    "div.job-details-jobs-unified-top-card__primary-description-container")
                if primary_container:
                    # Get all spans with the low emphasis class
                    low_emphasis_spans = primary_container.select("span.tvm__text.tvm__text--low-emphasis")

                    # Specifically use the second span as you suggested
                    if len(low_emphasis_spans) > 1:
                        relative_date_text = low_emphasis_spans[1].get_text(strip=True)

                        # Clean up the text to remove any dots or other separators
                        relative_date_text = relative_date_text.replace("·", "").strip()

                        # Convert to an actual calendar date
                        calendar_date = convert_relative_date(relative_date_text)

                # If still unknown, try the fallback selectors
                if relative_date_text == "Unknown Date":
                    calendar_date = "Unknown Date"
                    pass

            except Exception as e:
                print(f"Error extracting posted date: {e}")
                calendar_date = "Unknown Date"

            # Try to find employment type
            employment_type = "Not listed"
            employment_selectors = [
                "span.jobs-unified-top-card__job-insight:contains('Employment type')",
                "li.jobs-unified-top-card__job-insight:contains('Employment type')",
                "span.description__job-criteria-text:contains('Employment type')"
            ]
            for selector in employment_selectors:
                try:
                    emp_elem = soup.select_one(selector)
                    if emp_elem:
                        employment_type = emp_elem.get_text(strip=True).replace("Employment type", "").strip()
                        break
                except:
                    pass

            hourly_pay = "Not listed"
            try:
                # First try to extract from job detail page
                salary_pattern = re.compile(r'\$\d+(?:\.\d+)?(?:/hr)?')
                salary_match = salary_pattern.search(str(soup))
                if salary_match:
                    hourly_pay = salary_match.group(0)

                # If not found, check if we can extract from the original card
                if hourly_pay == "Not listed":
                    # Extract the text content from the card
                    card_html = card.get_attribute('outerHTML')
                    card_soup = BeautifulSoup(card_html, 'html.parser')
                    # Try to find salary text in the card
                    # Look for salary in the HTML we got from the example
                    salary_container = card_soup.select_one("div.mt1.t-sans.t-12 li")
                    if salary_container:
                        salary_text = salary_container.get_text(strip=True)
                        if '$' in salary_text:
                            hourly_pay = salary_text
            except Exception as e:
                print(f"Error extracting salary with regex: {e}")

            # For fields that LinkedIn might not provide, assign placeholders
            work_days = "Not listed"
            hours_per_week = "Not listed"

            # Build a dictionary for this job
            job_data = {
                'Link': job_link,
                'Job Title': job_title_text,
                'Company': company_text,
                'Posted Date': calendar_date,
                'Location': location_text,
                'Hourly Pay': hourly_pay,
                'Employment Type': employment_type,
                'Work Days': work_days,
                'Hours per Week': hours_per_week
            }

            print(f"Extracted job data: {job_title_text} at {company_text}")

            # Append the job data to the DataFrame
            df = pd.concat([df, pd.DataFrame([job_data])], ignore_index=True)

        except Exception as e:
            print(f"Error processing job card {index}: {e}")
            traceback.print_exc()

        finally:
            # Close the job detail tab if it's open and switch back to the search tab
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(original_window)  # Always return to the original window

            # Add a delay between job cards to avoid rate limiting
            time.sleep(random.uniform(2, 5))

    return df

def go_to_page(driver, page_number):
    """
    Navigate to a given page number in LinkedIn job search results
    by clicking the pagination button with data-test-pagination-page-btn equal to the page number.
    """
    try:
        # Build a CSS selector that targets the button inside the <li> with the correct data attribute
        selector = f"li[data-test-pagination-page-btn='{page_number}'] button"
        print(f"Looking for pagination button with selector: {selector}")
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        button.click()
        print(f"Navigated to page {page_number}")
        # Wait for the new page to load the results
        time.sleep(5)
        return True
    except Exception as e:
        print(f"Error navigating to page {page_number}: {e}")
        return False

def scrape_linkedin_job_data(driver, job_title, job_location):
    """
    Scrape LinkedIn job data with pagination.
    """
    # Create an empty DataFrame to hold the job data
    df = pd.DataFrame(columns=[
        'Link', 'Job Title', 'Company', 'Posted Date', 'Location',
        'Hourly Pay', 'Employment Type', 'Work Days', 'Hours per Week'
    ])

    # Ensure we're logged in first
    print("Checking login status before starting scraping")
    logged_in = login_to_linkedin(driver)
    if not logged_in:
        print("WARNING: Not logged in to LinkedIn. Some job details may be inaccessible.")

    # Construct the LinkedIn job search URL and load the page
    base_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={job_location}"
    print(f"Navigating to: {base_url}")
    driver.get(base_url)
    time.sleep(5)  # Allow page time to load

    dismiss_modals(driver)
    handle_login_wall(driver)

    current_page = 1
    while True:
        print(f"Processing page {current_page}")

        # Wait for job results to load
        if not wait_for_job_results(driver, timeout=30):
            print("Could not load job results on this page")
            break

        # Get job cards on the current page (using your existing selectors)
        job_cards = []
        card_selectors = [
            "li.jobs-search-results__list-item",
            "div.job-card-container",
            "div.job-card-list",
            "div.job-search-card"
        ]
        for selector in card_selectors:
            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    print(f"Found {len(job_cards)} job cards with selector: {selector}")
                    break
            except Exception:
                continue

        if not job_cards:
            print("No job cards found. Ending pagination.")
            break

        # Process job cards and extract job info (using your extract_job_card_info function)
        df = extract_job_card_info(driver, job_cards, df)

        # Attempt to go to the next page
        next_page = current_page + 1
        if not go_to_page(driver, next_page):
            print("No more pages found. Ending pagination.")
            break

        current_page = next_page
        time.sleep(5)  # Allow page time to load before proccoessing next page

    return df