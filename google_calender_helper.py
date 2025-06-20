from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import streamlit as st

# Set up credentials from Streamlit secrets
SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=SCOPES
)

# Create Google Calendar API service
service = build("calendar", "v3", credentials=credentials)

# You may need to specify your calendar ID here
# For primary user calendar, use 'primary'
CALENDAR_ID = "primary"

def create_google_calendar_event(summary, description, start_date):
    try:
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_date.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': (start_date + timedelta(hours=1)).isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                    {'method': 'email', 'minutes': 60},
                ],
            },
        }
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return True, event.get("htmlLink")
    except Exception as e:
        return False, str(e)
