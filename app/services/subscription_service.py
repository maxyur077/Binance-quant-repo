from __future__ import annotations

from datetime import datetime, timezone, timedelta
from app.db.supabase_client import get_supabase_client
from app.settings import get_settings

settings = get_settings()


class SubscriptionService:
    @staticmethod
    async def create_trial_subscription(user_id: str) -> dict:
        supabase = get_supabase_client()
        now = datetime.now(timezone.utc)
        trial_ends = now + timedelta(days=settings.TRIAL_DURATION_DAYS)

        data = {
            "user_id": user_id,
            "plan": "trial",
            "status": "active",
            "trial_started_at": now.isoformat(),
            "trial_ends_at": trial_ends.isoformat(),
            "amount_usd": settings.SUBSCRIPTION_PRICE_USD,
            "auto_renew": False,
        }
        res = supabase.table("subscriptions").insert(data).execute()
        return res.data[0] if res.data else {}

    @staticmethod
    async def check_subscription_status(user_id: str) -> dict:
        supabase = get_supabase_client()
        res = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()
        if not res.data:
            return {"active": False, "plan": "none", "reason": "no_subscription"}

        sub = res.data[0]
        now = datetime.now(timezone.utc)

        if sub["status"] == "active":
            if sub["plan"] == "trial":
                ends_at = datetime.fromisoformat(sub["trial_ends_at"])
                if now > ends_at:
                    supabase.table("subscriptions").update({"status": "expired"}).eq("id", sub["id"]).execute()
                    return {"active": False, "plan": "trial", "reason": "trial_expired"}
                return {"active": True, "plan": "trial"}
            
            elif sub["plan"] == "premium":
                if sub["current_period_end"]:
                    ends_at = datetime.fromisoformat(sub["current_period_end"])
                    if now > ends_at:
                        supabase.table("subscriptions").update({"status": "expired"}).eq("id", sub["id"]).execute()
                        return {"active": False, "plan": "premium", "reason": "subscription_expired"}
                return {"active": True, "plan": "premium"}
                
        return {"active": False, "plan": sub["plan"], "reason": sub["status"]}

    @staticmethod
    async def activate_premium(user_id: str, days: int = 30) -> dict:
        supabase = get_supabase_client()
        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=days)

        data = {
            "plan": "premium",
            "status": "active",
            "current_period_start": now.isoformat(),
            "current_period_end": period_end.isoformat(),
        }
        res = supabase.table("subscriptions").update(data).eq("user_id", user_id).execute()
        return res.data[0] if res.data else {}


subscription_service = SubscriptionService()
