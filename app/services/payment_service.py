from __future__ import annotations

import httpx
from datetime import datetime, timezone, timedelta

from app.db.supabase_client import get_supabase_client
from app.settings import get_settings
from app.services.subscription_service import subscription_service

settings = get_settings()


class PaymentService:
    @staticmethod
    async def create_payment_intent(user_id: str, subscription_id: str) -> dict:
        supabase = get_supabase_client()
        
        # In a real app we'd fetch the live SOL/USD price
        # For simplicity, we assume a static rate or fetch it here
        sol_usd_rate = 150.0  # mock rate
        amount_usd = settings.SUBSCRIPTION_PRICE_USD
        amount_sol = round(amount_usd / sol_usd_rate, 8)
        
        import secrets
        reference_key = secrets.token_hex(16)
        
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=1)
        
        data = {
            "user_id": user_id,
            "subscription_id": subscription_id,
            "amount_usd": amount_usd,
            "amount_sol": amount_sol,
            "sol_usd_rate": sol_usd_rate,
            "receiving_wallet_address": settings.PHANTOM_RECEIVING_WALLET,
            "reference_key": reference_key,
            "status": "pending",
            "payment_method": "phantom",
            "expires_at": expires_at.isoformat()
        }
        res = supabase.table("payments").insert(data).execute()
        return res.data[0] if res.data else {}

    @staticmethod
    async def verify_payment(payment_id: str) -> dict:
        supabase = get_supabase_client()
        res = supabase.table("payments").select("*").eq("id", payment_id).execute()
        if not res.data:
            return {"success": False, "error": "Payment not found"}
            
        payment = res.data[0]
        if payment["status"] == "verified":
            return {"success": True, "message": "Already verified"}
            
        # Here we would query the Solana RPC using payment["reference_key"]
        # using the Solana RPC URL (settings.SOLANA_RPC_URL)
        # For this prototype we will mock success if a transaction_signature was provided
        
        if payment.get("transaction_signature"):
            # Mock verification
            supabase.table("payments").update({
                "status": "verified",
                "verified_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", payment_id).execute()
            
            # Activate subscription
            if payment["subscription_id"]:
                await subscription_service.activate_premium(payment["user_id"], days=30)
                
            return {"success": True, "message": "Payment verified successfully"}
            
        return {"success": False, "error": "No transaction signature provided yet"}


payment_service = PaymentService()
