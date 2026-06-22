from __future__ import annotations

from datetime import datetime, timezone
from app.workers.base_worker import BaseWorker
from app.db.supabase_client import get_supabase_client
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class SubscriptionWorker(BaseWorker):
    def __init__(self, interval_seconds: int = 60 * 60): # Run hourly
        super().__init__("SubscriptionWorker", interval_seconds)

    async def process(self) -> None:
        supabase = get_supabase_client()
        now = datetime.now(timezone.utc).isoformat()
        
        # Check expired trials
        res_trials = supabase.table("subscriptions").select("id, user_id").eq("status", "active").eq("plan", "trial").lt("trial_ends_at", now).execute()
        if res_trials.data:
            for sub in res_trials.data:
                supabase.table("subscriptions").update({"status": "expired"}).eq("id", sub["id"]).execute()
                # Lock out trading account
                supabase.table("trading_accounts").update({"is_active": False}).eq("user_id", sub["user_id"]).execute()
                logger.info(f"Expired trial for user {sub['user_id']}")
                
        # Check expired premiums
        res_premium = supabase.table("subscriptions").select("id, user_id").eq("status", "active").eq("plan", "premium").lt("current_period_end", now).execute()
        if res_premium.data:
            for sub in res_premium.data:
                supabase.table("subscriptions").update({"status": "expired"}).eq("id", sub["id"]).execute()
                # Lock out trading account
                supabase.table("trading_accounts").update({"is_active": False}).eq("user_id", sub["user_id"]).execute()
                logger.info(f"Expired premium for user {sub['user_id']}")


subscription_worker = SubscriptionWorker()
