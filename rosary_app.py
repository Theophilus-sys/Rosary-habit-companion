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
service = get_calendar_services()
def create_80_day_challenge(service, start_date_str):
    # 1. Convert start string to a datetime object
    start_date = dt.datetime.fromisoformat(start_date_str)
    
    print(f"🚀 Starting 80-Day Rosary Challenge from {start_date.date()}...")

    for day in range(1, 81):
        # Calculate the date for this specific day of the challenge
        current_date = start_date + dt.timedelta(days=day-1)
        
        # Determine the Mystery based on the day of the week
        day_name = current_date.strftime("%A")
        mysteries = {
            "Monday": "Joyful", "Tuesday": "Sorrowful", "Wednesday": "Glorious",
            "Thursday": "Luminous", "Friday": "Sorrowful", "Saturday": "Joyful",
            "Sunday": "Glorious"
        }
        mystery = mysteries.get(day_name)

        # Define the Event structure
        event_body = {
            'summary': f'Rosary Day {day}: {mystery} Mysteries',
            'description': f'Day {day} of your 80-day habit transformation. Meditation on the {mystery} Mysteries.',
            'start': {
                'dateTime': current_date.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (current_date + dt.timedelta(minutes=40)).isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'colorId': '11', # Google's "Bold Blue" to make it stand out
            'reminders': {
                'useDefault': False,
                'overrides': [{'method': 'popup', 'minutes': 15}],
            },
        }

        # 2. Push to Google Calendar
        # 3. Push to your mobile-synced primary calendar
        result = service.events().insert(calendarId='primary', body=event_body).execute()
        print(f"✅ 80-Day Automation Active! Link: {result.get('htmlLink')}")
        
        if day % 10 == 0 or day == 1:
            print(f"✅ Day {day} synced! Mystery:{mystery}")
            
    print("✨ Mission Accomplished: All 80 days are now on your calendar!")
def initialize_database():
    conn = sqlite3.connect("rosary_tracker.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS habit_ledger
                  (date TEXT PRIMARY KEY, day_number INTEGER, mystery TEXT, status TEXT)''')
    conn.commit()
    conn.close()
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
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE habit_ledger SET status = 'Completed', completion_time = ? WHERE day_number = ?", (now, day))
    conn.commit()
    conn.close()

# 3.Load Data & Today's Info
df = get_progress()
today_obj = dt.date.today()
today_str = today_obj.isoformat()
today_row = df[df["date"] == today_str]

# # 4. Today's Mystery & Action
# today_date = datetime.date.today().isoformat()
# today_data = df[df['date'] == today_date]

st.write(f"### Today: {today_obj.strftime("%A, %B %d, %Y")}")

st.sidebar.header("Your Journey")
df = get_progress()
completed = len(df[df["status"] == "Completed"])
st.sidebar.metric("Days Completed",f"{completed}/80")
st.sidebar.progress(completed / 80)

if not today_row.empty:
    day_num = int(today_row.iloc[0]['day_number'])
    mystery = today_row.iloc[0]['mystery']
    status = today_row.iloc[0]['status']
    
    st.subheader(f"Day {day_num} : {mystery} Mysteries")
    
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
    st.dataframe(fresh_df[["day_number","date","mystery","status"]], use_container_width=True)

if st.button("Initialize Sunday Challenge"):
    #this calls a function that creates a 80-day rosary commitment plan 
    create_80_day_challenge(service, "2026-04-05T20:00:00")
    st.success("Challenge generated For Sunday")
    st.rerun()
