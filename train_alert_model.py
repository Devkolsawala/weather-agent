# train_alert_model.py

import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

DB_FILE = "alerts.db"
MODEL_FILE = "alert_model.pkl"

# Connect to DB and load data
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql("SELECT * FROM alerts WHERE opened IS NOT NULL", conn)

# Basic preprocessing
df["description"] = df["description"].str.contains("rain|storm|thunder", case=False).astype(int)

# Features and label
X = df[["temperature", "humidity", "description"]]
y = df["opened"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, MODEL_FILE)
print("✅ Model saved to:", MODEL_FILE)
