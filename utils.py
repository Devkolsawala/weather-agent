import os
import requests
import smtplib
import json
from email.message import EmailMessage
from dotenv import load_dotenv
from twilio.rest import Client
from ollama import Client as OllamaClient

load_dotenv()

# Env vars
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY")
SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT = os.getenv("EMAIL_RECIPIENT")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

# Twilio
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE_NUMBER")

# Load user preferences
with open("preferences.json", "r") as f:
    user_prefs = json.load(f)

# Weather fetch
def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

# Classify severity
def classify_weather(weather):
    desc = weather['description'].lower()
    temp = weather['temperature']
    humidity = weather['humidity']
    if "storm" in desc or "thunder" in desc or "heavy rain" in desc:
        return "severe"
    elif "rain" in desc or temp > 35 or humidity > 80:
        return "alert"
    else:
        return "normal"

# Extract triggers
def extract_triggers(weather):
    desc = weather['description'].lower()
    temp = weather['temperature']
    humidity = weather['humidity']
    triggers = []
    if "storm" in desc or "thunder" in desc:
        triggers.append("storm")
    if "rain" in desc and "heavy" in desc:
        triggers.append("heavy_rain")
    if humidity > 80:
        triggers.append("high_humidity")
    if temp > 35:
        triggers.append("high_temp")
    return triggers

# Email
def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER
        msg["To"] = RECIPIENT
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# SMS
def send_sms(body):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        message = client.messages.create(
            body=body,
            from_=TWILIO_FROM,
            to=RECIPIENT_PHONE
        )
        print(f"SMS sent: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

# Local LLM summary via Ollama
def generate_natural_summary_local(weather):
    prompt = (
        f"Generate a short, friendly weather summary for today.\n"
        f"Details:\n"
        f"- Description: {weather['description']}\n"
        f"- Temperature: {weather['temperature']}°C\n"
        f"- Humidity: {weather['humidity']}%\n\n"
        f"Keep it concise, human-readable, and optionally include a light suggestion like 'carry an umbrella' or 'good day for outdoor activities'."
    )
    try:
        client = OllamaClient()
        response = client.chat(
            model="mistral",  # ✅ Mistral: Fast and accurate for short generation
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"LLM summary error: {e}")
        return None