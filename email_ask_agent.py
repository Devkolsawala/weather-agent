import imaplib
import email
import time
import os
from utils import get_forecast_data, generate_ask_response, send_email
from dotenv import load_dotenv

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def fetch_latest_question():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN SUBJECT "Weather Question")')
        if status != "OK":
            print("No new weather question emails.")
            return None, None

        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])
            sender = email.utils.parseaddr(msg["From"])[1]
            subject = msg["Subject"]

            # Get plain text body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            mail.store(num, '+FLAGS', '\\Seen')  # Mark as read
            return sender, body.strip()
        return None, None

    except Exception as e:
        print(f"❌ IMAP Error: {e}")
        return None, None

def handle_question_via_email():
    sender_email, question = fetch_latest_question()
    if not question:
        return

    print(f"📥 New question from {sender_email}: {question}")

    forecast_data = get_forecast_data()
    if not forecast_data:
        print("❌ Forecast data fetch failed.")
        return

    answer = generate_ask_response(question, forecast_data)
    if answer:
        send_email("🤖 Weather Assistant Response", answer, recipient=sender_email)
        print("✅ Response sent.")
    else:
        print("❌ Failed to generate a response.")

if __name__ == "__main__":
    while True:
        handle_question_via_email()
        print("🔄 Waiting 60 seconds for next check...")
        time.sleep(60)
