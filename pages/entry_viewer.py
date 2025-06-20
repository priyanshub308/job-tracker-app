# 📄 pages/entry_viewer.py
import streamlit as st
import pandas as pd
from google_sheets_helper import sheet
from datetime import datetime

st.set_page_config(page_title="Entry Viewer", layout="wide")
st.title("📄 Entry Viewer — All Your Tracked Data")

# Select section (worksheet)
sections = [ws.title for ws in sheet.worksheets()]
selected_section = st.selectbox("📁 Select a section to view entries", sections)

worksheet = sheet.worksheet(selected_section)
data = worksheet.get_all_values()

if not data or len(data) < 2:
    st.warning("⚠️ No entries found in this section.")
else:
    df = pd.DataFrame(data[1:], columns=data[0])
    df.index += 2  # Offset for correct Google Sheets row numbers

    st.markdown("### 📅 Optional: Filter by Date")
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    if date_columns:
        date_col = st.selectbox("Select date field to filter:", date_columns)
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            min_date, max_date = df[date_col].min(), df[date_col].max()
            start_date, end_date = st.date_input("Date range:", (min_date, max_date))
            df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]
        except:
            st.warning("⚠️ Couldn't parse date format in selected column.")

    # Filter dropdowns
    st.markdown("### 🔍 Filter Entries")
    filters = {}
    for col in df.columns:
        if col in date_columns:
            continue
        unique_vals = df[col].unique().tolist()
        if len(unique_vals) < 50:
            selected = st.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
            filters[col] = selected

    for col, allowed_vals in filters.items():
        df = df[df[col].isin(allowed_vals)]

    st.markdown("---")
    st.subheader(f"📊 Showing {len(df)} entries")

    # Display with edit/delete buttons
    for i, row in df.iterrows():
        cols = st.columns([6, 1, 1])
        cols[0].write(row.to_frame().T)

        if cols[1].button("✏️ Edit", key=f"edit_{i}"):
            st.session_state["edit_row"] = row.to_dict()
            st.session_state["edit_index"] = i
            st.experimental_rerun()

        if cols[2].button("🗑️ Delete", key=f"delete_{i}"):
            worksheet.delete_rows(i)
            st.success(f"Row {i} deleted.")
            st.experimental_rerun()

    # If editing
    if "edit_row" in st.session_state:
        st.markdown("---")
        st.subheader("✏️ Edit Entry")
        edited = {}
        for field, val in st.session_state["edit_row"].items():
            edited[field] = st.text_input(field, value=val)

        if st.button("✅ Save Changes"):
            worksheet.update(f"A{st.session_state['edit_index']}", [list(edited.values())])
            st.success("✅ Entry updated.")
            del st.session_state["edit_row"]
            del st.session_state["edit_index"]
            st.experimental_rerun()

    st.download_button(
        label="⬇️ Download as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{selected_section}_entries.csv",
        mime='text/csv'
    )
