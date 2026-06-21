from __future__ import annotations

from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    total_users: int = 0
    active_users: int = 0
    trial_users: int = 0
    paid_users: int = 0
    expired_users: int = 0
    monthly_revenue: float = 0.0
    total_revenue: float = 0.0
    total_pnl: float = 0.0
    max_user_limit: int = 100


class AdminUserListItem(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str = "user"
    is_active: bool = True
    subscription_status: str = ""
    subscription_plan: str = ""
    created_at: str
    last_login_at: str | None = None


class AdminUserUpdateRequest(BaseModel):
    is_active: bool | None = None
    role: str | None = None


class ManualPaymentRequest(BaseModel):
    user_id: str
    amount_usd: float
    notes: str = ""
