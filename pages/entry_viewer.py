# 📄 pages/entry_viewer.py
import streamlit as st
import pandas as pd
from google_sheets_helper import sheet
from datetime import datetime
from dateutil.parser import parse

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

    # Convert reminder dates and filter
    def try_parse_date(x):
        try:
            return parse(x, fuzzy=True)
        except:
            return pd.NaT

    st.markdown("### 📅 Optional: Filter by Date")
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    if date_columns:
        date_col = st.selectbox("Select date field to filter:", date_columns)
        df[date_col] = df[date_col].apply(try_parse_date)
        min_date, max_date = df[date_col].min(), df[date_col].max()
        start_date, end_date = st.date_input("Date range:", (min_date, max_date))
        df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]

    # Tag & Priority filtering
    tag_col = next((col for col in df.columns if col.lower() == "tags"), None)
    priority_col = next((col for col in df.columns if "priority" in col.lower()), None)

    if tag_col:
        tags = sorted(set(tag.strip() for val in df[tag_col].dropna() for tag in val.split(",")))
        selected_tags = st.multiselect("🧩 Filter by tags", tags, default=tags)
        df = df[df[tag_col].apply(lambda x: any(tag in x.split(",") for tag in selected_tags) if isinstance(x, str) else False)]

    if priority_col:
        priorities = df[priority_col].dropna().unique().tolist()
        selected_priority = st.multiselect("🎯 Filter by priority", priorities, default=priorities)
        df = df[df[priority_col].isin(selected_priority)]

    st.markdown("---")
    st.subheader(f"📊 Showing {len(df)} entries")

    # Display entries with edit/delete/reminder
    for i, row in df.iterrows():
        cols = st.columns([6, 1, 1, 1])
        cols[0].write(row.to_frame().T)

        if cols[1].button("✏️ Edit", key=f"edit_{i}"):
            st.session_state["edit_row"] = row.to_dict()
            st.session_state["edit_index"] = i
            st.rerun()

        if cols[2].button("🗑️ Delete", key=f"delete_{i}"):
            worksheet.delete_rows(i)
            st.success(f"Row {i} deleted.")
            st.rerun()

        if cols[3].button("🔔 Remind", key=f"remind_{i}"):
            st.info("📬 Reminder feature coming soon (email or mobile notifications)")

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
            st.rerun()

    st.download_button(
        label="⬇️ Download as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{selected_section}_entries.csv",
        mime='text/csv'
    )

    # Multisection overview (basic preview)
    if st.checkbox("📂 Show all sections combined"):
        st.markdown("## 🔄 Combined Overview")
        combined_df = pd.DataFrame()
        for sec in sections:
            ws = sheet.worksheet(sec)
            d = ws.get_all_values()
            if d and len(d) > 1:
                subdf = pd.DataFrame(d[1:], columns=d[0])
                subdf["Section"] = sec
                combined_df = pd.concat([combined_df, subdf], ignore_index=True)
        st.dataframe(combined_df)
