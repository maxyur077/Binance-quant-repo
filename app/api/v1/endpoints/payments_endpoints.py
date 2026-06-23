from __future__ import annotations

import base64
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.v1.deps.auth_deps import get_current_user
from app.services.payment_service import payment_service
from app.services.qr_service import qr_service
from app.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentIntentRequest(BaseModel):
    subscription_id: str


@router.post("/intent")
async def create_payment_intent(req: PaymentIntentRequest, current_user: dict = Depends(get_current_user)):
    res = await payment_service.create_payment_intent(current_user["id"], req.subscription_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create payment intent")
        
    return {"success": True, "payment": res}


@router.get("/{payment_id}/qr")
async def get_payment_qr(payment_id: str, current_user: dict = Depends(get_current_user)):
    supabase = get_supabase_client()
    res = supabase.table("payments").select("*").eq("id", payment_id).eq("user_id", current_user["id"]).execute()
    
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    payment = res.data[0]
    
    try:
        qr_bytes = qr_service.generate_solana_pay_qr(
            recipient=payment["receiving_wallet_address"],
            amount=payment["amount_sol"],
            reference=payment["reference_key"],
            label="Binance Quant",
            message=f"Premium Subscription"
        )
        b64_qr = base64.b64encode(qr_bytes).decode("utf-8")
        return {"success": True, "qr_base64": b64_qr}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
