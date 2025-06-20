
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# Authentication using Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(credentials)
SHEET_NAME = st.secrets["sheet_name"]
sheet = client.open(SHEET_NAME)

def get_sections():
    return [ws.title for ws in sheet.worksheets()]

def get_fields_for_section(section):
    try:
        ws = sheet.worksheet(section)
        return ws.row_values(1)  # Ignore first column (timestamp or ID)
    except:
        return []

# def add_entry(section, data_dict):
#     ws = sheet.worksheet(section)
#     values = [data_dict.get(field, "") for field in get_fields_for_section(section)]
#     ws.append_row([""] + values)

def add_entry(section_name, entry_data):
    worksheet = sheet.worksheet(section_name)
    headers = worksheet.row_values(1)

    # Ensure correct order: use headers from sheet, not from entry_data.keys()
    new_row = [entry_data.get(header, "") for header in headers]

    worksheet.append_row(new_row)
    
def get_entries_for_section(section_name):
    worksheet = sheet.worksheet(section_name)
    return worksheet.get_all_records()
