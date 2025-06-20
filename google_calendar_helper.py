from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Google Calendar API Setup
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "service_account.json"  # Ensure this file is in your root directory

def create_google_calendar_event(title, start_datetime, duration_minutes=60):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": title,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": (start_datetime + timedelta(minutes=duration_minutes)).isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event.get("htmlLink")
