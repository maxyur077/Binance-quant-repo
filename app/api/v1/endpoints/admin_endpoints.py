from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# We would typically have a get_admin_user dependency here, 
# but for now we'll use get_current_user and check the role inside or assume it's protected by middleware.
from app.api.v1.deps.auth_deps import get_current_user
from app.services.admin_service import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


class ManualConfirmRequest(BaseModel):
    user_id: str
    amount_usd: float
    notes: str = ""


async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


@router.get("/stats")
async def get_stats(admin_user: dict = Depends(get_admin_user)):
    """
    Get global system statistics.
    """
    stats = await admin_service.get_system_stats()
    return stats


@router.post("/payments/manual-confirm")
async def manual_confirm_payment(req: ManualConfirmRequest, admin_user: dict = Depends(get_admin_user)):
    """
    Manually mark a payment as done and activate subscription for a user.
    """
    res = await admin_service.manual_confirm_payment(req.user_id, req.amount_usd, req.notes)
    if not res.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res.get("error"))
    return res
