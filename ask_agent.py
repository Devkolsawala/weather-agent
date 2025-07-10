# ask_agent.py

import sys
from utils import get_forecast_data, send_email, generate_ask_response
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

RECIPIENT = os.getenv("EMAIL_RECIPIENT")

def generate_response(question: str) -> str:
    # Placeholder for real LLM logic
    return f"Hi! You asked: '{question.strip()}'. Here's a sample weather-based reply!"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ask_agent.py \"<Your weather question>\"")
        sys.exit(1)

    user_question = sys.argv[1]
    logging.info(f"🧠 Question received: {user_question}")

    if not RECIPIENT:
        logging.error("❌ EMAIL_RECIPIENT not found in .env!")
        sys.exit(1)
    else:
        logging.info(f"📨 Will send email to: {RECIPIENT}")

    forecast_data = get_forecast_data()
    if not forecast_data:
        logging.error("Failed to get weather forecast.")
        return

    answer = generate_ask_response(user_question, forecast_data)
    if answer:
        send_email("🤖 Weather Assistant Answer", answer, RECIPIENT)  # ✅ pass explicitly
        logging.info("✅ Answer emailed successfully.")
    else:
        logging.error("Failed to generate answer.")


if __name__ == "__main__":
    main()
