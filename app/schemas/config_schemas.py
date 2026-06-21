from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class TradingConfigResponse(BaseModel):
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


class TradingConfigUpdateRequest(BaseModel):
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


class GoldListResponse(BaseModel):
    symbols: list[str]


class RegimeResponse(BaseModel):
    regime: str
    mode: str
    personality: str
