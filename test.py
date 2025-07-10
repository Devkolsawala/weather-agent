# test_email.py

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

msg = EmailMessage()
msg["Subject"] = "Test Email from Weather Agent"
msg["From"] = os.getenv("EMAIL_SENDER")
msg["To"] = os.getenv("EMAIL_RECIPIENT")
msg.set_content("This is a test email.")

try:
    with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)
        print("✅ Test email sent successfully.")
except Exception as e:
    print(f"❌ Email failed: {e}")
