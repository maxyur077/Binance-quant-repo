from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.api.v1.deps.auth_deps import get_current_user
from app.services.config_service import config_service

router = APIRouter(prefix="/config", tags=["config"])


class UpdateSettingsRequest(BaseModel):
    leverage: Optional[int] = None
    risk_per_trade: Optional[float] = None
    atr_mult: Optional[float] = None
    tp_rr_ratio: Optional[float] = None
    margin_per_trade_pct: Optional[float] = None
    top_n_coins: Optional[int] = None
    daily_loss_limit_pct: Optional[float] = None
    regime_mode: Optional[str] = None
    symbol_whitelist: Optional[List[str]] = None
    personality_overrides: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_settings(current_user: dict = Depends(get_current_user)):
    """Get the current user's trading settings."""
    return await config_service.get_user_settings(current_user["id"])


@router.patch("/")
async def update_settings(req: UpdateSettingsRequest, current_user: dict = Depends(get_current_user)):
    """Update specific fields in the user's trading settings."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    
    if not updates:
        return {"success": True, "message": "No changes requested"}
        
    res = await config_service.update_user_settings(current_user["id"], updates)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update settings")
        
    return res
