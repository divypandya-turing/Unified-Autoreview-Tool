"""This script provides Google Drive API service."""

import pydata_google_auth
from googleapiclient.discovery import build

# Authenticate and build the Drive API client
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

CREDS = pydata_google_auth.get_user_credentials(
    SCOPES,
    auth_local_webserver=True,
)

# Build the Drive API service
DRIVE_SERVICE = build("drive", "v3", credentials=CREDS)
SHEETS_SERVICE = build("sheets", "v4", credentials=CREDS)
