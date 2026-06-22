from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.v1.deps.auth_deps import get_current_user
from app.db.supabase_client import get_supabase_client
from app.security.encryption_handler import encrypt, decrypt

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramConfigRequest(BaseModel):
    bot_token: str
    chat_id: str
    notify_trades: bool = True
    notify_signals: bool = False
    notify_subscription: bool = True


@router.get("/config")
async def get_telegram_config(current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    res = supabase.table("telegram_configs").select("*").eq("user_id", current_user["id"]).execute()
    
    if not res.data:
        return {"configured": False}
        
    config = res.data[0]
    return {
        "configured": True,
        "chat_id": config.get("chat_id"),
        "is_active": config.get("is_active"),
        "notify_trades": config.get("notify_trades"),
        "notify_signals": config.get("notify_signals"),
        "notify_subscription": config.get("notify_subscription")
    }


@router.post("/config")
async def update_telegram_config(req: TelegramConfigRequest, current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    
    # Encrypt the token
    enc_token = encrypt(req.bot_token)
    
    data = {
        "user_id": current_user["id"],
        "bot_token_enc": enc_token,
        "chat_id": req.chat_id,
        "notify_trades": req.notify_trades,
        "notify_signals": req.notify_signals,
        "notify_subscription": req.notify_subscription,
        "is_active": True
    }
    
    # Upsert logic - check if exists
    res = supabase.table("telegram_configs").select("id").eq("user_id", current_user["id"]).execute()
    if res.data:
        config_id = res.data[0]["id"]
        update_res = supabase.table("telegram_configs").update(data).eq("id", config_id).execute()
        return {"success": True, "config": update_res.data[0]}
    else:
        insert_res = supabase.table("telegram_configs").insert(data).execute()
        return {"success": True, "config": insert_res.data[0]}
