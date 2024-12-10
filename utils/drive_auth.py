"""This script provides Google Drive API service."""

import pydata_google_auth
from googleapiclient.discovery import build

# Authenticate and build the Drive API client
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def initialize_drive_service():
    """Initialize the Google Drive service."""
    creds = pydata_google_auth.get_user_credentials(
        SCOPES,
        auth_local_webserver=True,
    )
    return build("drive", "v3", credentials=creds)


def initialize_sheets_service():
    """Initialize the Google Sheets service."""
    creds = pydata_google_auth.get_user_credentials(
        SCOPES,
        auth_local_webserver=True,
    )
    return build("sheets", "v4", credentials=creds)
