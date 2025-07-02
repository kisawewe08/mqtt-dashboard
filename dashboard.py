import streamlit as st
import sqlite3
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, limit=None, key="data_refresh")

DB_PATH = "mqtt_data.db"

# Safely load data
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='temperature_log'")
    table_exists = cursor.fetchone()
    if not table_exists:
        conn.close()
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])

    # Try to load data
    try:
        df = pd.read_sql_query(
            "SELECT * FROM temperature_log ORDER BY timestamp DESC LIMIT 200",
            conn
        )
        conn.close()
        return df
    except Exception:
        conn.close()
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])

# Extract temperature value from message text
def extract_temp(msg):
    try:
        return float(msg.split(":")[1].strip().replace("°C", ""))
    except:
        return None

# Set page config
st.set_page_config(page_title="MQTT Dashboard", layout="wide")
st.title("📊 Real-Time MQTT Temperature Dashboard")

# Try to load and process data
try:
    df = load_data()

    if df.empty:
        st.info("📭 No data found. Waiting for MQTT messages or table to be created.")
        st.stop()

    # Process temp and timestamp
    df["temperature"] = df["message"].apply(extract_temp)
    df = df.dropna(subset=["temperature"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Topic filter
    topics = df["topic"].unique().tolist()
    selected_topic = st.selectbox("🔍 Filter by Topic", options=topics)
    df = df[df["topic"] == selected_topic]

    # Show latest temp
    latest_temp = df["temperature"].iloc[0]
    st.markdown(f"### 🌡️ Latest Temperature: `{latest_temp:.2f}°C`")

    # Alerts
    if latest_temp > 30:
        st.error("🔴 Warning: Temperature is too high!")
    elif latest_temp < 15:
        st.warning("🔵 Alert: Temperature is too low!")
    else:
        st.success("✅ Temperature is within normal range.")

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Temp", f"{df['temperature'].mean():.2f}°C")
    col2.metric("Max Temp", f"{df['temperature'].max():.2f}°C")
    col3.metric("Min Temp", f"{df['temperature'].min():.2f}°C")
    col4.metric("Messages", len(df))

    # Table
    st.markdown("### 🧾 Latest Messages")
    st.dataframe(df[["timestamp", "topic", "message"]].sort_values("timestamp", ascending=False), use_container_width=True)

    # Chart
    st.markdown("### 📈 Temperature Over Time")
    st.line_chart(df.set_index("timestamp")[["temperature"]].sort_index())

except Exception as e:
    st.error("❌ Error loading dashboard.")
    st.exception(e)