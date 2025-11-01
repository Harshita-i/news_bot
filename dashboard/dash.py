import streamlit as st
import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI News Analytics", page_icon="🧠", layout="wide")

st.title("AI News Telegram Bot – Analytics Dashboard")
st.markdown("This dashboard visualizes user interactions and topic trends from the Telegram AI News Bot.")

# Connect to database
# @st.cache_data
@st.cache_data(ttl=60)
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "news_memory.db")
    conn = sqlite3.connect(DB_PATH) 
    # conn = sqlite3.connect("../memory.db")  # adjust path if running from project root
    df_interactions = pd.read_sql_query("SELECT * FROM interactions", conn)
    df_alerts = pd.read_sql_query("SELECT * FROM alerts", conn)
    conn.close()
    return df_interactions, df_alerts

try:
    df_interactions, df_alerts = load_data()
except Exception as e:
    st.error(f"Failed to load database: {e}")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("🔎 Filter Options")
selected_user = st.sidebar.selectbox(
    "Filter by Chat ID (optional):", 
    options=["All"] + sorted(df_interactions["chat_id"].unique().tolist())
)

# Apply filters
if selected_user != "All":
    df_filtered = df_interactions[df_interactions["chat_id"] == selected_user]
else:
    df_filtered = df_interactions

st.sidebar.header("Controls")
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()  # clears all cached data
    st.rerun() # reloads the app


# --- Overview metrics ---
st.subheader("📈 Overview Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Users", len(df_interactions["chat_id"].unique()))
col2.metric("Total Topics Requested", len(df_interactions))
col3.metric("Total Alerts", len(df_alerts))

# --- Top Topics ---
st.subheader("🔥 Top Requested Topics")
top_topics = df_filtered["input_topic"].value_counts().head(10)
st.bar_chart(top_topics)

# --- User Activity Over Time ---
st.subheader("📅 User Activity Over Time")
df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"])
daily = df_filtered.groupby(df_filtered["timestamp"].dt.date).size()
st.line_chart(daily)

# --- Alerts Table ---
st.subheader("🔔 Active Alerts Overview")
st.dataframe(df_alerts)

# --- Sample Summaries ---
st.subheader("📰 Recent AI Summaries")
st.dataframe(df_filtered[["timestamp", "input_topic", "summary"]].tail(10))

st.markdown("---")
st.caption("Built with ❤️ using Streamlit + Telegram + Gemini AI")
