from fastapi import FastAPI, Request
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse
from pydantic import BaseModel
import os

from scraper.LnIWebScraper.storage.database import upload_csv_to_drive

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

    # Call your existing function
    if os.path.exists(csv_path):
        upload_csv_to_drive(csv_path, drive_filename)
        return {"status": "success", "message": f"Uploaded {csv_path} to Drive as '{drive_filename}'"}
    else:
        return {"status": "error", "message": f"CSV file not found at: {csv_path}"}



