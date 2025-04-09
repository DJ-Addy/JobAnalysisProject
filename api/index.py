import traceback

from fastapi import FastAPI, Request
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse
from pydantic import BaseModel
import os
import pandas as pd
import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from .database_utils import upload_csv_to_drive


SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.json'
CLIENT_SECRET =r"C:\Users\Adam\Desktop\JobAnalysisProject\nextjs-fastapi\api\aqueous-botany-455604-q6-ec918345f930.json"

print("DEBUG: This is the code that should run!")

### Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")


@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}


class UploadRequest(BaseModel):
    csv_path: str
    drive_filename: str


@app.post("/upload-csv")
def upload_csv_to_drive_api(request: UploadRequest):
    csv_path = request.csv_path
    drive_filename = request.drive_filename

    # No try/except for the moment, so we can see the full traceback in the console:
    if not os.path.exists(csv_path):
        return {"status": "error", "message": f"File not found: {csv_path}"}

    upload_csv_to_drive(csv_path, drive_filename)
    return {"status": "success", "message": "Uploaded successfully!"}



