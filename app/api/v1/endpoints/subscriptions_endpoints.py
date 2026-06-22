from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps.auth_deps import get_current_user
from app.services.subscription_service import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/status")
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    res = await subscription_service.check_subscription_status(current_user["id"])
    return res


@router.post("/trial")
async def start_trial(current_user: dict = Depends(get_current_user)):
    status_res = await subscription_service.check_subscription_status(current_user["id"])
    
    # Allow trial if no subscription exists
    if status_res["plan"] != "none":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User already has or had a subscription."
        )
        
    res = await subscription_service.create_trial_subscription(current_user["id"])
    return {"success": True, "subscription": res}
