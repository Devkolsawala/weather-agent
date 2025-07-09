from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from utils import (
    get_weather,
    classify_weather,
    extract_triggers,
    send_email,
    send_sms,
    generate_natural_summary_local,
    user_prefs
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    logging.info("Starting weather fetch and email job...")

    weather = get_weather()
    if weather is None:
        logging.error("Failed to retrieve weather data. Email not sent.")
        return

    category = classify_weather(weather)
    triggers = extract_triggers(weather)

    if not any(trigger in user_prefs["alert_triggers"] for trigger in triggers):
        logging.info(f"Skipping email: no preferred triggers matched: {triggers}")
        return

    if category == "normal" and user_prefs.get("skip_normal", True):
        logging.info("Skipping normal weather update as per preferences.")
        return

    summary = generate_natural_summary_local(weather)
    if summary:
        body = f"{summary}\n\n⚠️ Alerts: {', '.join(triggers)}"
    else:
        body = (
            f"📋 Description: {weather['description'].capitalize()}\n"
            f"🌡 Temperature: {weather['temperature']}°C\n"
            f"💧 Humidity: {weather['humidity']}%"
        )

    subject = f"[{category.upper()}] Daily Weather Update"
    send_email(subject, body)

    if category in ["alert", "severe"]:
        send_sms(f"[{category.upper()}] {weather['description'].capitalize()}, "
                 f"{weather['temperature']}°C, Humidity: {weather['humidity']}%")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, trigger="interval",seconds = 30 )#hours=24, next_run_time=None
    logging.info("Weather Agent started. First job will run in 24 hours.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")



# from apscheduler.schedulers.blocking import BlockingScheduler
# import logging
# from utils import get_weather, send_email, classify_weather, load_user_preferences

# # Optional: Configure logging for better debugging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def job():
#     logging.info("Starting weather fetch and email job...")

#     prefs = load_user_preferences()
#     weather = get_weather()

#     if weather:
#         category, triggers = classify_weather(weather)

#         # Check user preference for this type of alert
#         if prefs["email_frequency"] == "severe_only" and category != "severe":
#             logging.info("Skipping email: user only wants severe alerts.")
#             return
#         if prefs["email_frequency"] == "alert_only" and category == "normal":
#             logging.info("Skipping email: user only wants alerts/severe.")
#             return

#         # If no matched triggers are enabled by user, skip
#         if not any(prefs["notify_on"].get(trigger, False) for trigger in triggers):
#             logging.info(f"Skipping email: no preferred triggers matched: {triggers}")
#             return

#         # Construct email
#         subject = f"[{category.upper()}] Personalized Weather Update"
#         body = f"🌤 Description: {weather['description'].capitalize()}\n"
#         body += f"🌡 Temperature: {weather['temperature']}°C\n"
#         body += f"💧 Humidity: {weather['humidity']}%\n\n"

#         if category == "severe":
#             body += "⚠️ Take precautions! Severe conditions detected.\n"
#         elif category == "alert":
#             body += "💡 Be aware: potential impact from current conditions.\n"
#         else:
#             body += "✅ All clear. Enjoy your day!\n"

#         send_email(subject, body)

#     else:
#         logging.error("Failed to retrieve weather data. Email not sent.")

# if __name__ == "__main__":
#     scheduler = BlockingScheduler()
#     # Run every 24 hours (once a day)
#     scheduler.add_job(job, trigger="interval", seconds=10 ) #hours=24, next_run_time=None

#     logging.info("Weather Agent started. First job will run in 24 hours.")
#     try:
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         logging.info("Scheduler stopped.")


