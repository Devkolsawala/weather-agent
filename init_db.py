# init_db.py

import sqlite3

def init_db():
    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            name TEXT,
            description TEXT,
            temperature REAL,
            humidity REAL,
            sent INTEGER,
            opened INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("✅ alerts.db initialized.")

if __name__ == "__main__":
    init_db()
