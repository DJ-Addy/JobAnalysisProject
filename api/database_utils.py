

import os
import pandas as pd
import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.json'
CLIENT_SECRET =r"C:\Users\Adam\Desktop\JobAnalysisProject\nextjs-fastapi\api\aqueous-botany-455604-q6-ec918345f930.json"
def upload_csv_to_drive(csv_path, drive_filename):
    print("DEBUG: csv_path =", csv_path)
    print("DEBUG: drive_filename =", drive_filename)
    print("DEBUG: CLIENT_SECRET =", CLIENT_SECRET)
    # Now load creds:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET, SCOPES)
    client = gspread.authorize(creds)
    print("DEBUG: credentials loaded successfully")

    sheet = client.open(drive_filename).sheet1
    print("DEBUG: opened sheet:", drive_filename)

    df = pd.read_csv(csv_path)
    print("DEBUG: read CSV, shape =", df.shape)

    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("DEBUG: sheet updated!")