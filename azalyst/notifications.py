from datetime import datetime, timezone

from azalyst.config import DISCORD_WEBHOOK_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from azalyst.logger import logger


def send_telegram_alert(title: str, message: str, bot_token: str = None, chat_id: str = None):
    token = bot_token or TELEGRAM_BOT_TOKEN
    cid = chat_id or TELEGRAM_CHAT_ID
    if not token or not cid:
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        text = f"{title}\n\n{message}"
        payload = {"chat_id": cid, "text": text}
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.warn(f"Failed to send Telegram alert: {e}")


def send_alerts(title: str, message: str, telegram_token: str = None, telegram_chat_id: str = None):
    send_telegram_alert(title, message, bot_token=telegram_token, chat_id=telegram_chat_id)
