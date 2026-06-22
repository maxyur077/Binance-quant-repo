from __future__ import annotations

from datetime import datetime, timezone
from app.workers.base_worker import BaseWorker
from app.db.supabase_client import get_supabase_client
from app.services.payment_service import payment_service
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class PaymentWorker(BaseWorker):
    def __init__(self, interval_seconds: int = 30): # Poll for blockchain verifications
        super().__init__("PaymentWorker", interval_seconds)

    async def process(self) -> None:
        supabase = get_supabase_client()
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. Expire old pending payments
        supabase.table("payments").update({"status": "expired"}).eq("status", "pending").lt("expires_at", now).execute()
        
        # 2. Verify pending payments
        # In a real app we'd fetch all pending and check the blockchain
        # For prototype, we just mock the logic inside verify_payment if signature exists
        res = supabase.table("payments").select("id, transaction_signature").eq("status", "pending").execute()
        pending = res.data if res.data else []
        
        for p in pending:
            if p.get("transaction_signature"):
                await payment_service.verify_payment(p["id"])


payment_worker = PaymentWorker()
