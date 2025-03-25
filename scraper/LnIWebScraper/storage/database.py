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



def upload_csv_to_drive(csv_path, drive_filename):
    creds = None

    # Load existing credentials if they exist
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Authenticate and refresh if necessary
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    # Build the Drive API client
    drive_service = build('drive', 'v3', credentials=creds)

    # Upload the file
    file_metadata = {'name': drive_filename}
    media = MediaFileUpload(csv_path, mimetype='text/csv')
    response = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"Successfully uploaded '{drive_filename}' to Google Drive (File ID: {response.get('id')})")

