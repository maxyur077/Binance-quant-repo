from __future__ import annotations

import httpx

from app.settings import get_settings

settings = get_settings()


class NotificationService:
    @staticmethod
    async def send_telegram_alert(
        title: str, message: str, bot_token: str | None = None, chat_id: str | None = None
    ) -> None:
        token = bot_token
        cid = chat_id
        if not token or not cid:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        full_text = f"<b>{str(title)}</b>\n\n{str(message)}"
        payload = {"chat_id": cid, "text": full_text, "parse_mode": "HTML"}

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10.0)
                resp.raise_for_status()
        except Exception:
            pass


notification_service = NotificationService()
