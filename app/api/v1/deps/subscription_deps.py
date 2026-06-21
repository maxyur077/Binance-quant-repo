from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status

from app.api.v1.deps.auth_deps import get_current_active_user
from app.repositories.subscription_repository import SubscriptionRepository

_sub_repo = SubscriptionRepository()


async def require_active_subscription(user: dict = Depends(get_current_active_user)) -> dict:
    sub = await _sub_repo.get_by_user_id(user["id"])

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No subscription found. Please subscribe to access trading features.",
        )

    if sub["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription expired. Please renew to access trading features.",
        )

    now = datetime.now(timezone.utc)

    if sub["plan"] == "trial" and sub.get("trial_ends_at"):
        trial_end = datetime.fromisoformat(sub["trial_ends_at"].replace("Z", "+00:00"))
        if now > trial_end:
            await _sub_repo.update(sub["id"], {"status": "expired"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Trial period has expired. Please subscribe to continue.",
            )

    if sub["plan"] == "monthly" and sub.get("current_period_end"):
        period_end = datetime.fromisoformat(sub["current_period_end"].replace("Z", "+00:00"))
        if now > period_end:
            await _sub_repo.update(sub["id"], {"status": "expired"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription period has expired. Please renew.",
            )

    return user
