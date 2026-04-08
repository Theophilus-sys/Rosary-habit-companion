#For the streamlit experience
import streamlit as st
import datetime as dt
import pandas as pd
import sqlite3

st.set_page_config(page_title="Rosary Habit Companion",page_icon="🙏")
#One Click Progress Updating
def mark_day_as_done(day_number):
    conn = sqlite3.connect("rosary_tracker.db")
    cursor = conn.cursor()
    completion_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''UPDATE habit_ledger SET Status = 'Completed', Completion_Time = ? WHERE Day_Number = ?''',(completion_time, day_number))
    
    conn.commit()
    conn.close()
    
#Data Fetching
def view_ledger():
    conn = sqlite3.connect("rosary_tracker.db")
    try:
        df = pd.read_sql_query("SELECT * FROM habit_ledger", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

df_ledger = view_ledger()

total_day = 80
completed_days = len(df_ledger[df_ledger["Status"]=="Completed"]) if not df_ledger.empty else 0
progress_percent = completed_days/total_day
today_date = dt.date.today().strftime("%Y-%m-%d")
today_row = df_ledger[df_ledger["Date"].str.contains(today_date)] if not df_ledger.empty else pd.DataFrame()
# Sidebar setup
with st.sidebar:
    st.header("📊Progress Tracker")
    st.write(f"**{completed_days}/{total_day} Day Completed**")
    st.progress(progress_percent)
    st.divider()
    
# --- 1. FIND TODAY'S DATA ---
today_str = dt.date.today().strftime("%Y-%m-%d")
# Check if today exists in the Date column
today_row = df_ledger[df_ledger['Date'].astype(str).str.contains(today_str)] if not df_ledger.empty else pd.DataFrame()

#Customizing Main Page UI with displaying the ledger
st.title("🌍AI Rosary Habit Companion")

# --- 2. THE SAFETY SHIELD (This prevents the IndexError) ---
if not today_row.empty:
    # Use .iloc safely because we know the row isn't empty
    current_day = int(today_row.iloc[0]["Day_Number"])
    mystery = today_row.iloc[0]["Mystery"]

    col1, col2 =st.columns(2)
    with col1:
        st.metric("Today's date", today_str)

    with col2:
        st.metric("Challenge Day", f"Day {current_day}")
    
    st.subheader(f"Today's Mystery: **{mystery}**")
    
    if st.button("✅ Mark Today as Done", use_container_width=True):
        mark_day_as_done(current_day)
        st.session_state.celebrate = True
        st.rerun()
else:
    # This fallback keeps the app from crashing!
    st.metric("Challenge Day", "Not Scheduled")
    st.warning(f"⚠️ No entry found for {today_str} in the ledger.")
    st.info("Ensure the challenge is initialized for today's date in the sidebar.")

# Dropdown Ledger 
st.divider()
with st.expander("View Full Habit Ledger"):
   
    if not df_ledger.empty:
        st.dataframe(df_ledger, use_container_width=True,hide_index=True)
    else:
        st.write("No Data Available Yet.")

if st.session_state.get("celebrate"):
    st.balloons()
    st.success("Great Job Today! Can't Wait To See You Tomorrow")
    st.session_state.celebrate = False
