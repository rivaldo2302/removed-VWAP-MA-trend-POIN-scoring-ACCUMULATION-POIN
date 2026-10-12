import os
import requests

try:
    from telegram_config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    # The private config is optional so the scanner can still run without Telegram.
    TELEGRAM_BOT_TOKEN = ""
    TELEGRAM_CHAT_ID = ""

def send_telegram_message(message_text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Gagal mengirim ke Telegram: TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum di-set.")
        print("Set dulu environment variable-nya sebelum menjalankan daily_scanner.py.")
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Gagal mengirim ke Telegram: {e}")
        return None
