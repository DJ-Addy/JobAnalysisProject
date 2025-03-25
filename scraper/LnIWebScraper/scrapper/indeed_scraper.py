import os
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver  # SeleniumBase's Driver with undetected-chromedriver support
import traceback

from seleniumbase.common.exceptions import TimeoutException

# Define country URLs
COUNTRY_URLS = {
    'nigeria': 'https://ng.indeed.com',
    'united_kingdom': 'https://uk.indeed.com',
    'united_states': 'https://www.indeed.com',
    'canada': 'https://ca.indeed.com',
    'germany': 'https://de.indeed.com',
    'australia': 'https://au.indeed.com',
    'india': 'https://www.indeed.co.in',
    # Add other countries as needed
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
]


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


def search_jobs(driver, country_url, job_position, job_location, date_posted):
    """Navigate to Indeed and search for jobs using our captcha-handling helper."""
    formatted_job = "+".join(job_position.split())
    base_url = f"{country_url}/jobs?q={formatted_job}&l={job_location}&fromage={date_posted}"
    print(f"Navigating to: {base_url}")
    human_like_delay()
    if not open_url_with_captcha(driver, base_url, retries=4):
        print("Failed to open search URL with captcha handling.")
        return base_url, "Unknown"
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobsearch-ResultsList")))
        scroll_like_human(driver)
        try:
            job_count_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "jobsearch-JobCountAndSortPane-jobCount")]')))
            total_jobs = job_count_element.text.strip()
            print(f"Found {total_jobs}")
        except Exception:
            print("Couldn't find job count element")
            total_jobs = "Unknown"
        driver.save_screenshot('search_page.png')
        return base_url, total_jobs
    except Exception as e:
        print(f"Error during search: {e}")
        driver.save_screenshot('error_page.png')
        return base_url, "Unknown"


def get_driver():
    """Initialize driver with proper anti-detection settings"""
    return Driver(
        uc=True,
        headless=False,  # Start with visible browser for debugging
        incognito=True,
        disable_gpu=True,
        no_sandbox=True,
        page_load_strategy='eager',
        agent=random.choice(USER_AGENTS)
    )


def scrape_job_data(driver, country_url, job_position, job_location, date_posted, total_jobs):
    formatted_job = "+".join(job_position.split())
    base_url = f"{country_url}/jobs?q={formatted_job}&l={job_location}&fromage={date_posted}"
    df = pd.DataFrame(columns=['Link', 'Job Title', 'Company', 'Posted Date', 'Location',
                               'Hourly Pay', 'Employment Type', 'Work Days', 'Hours per Week'])
    MAX_PAGES = 5
    MAX_RETRIES = 2
    page_num = 1

    while page_num <= MAX_PAGES:
        for attempt in range(MAX_RETRIES):
            try:
                start = (page_num - 1) * 10
                current_url = f"{base_url}&start={start}" if page_num > 1 else base_url

                print(f"Processing page {page_num}: {current_url}")
                if not open_url_with_captcha(driver, current_url):
                    raise Exception("Failed to open URL")

                # Check for security blocks
                if any(text in driver.page_source for text in ["unusual traffic", "security check"]):
                    raise Exception("Security verification detected")

                # Wait for jobs to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon")))
                break

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    print("Max retries reached")
                    return df
                driver.refresh()
                time.sleep(10)

        # Process page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='job_seen_beacon')

        if not job_cards:
            print("No more jobs found")
            break

        for card in job_cards:
            job_data = extract_job_data(card, country_url)
            if job_data:
                df = pd.concat([df, pd.DataFrame([job_data])], ignore_index=True)

        page_num += 1
        longer_delay()  # 15-30s delay between pages

    return df


def extract_job_data(job_card, country_url):
    """Extract job data from a job card element, including meta information."""
    try:
        job_title_element = job_card.find('a', class_=lambda x: x and 'JobTitle' in x) or \
                            job_card.find('h2', class_=lambda x: x and 'jobTitle' in str(x).lower()) or \
                            job_card.find('span', id=lambda x: x and 'jobTitle-' in str(x))
        job_title = job_title_element.text.strip() if job_title_element else "Unknown Title"
        link_element = job_card.find('a', {'data-jk': True}) or \
                       job_card.find('a', class_=lambda x: x and 'JobTitle' in x)
        if link_element and link_element.get('href'):
            link = link_element.get('href')
            if not link.startswith('http'):
                link = country_url + link
        else:
            link = "No link found"
        company_element = job_card.find('span', {'data-testid': 'company-name'}) or \
                          job_card.find('span', class_=lambda x: x and 'company' in str(x).lower())
        company = company_element.text.strip() if company_element else "Unknown Company"
        date_element = job_card.find('span', class_='date') or \
                       job_card.find('span', {'data-testid': 'myJobsStateDate'})
        posted_date = date_element.text.strip() if date_element else "Unknown Date"
        location_element = job_card.find('div', {'data-testid': 'text-location'}) or \
                           job_card.find('div', class_=lambda x: x and 'location' in str(x).lower())
        if location_element:
            try:
                location = location_element.find('span').text.strip()
            except (AttributeError, TypeError):
                location = location_element.text.strip()
        else:
            location = "Unknown Location"
        # Extract metadata from the job meta data group
        hourly_pay = "Not listed"
        employment_type = "Not listed"
        work_days = "Not listed"
        hours_per_week = "Not listed"
        meta_group = job_card.find("div", class_=lambda x: x and "jobMetaDataGroup" in x)
        if meta_group:
            meta_items = meta_group.find_all("div", attrs={"data-testid": "attribute_snippet_testid"})
            meta_texts = [item.get_text(strip=True) for item in meta_items]
            if len(meta_texts) > 0:
                hourly_pay = meta_texts[0]
            if len(meta_texts) > 1:
                employment_type = meta_texts[1]
            if len(meta_texts) > 2:
                work_days = meta_texts[2]
            if len(meta_texts) > 3:
                hours_per_week = meta_texts[3]
        return {
            'Link': link,
            'Job Title': job_title,
            'Company': company,
            'Posted Date': posted_date,
            'Location': location,
            'Hourly Pay': hourly_pay,
            'Employment Type': employment_type,
            'Work Days': work_days,
            'Hours per Week': hours_per_week
        }
    except Exception as e:
        print(f"Error extracting job data: {e}")
        return None