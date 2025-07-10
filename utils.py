import os
import json
import requests
import smtplib
import datetime
import geocoder
from email.message import EmailMessage
from dotenv import load_dotenv
from twilio.rest import Client
from ollama import Client as OllamaClient
import base64
from email.mime.text import MIMEText



# Load environment variables
load_dotenv()

# Config from .env
API_KEY = os.getenv("OPENWEATHER_API_KEY")
SENDER = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT = os.getenv("EMAIL_RECIPIENT")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Twilio SMS
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE_NUMBER")

# Load user preferences
try:
    with open("preferences.json", "r") as f:
        user_prefs = json.load(f)
except FileNotFoundError:
    user_prefs = {}

# 🌍 Geo-detect city

def send_email(service, to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = f"Re: {subject}"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_message = service.users().messages().send(
        userId="me",
        body={'raw': raw}
    ).execute()
    print(f"✅ Email sent to: {to}")


def get_current_city():
    try:
        g = geocoder.ip('me')
        city = g.city
        if city:
            print(f"📍 Detected location: {city}")
            return city
        else:
            print("⚠️ Geo detection failed, falling back to .env CITY")
            return os.getenv("CITY")
    except Exception as e:
        print(f"❌ Geo detection error: {e}")
        return os.getenv("CITY")

# 🌤️ 3-hour forecast
def get_forecast_data(city=None):
    city = city or get_current_city()
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["list"]
    except Exception as e:
        print(f"❌ Error fetching forecast: {e}")
        return None

# 📍 Current weather
def get_weather(city=None):
    city = city or get_current_city()
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "city": city
        }
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return None

# 🧠 Generate AI response to user questions
def generate_ask_response(user_question, forecast_data):
    try:
        weather_chunks = []
        for item in forecast_data[:16]:  # Next 48 hours
            dt = datetime.datetime.fromtimestamp(item["dt"]).strftime("%a %I:%M %p")
            desc = item["weather"][0]["description"]
            temp = item["main"]["temp"]
            humidity = item["main"]["humidity"]
            weather_chunks.append(f"{dt}: {desc}, {temp}°C, {humidity}% humidity")
        forecast_text = "\n".join(weather_chunks)

        prompt = (
            f"You are a helpful weather assistant. The user asked:\n"
            f"\"{user_question}\"\n\n"
            f"Here is the 48-hour weather forecast:\n{forecast_text}\n\n"
            f"Based on this, provide a short, human-friendly answer."
        )

        client = OllamaClient()
        response = client.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return None

# ⚠️ Severity classifier
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

# 🔍 Extract weather condition tags
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

# 📧 Email notifier
def send_email(subject, body, recipient=None):
    try:
        actual_recipient = recipient or RECIPIENT
        if not actual_recipient:
            raise ValueError("❌ EMAIL_RECIPIENT not set in .env or passed explicitly.")

        print(f"📨 Sending email to: {actual_recipient}")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER
        msg["To"] = actual_recipient
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
            print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# 📱 SMS notifier
def send_sms(body):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        message = client.messages.create(
            body=body,
            from_=TWILIO_FROM,
            to=RECIPIENT_PHONE
        )
        print(f"📨 SMS sent: {message.sid}")
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")

# 🧠 LLM summary
def generate_natural_summary_local(weather):
    prompt = (
        f"Generate a short, friendly weather summary for today.\n"
        f"Details:\n"
        f"- Description: {weather['description']}\n"
        f"- Temperature: {weather['temperature']}°C\n"
        f"- Humidity: {weather['humidity']}%\n\n"
        f"Keep it concise and optionally suggest something (e.g., carry an umbrella)."
    )
    try:
        client = OllamaClient()
        response = client.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"❌ LLM summary error: {e}")
        return "Unable to generate summary."
