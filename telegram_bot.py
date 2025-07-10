import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
from utils import get_weather, generate_natural_summary_local

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CITY = os.getenv("CITY", "Surat,IN")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I’m your AI Weather Assistant.\n\n"
        "Type /weather to get today’s summary.\n"
        "You can also set your city using /setcity <City,CountryCode> (e.g., /setcity Mumbai,IN)"
    )

# /weather command
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.user_data.get("city", DEFAULT_CITY)
    weather = get_weather(city)
    if weather:
        summary = generate_natural_summary_local(weather)
        await update.message.reply_text(f"📍 *{city}*\n\n{summary}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Failed to fetch weather data. Please check your city or try again later.")

# /setcity command
async def set_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /setcity City,CountryCode (e.g., /setcity Surat,IN)")
        return
    city = " ".join(context.args)
    context.user_data["city"] = city
    await update.message.reply_text(f"✅ City set to: {city}")

# /unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 I didn’t recognize that command. Try /weather or /start.")

# Main function
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("setcity", set_city))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🤖 Telegram bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keeps the bot running forever
    await asyncio.Event().wait()

# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error running bot: {e}")
