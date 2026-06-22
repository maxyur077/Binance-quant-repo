from __future__ import annotations

from app.db.supabase_client import get_supabase_client
from app.services.broker_factory import broker_factory
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class TradingService:
    @staticmethod
    async def switch_mode(user_id: str, new_mode: str) -> dict:
        """
        Switch between 'demo' and 'live' mode for a user's trading account.
        """
        if new_mode not in ("demo", "live"):
            return {"success": False, "error": "Invalid mode. Must be 'demo' or 'live'."}
            
        supabase = get_supabase_client()
        res = supabase.table("trading_accounts").select("*").eq("user_id", user_id).execute()
        
        if not res.data:
            return {"success": False, "error": "Trading account not found."}
            
        account = res.data[0]
        
        if account["mode"] == new_mode:
            return {"success": True, "message": f"Already in {new_mode} mode."}
            
        if new_mode == "live":
            # Validate API keys before switching
            enc_key = account.get("binance_api_key_enc")
            enc_secret = account.get("binance_api_secret_enc")
            is_testnet = account.get("is_testnet", False)
            
            if not enc_key or not enc_secret:
                return {"success": False, "error": "Binance API keys not configured."}
                
            broker = broker_factory.create_broker("live", enc_key, enc_secret, is_testnet)
            val_res = broker.validate_connection()
            
            if not val_res.get("success"):
                return {"success": False, "error": f"API Validation failed: {val_res.get('error')}"}
                
        update_res = supabase.table("trading_accounts").update({"mode": new_mode}).eq("id", account["id"]).execute()
        return {"success": True, "mode": new_mode, "account": update_res.data[0] if update_res.data else {}}

    @staticmethod
    async def toggle_pause(user_id: str, pause: bool) -> dict:
        supabase = get_supabase_client()
        res = supabase.table("trading_accounts").update({"is_paused": pause}).eq("user_id", user_id).execute()
        if not res.data:
            return {"success": False, "error": "Trading account not found."}
        return {"success": True, "is_paused": pause}


trading_service = TradingService()
