# 🌦️ AI-Powered Weather Assistant 🤖

![License](https://img.shields.io/github/license/Devkolsawala/weather-agent)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Last Commit](https://img.shields.io/github/last-commit/Devkolsawala/weather-agent)
![Stars](https://img.shields.io/github/stars/Devkolsawala/weather-agent?style=social)

> A fully autonomous AI agent that fetches weather data daily, summarizes it in natural language using a local LLM (via Ollama), and delivers it via email and SMS based on your preferences.

---

## 🚀 Features

- 🌤 Fetches real-time weather using **OpenWeatherMap API**
- 🤖 Uses **Mistral LLM via Ollama** to generate friendly summaries
- 📧 Sends updates to your **email**
- 📱 Sends alerts to **mobile via SMS (Twilio)**
- 🔁 Runs daily via **APScheduler**
- 🔐 Secure with `.env` & config files

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Devkolsawala/weather-agent.git
cd weather-agent


2. Create a Virtual Environment

python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux


3. Install Required Packages

pip install -r requirements.txt


4. Create .env File

# .env
OPENWEATHER_API_KEY=your_openweather_key
CITY=Surat,IN

EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password_or_app_password
EMAIL_RECIPIENT=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
RECIPIENT_PHONE_NUMBER=+91XXXXXXXXXX


5. Set Preferences (Optional)

{
  "alert_triggers": ["storm", "heavy_rain", "high_temp", "high_humidity"],
  "skip_normal": true
}


🤖 LLM (Ollama) Setup

1. Install Ollama (if not already installed)
Download Ollama

2. Pull the Mistral model

ollama pull mistral

3. Make sure ollama is running locally

▶️ Run the Agent
 
python weather_agent.py


🌐 Deployment Options
| Platform   | How                                                                          |
| ---------- | ---------------------------------------------------------------------------- |
| 🖥️ Local  | Run via terminal + APScheduler (already built-in)                            |
| 🐳 Docker  | Add `Dockerfile`, run as service or cron                                     |
| 💻 Windows | Use **Task Scheduler** to run `python weather_agent.py` daily                |
| 🐧 Linux   | Add to **cron**: `@daily /path/to/venv/bin/python /path/to/weather_agent.py` |


🧰 Tech Stack
Python 3.10+

OpenWeatherMap API

Ollama (Mistral Model)

Twilio SMS API

smtplib + email for SMTP email

APScheduler for background scheduling

dotenv + .env for config

requests, json, logging


📄 License
This project is licensed under the MIT License.

🙌 Acknowledgements
Ollama for local LLM integration

OpenWeatherMap

Twilio for SMS alerts

Shields.io for README badges

