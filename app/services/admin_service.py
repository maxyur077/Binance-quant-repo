from __future__ import annotations

from typing import Dict, Any
from app.db.supabase_client import get_supabase_client
from app.services.subscription_service import subscription_service
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class AdminService:
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Retrieves global system statistics for the admin dashboard.
        """
        supabase = get_supabase_client()
        
        # In a real dashboard, we would use complex SQL views or RPCs.
        # Here we perform basic aggregations.
        
        # 1. Total Users
        users_res = supabase.table("users").select("id", count="exact").execute()
        total_users = users_res.count if users_res.count is not None else 0
        
        # 2. Active Subscriptions & MRR
        subs_res = supabase.table("subscriptions").select("amount_usd").eq("status", "active").execute()
        active_subs = len(subs_res.data) if subs_res.data else 0
        mrr = sum(float(sub["amount_usd"]) for sub in (subs_res.data or []))
        
        # 3. Open Positions
        pos_res = supabase.table("positions").select("id", count="exact").eq("status", "open").execute()
        open_positions = pos_res.count if pos_res.count is not None else 0
        
        return {
            "total_users": total_users,
            "active_subscriptions": active_subs,
            "mrr_usd": mrr,
            "open_positions": open_positions
        }

    async def manual_confirm_payment(self, user_id: str, amount_usd: float, notes: str = "") -> dict:
        """
        Admin override to mark a payment as done and activate subscription.
        """
        supabase = get_supabase_client()
        
        try:
            # 1. Record manual payment
            payment_data = {
                "user_id": user_id,
                "amount_usd": amount_usd,
                "status": "confirmed",
                "payment_method": "admin_manual",
                "reference_key": f"manual_{notes}"[:64]
            }
            pay_res = supabase.table("payments").insert(payment_data).execute()
            
            # 2. Activate subscription
            sub_res = await subscription_service.activate_subscription(user_id)
            
            logger.info(f"Admin manually confirmed payment of ${amount_usd} for user {user_id}")
            
            return {
                "success": True, 
                "payment": pay_res.data[0] if pay_res.data else None,
                "subscription_ends": sub_res.get("current_period_end")
            }
        except Exception as e:
            logger.error(f"Manual payment confirmation failed: {e}")
            return {"success": False, "error": str(e)}


admin_service = AdminService()
