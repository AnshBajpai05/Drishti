import speech_recognition as sr
import subprocess
import logging
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

BOT_TOKEN = '7626871646:AAFGR4hRxDZwCy5T1Jljnao5Y4ry74eMnec' 
AUTHORIZED_USERS = [631******9, 160******7] #both are mine currently (2 accounts)
CAREGIVER_CHAT_ID = 160******27  

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

def speak(text):
    subprocess.run(["espeak", text])

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Say 'share location' to send your location.")
        logging.info("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            logging.info(f"Command heard: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I could not understand.")
        except sr.RequestError:
            speak("Speech service is not available.")
    return ""

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized user.")
        return

    location = update.message.location
    if location:
        lat = location.latitude
        lon = location.longitude
        text = f"📍 Location from user:\nLatitude: {lat}\nLongitude: {lon}\nhttps://maps.google.com/?q={lat},{lon}"

        await update.message.reply_text("✅ Location received. Sending to caregiver.")
        speak("Location received. Sending to caregiver.")

        await context.bot.send_message(chat_id=CAREGIVER_CHAT_ID, text=text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    await update.message.reply_text(f"Welcome. Your user ID is {user_id}")

async def run_telegram_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    speak("Telegram bot is running. Please open Telegram and share your location.")
    await app.run_polling()

if __name__ == '__main__':
    speak("Voice-controlled Telegram bot started.")
    command = listen_for_command()
    if "share location" in command:
        import asyncio
        asyncio.run(run_telegram_bot())
    else:
        speak("No valid command. Please say 'share location'.")
