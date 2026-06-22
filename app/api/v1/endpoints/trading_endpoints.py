from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.v1.deps.auth_deps import get_current_user
from app.services.trading_service import trading_service

router = APIRouter(prefix="/trading", tags=["trading"])


class ModeSwitchRequest(BaseModel):
    mode: str


class PauseRequest(BaseModel):
    pause: bool


@router.post("/mode")
async def switch_trading_mode(req: ModeSwitchRequest, current_user: dict = Depends(get_current_user)):
    res = await trading_service.switch_mode(current_user["id"], req.mode)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("error"))
    return res


@router.post("/pause")
async def toggle_trading_pause(req: PauseRequest, current_user: dict = Depends(get_current_user)):
    res = await trading_service.toggle_pause(current_user["id"], req.pause)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("error"))
    return res
