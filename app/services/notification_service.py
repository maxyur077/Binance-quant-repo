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

    @staticmethod
    async def send_telegram_message(user_id: str, message: str) -> None:
        """Helper to fetch a user's telegram config and send a message."""
        from app.db.supabase_client import get_supabase_client
        from app.security.encryption_handler import decrypt
        
        supabase = get_supabase_client()
        res = supabase.table("telegram_configs").select("*").eq("user_id", user_id).eq("is_active", True).execute()
        
        if not res.data:
            return
            
        config = res.data[0]
        enc_token = config.get("bot_token_enc")
        chat_id = config.get("chat_id")
        
        if not enc_token or not chat_id:
            return
            
        try:
            bot_token = decrypt(enc_token)
            await NotificationService.send_telegram_alert("Azalyst Alert", message, bot_token, chat_id)
        except Exception:
            pass

notification_service = NotificationService()
