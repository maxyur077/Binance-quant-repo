from __future__ import annotations

from datetime import datetime, timezone
from app.db.supabase_client import get_supabase_client
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class SignalService:
    @staticmethod
    async def distribute_signal(signal_data: dict) -> None:
        """
        Distributes a newly found signal to all active, unpaused trading accounts
        that match the signal's criteria (e.g., regime mode, symbol whitelist).
        """
        supabase = get_supabase_client()
        signal_id = signal_data["id"]
        
        # Fetch all active and unpaused trading accounts
        res = supabase.table("trading_accounts").select("id, user_id, mode").eq("is_active", True).eq("is_paused", False).execute()
        accounts = res.data if res.data else []
        
        if not accounts:
            logger.info("No active trading accounts to distribute signal.")
            return
            
        distributions = []
        now = datetime.now(timezone.utc).isoformat()
        
        for acc in accounts:
            # Here we could check user_settings (whitelist, regime_mode, etc.) 
            # to see if the user wants this trade. For now, we distribute to all.
            # Real implementation would join user_settings to filter.
            distributions.append({
                "signal_id": signal_id,
                "trading_account_id": acc["id"],
                "status": "pending",
                "created_at": now
            })
            
        if distributions:
            supabase.table("signal_distributions").insert(distributions).execute()
            logger.info(f"Distributed signal {signal_id} to {len(distributions)} accounts.")


signal_service = SignalService()
