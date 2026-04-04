#For the streamlit experience
import os.path
import datetime as dt
import pandas as pd
import streamlit as st
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import sqlite3
RESET_DATABASE =True
if RESET_DATABASE:
    db_path = "rosary_tracker.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("db removed")
        except Exception as e:
            print("Could not reset db: {e}")
#Streamlit Page Configuration
st.set_page_config(page_title="Catholic AI Rosary Companion")

# Background coloring
slideshow_css = """
<style>
/*1 Targeting very bootom layer for the animation */
.stApp {
    animation: colorChange 30s infinite alternate !important;
}
/* 2Making all top layer transparent so we can see bottom layer */
[data-testid="stHeader"],
[data-testid="stAppViewContainer"],
[data-testid="stCanvas"],
.main {
    background-color: transparent !important;
    background: transparent !important;
}

@keyframes colorChange {
    20%  { background-color: #2e7d32; }/*Green */
    25%  { background-color: #c62828; }/*Red */
    50%  { background-color: #ffffff; }/*White */
    75%  { background-color: #1565c0; }/*Blue */
    100%  { background-color: #fdd835; }/*Yellow */
}

/* Optional: This is for making text to be readable on changing color background */
h1, h2, h3, p, spam, label {
    color: #1e1e1e !important;
}
</style>
"""
st.markdown(slideshow_css, unsafe_allow_html=True)
st.title("Catholic AI Rosary Habit Builder")
st.markdown("80-Day Spritual Transformation Challenge")

#First hand: Authentication function
def get_calendar_services():
    creds = None
    #file token.pickle stores the user's access and refresh tokens
    if os.path.exists("token.pickle"):
        with open("token.pickle","rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle","wb") as token:
            pickle.dump(creds,token)

    #calender was changed to calendar
    return build("calendar","v3", credentials=creds)
def initialize_database():
    # 1. Connect to the database
    conn = sqlite3.connect('rosary_tracker.db')
    c = conn.cursor()

    # 2. Create the Ledger Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS habit_ledger (
            Day_Number INTEGER PRIMARY KEY,
            Date TEXT,
            Mystery TEXT,
            Status TEXT DEFAULT 'Pending',
            Completion_Time TEXT DEFAULT '00:00:00'
        )
    ''')
    conn.commit()
    conn.close()

# Start the ledger
initialize_database()
def get_db_connection():
    return sqlite3.connect("rosary_tracker.db", check_same_thread=False, timeout=10)

def get_progress():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM habit_ledger", conn)
    conn.close()
    return df
    
def mark_done(day):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE habit_ledger SET Status = 'Completed', Completion_Time = ? WHERE Day_Number = ?", (now, day))
    cursor.execute("UPDATE habit_ledger SET Completion_Time = '00:00:00' WHERE Completion_Time IS NULL OR Completion_Time = 'NONE'")
    conn.commit()
    conn.close()

# 3.Load Data & Today's Info
df = get_progress()
today_obj = dt.date.today()
today_str = today_obj.isoformat()
today_row = df[df["Date"] == today_str]

st.write(f"### Today: {today_obj.strftime("%A, %B %d, %Y")}")

st.sidebar.header("Your Journey")
df = get_progress()
completed = len(df[df["Status"] == "Completed"])
st.sidebar.metric("Days Completed",f"{completed}/80")
st.sidebar.progress(completed / 80)

if not today_row.empty:
    day_num = int(today_row.iloc[0]['Day_Number'])
    Mystery = today_row.iloc[0]['Mystery']
    status = today_row.iloc[0]['Status']
    
    st.subheader(f"Day {day_num} : {Mystery} Mysteries")
    
    if status == 'Pending':
        if st.button(f"Mark Day {day_num} as Completed", use_container_width=True,type="primary"):
            mark_done(day_num)
            st.balloons()
            st.rerun()
        
    else:
        st.button("✅ COMPLETED", disabled=True,use_container_width=True)
        st.success(f"✅ Day {day_num} is already finished. See you tomorrow!")
        
# 5. History Table (Optional)
with st.expander("View Full 80-Day Ledger", expanded=True):
    fresh_df = get_progress()
    st.dataframe(fresh_df[["Day_Number","Date","Mystery","Status","Completion_Time"]], use_container_width=True)

if st.button("Initialize Sunday Challenge"):
    #this calls a function that creates a 80-day rosary commitment plan 
    create_80_day_challenge(service, "2026-04-05T20:00:00")
    st.success("Challenge generated For Sunday")
    st.rerun()
