import streamlit as st
import sqlite3
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, limit=None, key="data_refresh")

DB_PATH = "mqtt_data.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM temperature_log ORDER BY timestamp DESC LIMIT 200", conn
    )
    conn.close()
    return df

def extract_temp(msg):
    try:
        return float(msg.split(":")[1].strip().replace("°C", ""))
    except:
        return None

st.set_page_config(page_title="MQTT Dashboard", layout="wide")
st.title("📊 Real-Time MQTT Temperature Dashboard")

# Load and process data
df = load_data()
df["temperature"] = df["message"].apply(extract_temp)
df = df.dropna(subset=["temperature"])
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---- FILTER ----
topics = df["topic"].unique().tolist()
selected_topic = st.selectbox("🔍 Filter by Topic", options=topics)

df = df[df["topic"] == selected_topic]

# ---- ALERTS ----
latest_temp = df["temperature"].iloc[0]
st.markdown(f"### 🌡️ Latest Temperature: `{latest_temp:.2f}°C`")

if latest_temp > 30:
    st.error("🔴 Warning: Temperature is too high!")
elif latest_temp < 15:
    st.warning("🔵 Alert: Temperature is too low!")
else:
    st.success("✅ Temperature is within normal range.")

# ---- STATISTICS ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Temp", f"{df['temperature'].mean():.2f}°C")
col2.metric("Max Temp", f"{df['temperature'].max():.2f}°C")
col3.metric("Min Temp", f"{df['temperature'].min():.2f}°C")
col4.metric("Messages", len(df))

# ---- DATA TABLE ----
st.markdown("### 🧾 Latest Messages")
st.dataframe(df[["timestamp", "topic", "message"]].sort_values("timestamp", ascending=False), use_container_width=True)

# ---- LINE CHART ----
st.markdown("### 📈 Temperature Over Time")
st.line_chart(df.set_index("timestamp")[["temperature"]].sort_index())