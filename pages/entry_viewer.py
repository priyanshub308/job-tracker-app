# 📄 pages/entry_viewer.py
import streamlit as st
import pandas as pd
from google_sheets_helper import sheet

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
    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Filters (if any fields present)
    st.markdown("### 🔍 Filter Entries")
    filters = {}
    for col in df.columns:
        unique_vals = df[col].unique().tolist()
        if len(unique_vals) < 50:  # only show filter for manageable options
            selected = st.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
            filters[col] = selected

    # Apply filters
    for col, allowed_vals in filters.items():
        df = df[df[col].isin(allowed_vals)]

    st.markdown("---")
    st.subheader(f"📊 Showing {len(df)} entries")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="⬇️ Download as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{selected_section}_entries.csv",
        mime='text/csv'
    )
