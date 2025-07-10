# smart_checker.py

import logging
from utils import get_weather, send_email, send_sms
from alert_logger import log_alert
import joblib
import os

MODEL_FILE = "alert_model.pkl"
logging.basicConfig(level=logging.INFO)

def predict_if_should_send(weather):
    if not os.path.exists(MODEL_FILE):
        logging.warning("⚠️ ML model not found. Sending by default.")
        return True

    try:
        model = joblib.load(MODEL_FILE)
        desc_feature = 1 if "rain" in weather["description"].lower() or "storm" in weather["description"].lower() else 0
        X = [[weather["temperature"], weather["humidity"], desc_feature]]
        prediction = model.predict(X)[0]
        return bool(prediction)
    except Exception as e:
        logging.error(f"❌ Prediction error: {e}")
        return True

def main():
    weather = get_weather()
    if not weather:
        logging.error("Could not fetch weather.")
        return

    if predict_if_should_send(weather):
        subject = "🌤️ Smart Weather Alert"
        body = (
            f"Smart alert triggered!\n\n"
            f"Weather: {weather['description']}\n"
            f"Temp: {weather['temperature']}°C\n"
            f"Humidity: {weather['humidity']}%"
        )
        send_email(subject, body)
        log_alert("Smart Alert", weather, sent=1, opened=None)
        logging.info("✅ Smart alert sent.")
    else:
        logging.info("🤖 Skipped alert — predicted as irrelevant.")

if __name__ == "__main__":
    main()
