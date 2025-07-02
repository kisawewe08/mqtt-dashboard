import os

def load_data():
    if not os.path.exists(DB_PATH):
        # Return empty dataframe if db doesn't exist yet
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM temperature_log ORDER BY timestamp DESC LIMIT 200", conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        # Return empty dataframe if table is missing
        return pd.DataFrame(columns=["id", "topic", "message", "timestamp", "temperature"])
if df.empty:
    st.info("📭 No data found. The database is empty or hasn't received messages yet.")
    st.stop()