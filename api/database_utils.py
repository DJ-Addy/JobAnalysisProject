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
CLIENT_SECRET = 'aqueous-botany-455604-q6-ec918345f930.json'
def upload_csv_to_drive(csv_path, drive_filename):
    creds =ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET,SCOPES)
    client=gspread.authorize(creds)
    sheet=client.open(drive_filename).sheet1
    df=pd.read_csv(csv_path)

    sheet.update([df.columns.values.tolist()]+df.values.tolist())

