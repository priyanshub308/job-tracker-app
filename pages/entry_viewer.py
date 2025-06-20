import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
from google_sheets_helper import sheet, get_sections, get_fields_for_section, get_entries_for_section
from google_calendar_helper import create_google_calendar_event
from dateutil.parser import parse

st.set_page_config(page_title="Entry Viewer", layout="wide")
st.title("📋 View and Manage Entries")

section_names = get_sections()
selected_section = st.selectbox("📁 Select Section", section_names)

if selected_section:
    worksheet = sheet.worksheet(selected_section)
    data = worksheet.get_all_records()
    if data:
        df = pd.DataFrame(data)

        st.markdown("---")
        st.subheader("🔍 Filter Entries")

        # Date filtering
        date_fields = [col for col in df.columns if "date" in col.lower()]
        selected_date_field = st.selectbox("📅 Optional: Filter by Date", ["None"] + date_fields)
        if selected_date_field != "None":
            try:
                df[selected_date_field] = pd.to_datetime(df[selected_date_field], errors='coerce')
                start_date = st.date_input("Start Date", df[selected_date_field].min().date())
                end_date = st.date_input("End Date", df[selected_date_field].max().date())
                df = df[(df[selected_date_field] >= pd.to_datetime(start_date)) & (df[selected_date_field] <= pd.to_datetime(end_date))]
            except:
                st.warning("⚠️ Couldn't parse date format in selected column.")

        # Tag and priority filters
        if "Tags" in df.columns:
            selected_tags = st.multiselect("🏷️ Filter by Tags", options=df["Tags"].dropna().unique())
            if selected_tags:
                df = df[df["Tags"].isin(selected_tags)]

        if "Priority" in df.columns:
            selected_priorities = st.multiselect("🔥 Filter by Priority", options=df["Priority"].dropna().unique())
            if selected_priorities:
                df = df[df["Priority"].isin(selected_priorities)]

        st.markdown("---")
        st.subheader("📌 Entries")

        for i, row in df.iterrows():
            entry_title = row.get("Exam Name") or row.get("Title") or f"Entry {i+1}"
            st.markdown(f"### 🔹 {entry_title}")
            entry_df = pd.DataFrame([row.values], columns=row.index)
            st.table(entry_df)

            cols = st.columns([1, 1, 1])
            if cols[0].button("✏️ Edit", key=f"edit_{i}"):
                st.session_state["edit_row"] = row.to_dict()
                st.session_state["edit_index"] = i
                st.rerun()

            if cols[1].button("🗑️ Delete", key=f"delete_{i}"):
                worksheet.delete_rows(i + 2)  # +2 for header + 0-indexing
                st.success("Deleted!")
                st.rerun()

            if cols[2].button("🔔 Reminder", key=f"remind_{i}"):
                st.session_state["reminder_index"] = i

            # Show reminder section if this is the active one
            if st.session_state.get("reminder_index") == i:
                with st.expander(f"📅 Set Reminder for: {entry_title}", expanded=True):
                    reminder_date = st.date_input("Reminder Date", datetime.today(), key=f"date_{i}")
                    reminder_time = st.time_input("Reminder Time", datetime.now().time(), key=f"time_{i}")
                    if st.button("✅ Add to Google Calendar", key=f"add_reminder_{i}"):
                        dt = datetime.combine(reminder_date, reminder_time)
                        event_link = create_google_calendar_event(entry_title, dt)
                        st.success("📆 Reminder added to Google Calendar!")
                        st.markdown(f"[📎 View Event]({event_link})", unsafe_allow_html=True)
                        del st.session_state["reminder_index"]

        # Calendar View
        st.markdown("---")
        st.subheader("📅 Calendar View")

        with st.container():
            st.markdown(
                """
                <style>
                .fc {
                    font-size: 14px;
                }
                .fc .fc-toolbar-title {
                    font-size: 20px;
                }
                .fc-scroller {
                    overflow-y: auto;
                    max-height: 600px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            events = []
            if selected_date_field != "None":
                for _, row in df.iterrows():
                    try:
                        date = parse(str(row[selected_date_field]))
                        title = row.get("Title") or row.get("Exam Name") or "Task"
                        events.append({
                            "title": title,
                            "start": date.strftime("%Y-%m-%d"),
                            "allDay": True
                        })
                    except:
                        continue

            calendar(
                events=events,
                options={
                    "initialView": "dayGridMonth",
                    "height": "600px",
                    "headerToolbar": {
                        "left": "prev,next
