# fake_logs.py

import sqlite3
import random
from datetime import datetime, timedelta

descriptions = [
    "clear sky", "light rain", "heavy rain", "thunderstorm", "few clouds", "overcast clouds"
]

def generate_dummy_alerts(n=20):
    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()

    for _ in range(n):
        temp = round(random.uniform(22, 38), 2)
        humidity = random.randint(40, 95)
        desc = random.choice(descriptions)
        name = "Smart Alert"

        # Randomly decide if it was opened
        opened = random.choice([0, 1])

        # Random past time
        ts = datetime.now() - timedelta(days=random.randint(0, 10), hours=random.randint(0, 12))

        c.execute("""
            INSERT INTO alerts (timestamp, name, description, temperature, humidity, sent, opened)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ts, name, desc, temp, humidity, 1, opened))

    conn.commit()
    conn.close()
    print(f"✅ Inserted {n} fake alerts into alerts.db.")

if __name__ == "__main__":
    generate_dummy_alerts(50)  # You can change the number here
