# This is a sample Python script.
import traceback

import schedule

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from scrapper.indeed_scraper import search_jobs, scrape_job_data, COUNTRY_URLS, get_driver
from scrapper.linkedin_scraper import scrape_linkedin_job_data
from storage.database import save_to_csv, upload_csv_to_drive
from seleniumbase import Driver
from dotenv import load_dotenv
import os
import requests


API_ENDPOINT = "http://127.0.0.1:8000/upload-csv"

def trigger_csv_upload():
    data = {
        "csv_path": "storage/jobs.csv",
        "drive_filename": "linkedin_jobs_indeed_jobs_union_for_janitor_il.csv"
    }
    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Failed to upload CSV. Status code: {response.status_code}")

def main():
        '''
        try:
            driver = get_driver()  # Use our custom driver setup
            country_url = COUNTRY_URLS['united_states']
            job_position = "janitor"
            job_location = "Illinois"
            date_posted = 20

            # First connection attempt with recovery
            search_url, total_jobs = search_jobs(driver, country_url, job_position, job_location, date_posted)
            if "Unknown" in total_jobs:
                print("Initial search failed, restarting driver...")
                driver.quit()
                driver = get_driver()
                search_url, total_jobs = search_jobs(driver, country_url, job_position, job_location, date_posted)

            df = scrape_job_data(driver, country_url, job_position, job_location, date_posted, total_jobs)

            if not df.empty:
                save_to_csv(df, "storage/jobs.csv")
            else:
                print("No jobs scraped.")

        except Exception as e:
            print(f"Critical error: {str(e)}")
            traceback.print_exc()
        finally:
            if driver:
                driver.quit()

        try:

            # Get credentials from command line if not in environment
            if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
                LINKEDIN_USERNAME = input("Enter your LinkedIn username: ")
                LINKEDIN_PASSWORD = input("Enter your LinkedIn password: ")

            # Initialize the driver
            driver = get_driver()

            # Define the job search parameters
            job_title = "Janitor"
            job_location = "Illinois"

            # Scrape job data
            job_data = scrape_linkedin_job_data(driver, job_title, job_location)

            # Save to CSV
            save_to_csv(job_data,"storage/jobs.csv")
            print(f"Job data saved to storage/jobs.csv")

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()

        finally:
            # Close the driver
            if 'driver' in locals():
                driver.quit()
        '''
        #"""
        '''
        driver = None
        try:
            # Load environment variables
            load_dotenv()

            # Get LinkedIn credentials
            LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
            LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

            # Get credentials from command line if not in environment
            if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
                LINKEDIN_USERNAME = input("Enter your LinkedIn username: ")
                LINKEDIN_PASSWORD = input("Enter your LinkedIn password: ")

            # Job search parameters
            job_position = "janitor"
            job_location = "Illinois"
            date_posted = 20  # for Indeed
            country_url = COUNTRY_URLS['united_states'] #for indeed

            # Initialize the driver
            driver = get_driver()

            # Scrape Indeed
            search_url, total_jobs = search_jobs(driver, country_url, job_position, job_location, date_posted)
            if "Unknown" in total_jobs:
                print("Initial search failed, restarting driver...")
                driver.quit()
                driver = get_driver()
                search_url, total_jobs = search_jobs(driver, country_url, job_position, job_location, date_posted)

            indeed_jobs = scrape_job_data(driver, country_url, job_position, job_location, date_posted, total_jobs)
            
            if not indeed_jobs.empty:
                save_to_csv(indeed_jobs, "storage/jobs.csv")
            else:
                print("No jobs scraped.")
            # Restart driver before LinkedIn to avoid session issues
            driver.quit()

            driver = get_driver()

            # Scrape LinkedIn
            linkedin_jobs = scrape_linkedin_job_data(driver, job_position, job_location)

            # Combine results
            save_to_csv(linkedin_jobs, "storage/jobs.csv")

            print(f"Job data saved to storage/jobs.csv")
            upload_csv_to_drive("storage/jobs.csv", 'linkedin_jobs_indeed_jobs_union_for_janitor_il.csv')
            print(f"Job data uploaded from storage/jobs.csv to drive")

        except Exception as e:
            print(f"An error occurred: {e}")
            if not indeed_jobs.empty:
                print("Saving Indeed jobs collected so far...")
                save_to_csv(indeed_jobs, "storage/jobs.csv")
            if not linkedin_jobs.empty:
                print("Saving LinkedIn jobs collected so far...")
                save_to_csv(linkedin_jobs, "storage/jobs.csv")
            traceback.print_exc()
            traceback.print_exc()


        finally:
            # Close the driver
            if 'driver' in locals():
                driver.quit()
        '''
        trigger_csv_upload()



if __name__ == "__main__":
    schedule.every().day.at("10:30").do(main())
#uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
