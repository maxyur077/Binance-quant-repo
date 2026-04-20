from datetime import datetime, timezone

from azalyst.config import DISCORD_WEBHOOK_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from azalyst.logger import logger


def send_telegram_alert(title: str, message: str, bot_token: str = None, chat_id: str = None):
    token = bot_token or TELEGRAM_BOT_TOKEN
    cid = chat_id or TELEGRAM_CHAT_ID
    if not token or not cid:
        logger.info(f"Telegram alert skipped — no token/chat_id configured")
        return
    try:
        import requests
        # Convert to string to avoid object errors
        title_str = str(title)
        message_str = str(message)
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        full_text = f"<b>{title_str}</b>\n\n{message_str}"
        payload = {"chat_id": cid, "text": full_text, "parse_mode": "HTML"}
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info(f"Telegram alert sent successfully")
    except Exception as e:
        logger.warn(f"Failed to send Telegram alert: {e}")


def send_alerts(title: str, message: str, telegram_token: str = None, telegram_chat_id: str = None):
    send_telegram_alert(title, message, bot_token=telegram_token, chat_id=telegram_chat_id)
