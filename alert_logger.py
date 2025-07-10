import sqlite3
import datetime

DB_FILE = "alerts.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            alert_name TEXT,
            temperature REAL,
            humidity REAL,
            description TEXT,
            sent INTEGER,
            opened INTEGER
        )
        """)
        conn.commit()
 

def log_alert(alert_name, weather, sent=1, opened=None):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO alerts (timestamp, alert_name, temperature, humidity, description, sent, opened)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.datetime.now().isoformat(),
            alert_name,
            weather["temperature"],
            weather["humidity"],
            weather["description"],
            sent,
            opened
        ))
        conn.commit()


def reset_alert_table():
    conn = sqlite3.connect("alerts.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS alerts")
    cursor.execute("""
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            alert_name TEXT,
            description TEXT,
            temperature REAL,
            humidity REAL,
            sent INTEGER,
            opened INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Alerts table reset successfully.")

