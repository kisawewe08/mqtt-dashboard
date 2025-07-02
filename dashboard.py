import os

def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='temperature_log'")
    table_exists = cursor.fetchone()

    if not table_exists:
        conn.close()
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])

    try:
       df = load_data()

    if df.empty:
        st.info("📭 No data found. Waiting for MQTT messages or table to be created.")
        st.stop()

    # Continue processing if data exists
    df["temperature"] = df["message"].apply(extract_temp)
    df = df.dropna(subset=["temperature"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

except Exception as e:
    st.error("❌ Failed to load data from database.")
    st.exception(e)
    st.stop()