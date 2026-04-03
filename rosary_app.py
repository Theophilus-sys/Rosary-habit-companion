#For the streamlit experience
import streamlit as st
import sqlite3
import pandas as pd
import datetime

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
today_obj = datetime.date.today()
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
