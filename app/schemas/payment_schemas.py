from __future__ import annotations

from pydantic import BaseModel


class PaymentCreateResponse(BaseModel):
    payment_id: str
    qr_base64: str
    wallet_address: str
    amount_usdt: float
    reference_key: str
    expires_at: str


class PaymentStatusResponse(BaseModel):
    payment_id: str
    status: str
    transaction_signature: str | None = None
    verified_at: str | None = None


class PaymentHistoryItem(BaseModel):
    id: str
    amount_usd: float
    status: str
    payment_method: str = "phantom"
    created_at: str
    verified_at: str | None = None
