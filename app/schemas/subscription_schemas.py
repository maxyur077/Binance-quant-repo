from __future__ import annotations

from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    id: str
    plan: str = "trial"
    status: str = "active"
    trial_started_at: str | None = None
    trial_ends_at: str | None = None
    current_period_start: str | None = None
    current_period_end: str | None = None
    amount_usd: float = 50.0
    auto_renew: bool = True
