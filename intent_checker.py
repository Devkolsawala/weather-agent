# intent_checker.py

import json
import logging
from utils import get_weather, send_email, send_sms
from alert_logger import log_alert

logging.basicConfig(level=logging.INFO)

# Load user-defined intents
with open("preferences.json", "r") as f:
    preferences = json.load(f)

intents = preferences.get("intents", [])

def matches_conditions(weather, conditions):
    """Evaluates conditions for an intent."""
    try:
        temp = weather["temperature"]
        humidity = weather["humidity"]
        desc = weather["description"].lower()

        if "temp_gt" in conditions and temp <= conditions["temp_gt"]:
            return False
        if "temp_lt" in conditions and temp >= conditions["temp_lt"]:
            return False
        if "humidity_gt" in conditions and humidity <= conditions["humidity_gt"]:
            return False
        if "humidity_lt" in conditions and humidity >= conditions["humidity_lt"]:
            return False
        if "description_contains" in conditions:
            match = any(keyword.lower() in desc for keyword in conditions["description_contains"])
            if not match:
                return False
        return True
    except Exception as e:
        logging.error(f"Error checking conditions: {e}")
        return False

def main():
    weather = get_weather()
    if not weather:
        logging.error("❌ Could not fetch weather data.")
        return

    for intent in intents:
        name = intent.get("name")
        conditions = intent.get("conditions", {})
        alert_type = intent.get("type", "email")

        if matches_conditions(weather, conditions):
            message = (
                f"🚨 Alert: '{name}' triggered!\n\n"
                f"Matched Weather:\n"
                f"- Description: {weather['description']}\n"
                f"- Temp: {weather['temperature']}°C\n"
                f"- Humidity: {weather['humidity']}%"
            )

            if alert_type == "sms":
                send_sms(message)
            else:
                send_email(f"🚨 Weather Alert: {name}", message)

            # Log to DB for ML learning
            log_alert(name, weather, sent=1, opened=None)

            logging.info(f"✅ Alert sent for intent: {name}")

if __name__ == "__main__":
    main()
