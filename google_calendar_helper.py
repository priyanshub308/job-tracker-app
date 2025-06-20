import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Replace with your personal calendar ID (email)
CALENDAR_ID = "priyanshudbzmpr@gmail.com"

def create_google_calendar_event(title, start_time):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": title,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {
            "dateTime": (start_time + timedelta(hours=1)).isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    try:
        event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return event_result.get("htmlLink")
    except Exception as e:
        st.error(f"❌ Failed to create calendar event: {e}")
        return None
