from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str = "user"
    is_active: bool = True
    is_email_verified: bool = False
    created_at: str
    last_login_at: str | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = None


class UserSettingsResponse(BaseModel):
    leverage: int = 20
    risk_per_trade: float = 0.07
    atr_mult: float = 1.4
    tp_rr_ratio: float = 2.0
    margin_per_trade_pct: float = 0.12
    top_n_coins: int = 20
    daily_loss_limit_pct: float = 25.0
    daily_profit_target: float = 0.0
    regime_mode: str = "auto"
    manual_regime: str = "sideways"
    symbol_whitelist: list[str] = []
    personality_overrides: dict[str, Any] = {}


class UserSettingsUpdateRequest(BaseModel):
    leverage: int | None = None
    risk_per_trade: float | None = None
    atr_mult: float | None = None
    tp_rr_ratio: float | None = None
    margin_per_trade_pct: float | None = None
    top_n_coins: int | None = None
    daily_loss_limit_pct: float | None = None
    daily_profit_target: float | None = None
    regime_mode: str | None = None
    manual_regime: str | None = None
    symbol_whitelist: list[str] | None = None
    personality_overrides: dict[str, Any] | None = None


class BinanceConnectRequest(BaseModel):
    api_key: str
    api_secret: str
    is_testnet: bool = False


class BinanceStatusResponse(BaseModel):
    is_connected: bool = False
    is_testnet: bool = False
    is_active: bool = False
    live_balance: float | None = None


class TradingAccountResponse(BaseModel):
    id: str
    mode: str
    is_testnet: bool = False
    is_active: bool = True
    is_paused: bool = False
    initial_balance: float = 100.0
    current_balance: float = 100.0
    live_balance: float | None = None
    daily_pnl: float = 0.0
    created_at: str
