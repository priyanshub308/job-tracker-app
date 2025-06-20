# 📄 field_editor.py
import streamlit as st
from google_sheets_helper import sheet

st.set_page_config(page_title="Field Editor", layout="wide")
st.title("🧩 Field Editor — Customize Your Section Headers")

# Get all sheet names
sections = [ws.title for ws in sheet.worksheets()]
st.sidebar.header("Select or Create Section")

selected_section = st.sidebar.selectbox("Choose a section (sheet)", sections)

# Get current headers from row 1
worksheet = sheet.worksheet(selected_section)
headers = worksheet.row_values(1)

st.subheader(f"Current fields in '{selected_section}':")
if headers:
    st.code(", ".join(headers), language="text")
else:
    st.info("No fields found in this section.")

st.markdown("---")
st.subheader("➕ Add or Replace Fields")

field_input = st.text_area("Enter comma-separated field names:",
                           placeholder="e.g., examname, date, score, status")

if st.button("💾 Save Fields"):
    new_fields = [f.strip() for f in field_input.split(",") if f.strip()]
    if new_fields:
        worksheet.delete_rows(1)  # clear header
        worksheet.insert_row(new_fields, 1)
        st.success("✅ Fields updated successfully!")
        st.rerun()
    else:
        st.warning("⚠️ Please enter at least one valid field name.")
