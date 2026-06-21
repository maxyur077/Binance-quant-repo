from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth_deps import get_current_active_user
from app.dependencies import get_user_service
from app.schemas.base_schemas import SuccessResponse
from app.schemas.subscription_schemas import SubscriptionResponse
from app.schemas.user_schemas import (
    TradingAccountResponse,
    UserProfile,
    UserSettingsResponse,
    UserSettingsUpdateRequest,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_profile(
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.get_profile(user["id"])


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    request: UserUpdateRequest,
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.update_profile(user["id"], request)


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_settings(
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.get_settings(user["id"])


@router.patch("/me/settings", response_model=UserSettingsResponse)
async def update_settings(
    request: UserSettingsUpdateRequest,
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.update_settings(user["id"], request.model_dump(exclude_none=True))


@router.get("/me/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.get_subscription_status(user["id"])


@router.get("/me/trading-accounts", response_model=list[TradingAccountResponse])
async def get_trading_accounts(
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> list[dict]:
    return await user_service.get_trading_accounts(user["id"])
