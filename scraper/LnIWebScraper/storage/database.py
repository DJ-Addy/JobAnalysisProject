import csv
import os

import pandas as pd
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_PATH = 'token.json'
CLIENT_SECRET = 'client_secret_151474916753-lfmqqlgr78kdnn4vp912iivh58p6rt67.apps.googleusercontent.com.json'

def save_to_csv(df, output_path):
    """Save the job data to a CSV file at the specified path."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if os.path.exists(output_path):
            try:
                existing_df = pd.read_csv(output_path)
                if existing_df.empty:
                    combined_df = df
                else:
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                    combined_df = combined_df.drop_duplicates(subset=['Job Title', 'Company'], keep='first')
                combined_df.to_csv(output_path, index=False)
                print(f"Successfully appended {len(df)} jobs. Total records: {len(combined_df)}")
            except Exception as e:
                print(f"Error appending to existing file: {e}")
                print("Creating new file instead.")
                df.to_csv(output_path, index=False)
                print(f"Successfully saved {len(df)} jobs to new file.")
        else:
            df.to_csv(output_path, index=False)
            print(f"Successfully saved {len(df)} jobs to new file.")
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        fallback_path = "jobs_fallback.csv"
        try:
            df.to_csv(fallback_path, index=False)
            print(f"Saved to fallback location: {fallback_path}")
        except:
            print("Failed to save even to fallback location.")
        return False



