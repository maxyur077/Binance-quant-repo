from __future__ import annotations

from typing import Dict, Any
from app.db.supabase_client import get_supabase_client
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class ConfigService:
    async def get_user_settings(self, user_id: str) -> dict:
        supabase = get_supabase_client()
        res = supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
        
        if not res.data:
            # Create default settings
            default_settings = {
                "user_id": user_id,
                "leverage": 20,
                "risk_per_trade": 0.07,
                "atr_mult": 1.4,
                "tp_rr_ratio": 2.0,
                "margin_per_trade_pct": 0.12,
                "top_n_coins": 20,
                "daily_loss_limit_pct": 25.0,
                "regime_mode": "auto",
                "symbol_whitelist": [],
                "personality_overrides": {}
            }
            insert_res = supabase.table("user_settings").insert(default_settings).execute()
            return insert_res.data[0] if insert_res.data else default_settings
            
        return res.data[0]

    async def update_user_settings(self, user_id: str, updates: Dict[str, Any]) -> dict:
        supabase = get_supabase_client()
        
        # Ensure setting exists first
        await self.get_user_settings(user_id)
        
        res = supabase.table("user_settings").update(updates).eq("user_id", user_id).execute()
        return {"success": True, "settings": res.data[0] if res.data else None}


config_service = ConfigService()
