import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
from google_sheets_helper import sheet, get_sections, get_fields_for_section, get_entries_for_section
from dateutil.parser import parse
from google_calendar_helper import create_google_calendar_event

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
                worksheet.delete_rows(i + 2)  # +2 for 1-indexing and header row
                st.success("Deleted!")
                st.rerun()
            if cols[2].button("🔔 Reminder", key=f"remind_{i}"):
                with st.expander(f"⏰ Set Reminder for: {entry_title}"):
                    reminder_date = st.date_input(f"📅 Select Reminder Date", datetime.today(), key=f"reminder_date_{i}")
                    reminder_time = st.time_input(f"⏰ Select Reminder Time", datetime.now().time(), key=f"reminder_time_{i}")
                    if st.button("✅ Confirm Reminder", key=f"confirm_reminder_{i}"):
                        event_date = datetime.combine(reminder_date, reminder_time)
                        calendar_link = create_google_calendar_event(entry_title, event_date)
                        st.success(f"📆 Reminder Created!")
                        st.markdown(f"[🔗 View in Google Calendar]({calendar_link})", unsafe_allow_html=True)

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
            if "Title" in df.columns and selected_date_field != "None":
                for _, row in df.iterrows():
                    try:
                        date = parse(str(row[selected_date_field]))
                        title = row["Title"] if "Title" in row else "Task"
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
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,timeGridWeek,timeGridDay"
                    }
                }
            )

        # Multisection overview
        if st.checkbox("📂 Show all sections combined"):
            combined = []
            for sec in section_names:
                try:
                    sec_data = sheet.worksheet(sec).get_all_records()
                    for d in sec_data:
                        d["Section"] = sec
                        combined.append(d)
                except:
                    continue
            if combined:
                df_combined = pd.DataFrame(combined)
                st.dataframe(df_combined)
                st.download_button("⬇️ Download CSV", data=df_combined.to_csv(index=False), file_name="combined_data.csv", mime="text/csv")
            else:
                st.info("No data found in other sections.")
    else:
        st.info("No entries in this section.")
