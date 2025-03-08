import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
import threading

# Config (Render पर ये values Environment Variables में सेट करें)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # OpenRouter API Key
BOT_TOKEN = os.getenv("BOT_TOKEN")                    # Telegram Bot Token

# Flask App (Render के लिए Port 10000 यूज़ करें)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running!"
def run_flask(): app.run(host='0.0.0.0', port=10000)

# DeepSeek-V3 API Call
async def generate_gali(user_name: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://your-app-name.onrender.com",  # अपना Render URL
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    User को हल्की-फुल्की गाली दो (बिना अश्लील शब्दों के), 
    हिंदी Roman Script में, Funny और Sarcastic टोन में।
    User का नाम: {user_name}
    Example: "Arre {user_name}, tumhare jokes sunkar mere phone ne auto-shutdown kar liya!"
    """
    
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    return response.json()['choices'][0]['message']['content']

# Telegram Bot Handlers
async def gali_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_name = update.message.from_user.first_name
        gali = await generate_gali(user_name)
        await update.message.reply_text(gali)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

if __name__ == "__main__":
    # Start Flask in a separate thread
    threading.Thread(target=run_flask).start()
    
    # Start Telegram Bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("gali", gali_command))
    application.run_polling()
