
import streamlit as st
from google_sheets_helper import get_sections, add_entry, get_fields_for_section
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Smart Job & Task Tracker", layout="wide")
st.title("📋 Smart Job & Task Tracker")

# Choose section or create a new one
sections = get_sections()
section = st.selectbox("Select or create a section", options=sections + ["➕ Create New"], index=0)

if section == "➕ Create New":
    section = st.text_input("Enter new section name")
    if section:
        st.success(f"New section '{section}' will be used.")

# Get fields for the selected section
fields = get_fields_for_section(section)

if fields:
    st.subheader(f"Add entry to '{section}'")
    entry_data = {}
    for field in fields:
        entry_data[field] = st.text_input(f"{field}", key=field)

    if st.button("➕ Submit Entry"):
        add_entry(section, entry_data)
        st.success("Entry added successfully!")
else:
    st.info("This section has no fields yet. Go to 'Field Setup' page to add them.")
