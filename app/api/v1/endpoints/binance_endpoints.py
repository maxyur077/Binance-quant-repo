from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth_deps import get_current_active_user
from app.api.v1.deps.subscription_deps import require_active_subscription
from app.dependencies import get_user_service
from app.schemas.base_schemas import SuccessResponse
from app.schemas.user_schemas import BinanceConnectRequest, BinanceStatusResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users/me/binance", tags=["Binance"])


@router.post("/connect", response_model=BinanceStatusResponse)
async def connect_binance(
    request: BinanceConnectRequest,
    user: dict = Depends(require_active_subscription),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.connect_binance(user["id"], request)


@router.get("/status", response_model=BinanceStatusResponse)
async def get_binance_status(
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    return await user_service.get_binance_status(user["id"])


@router.post("/disconnect", response_model=SuccessResponse)
async def disconnect_binance(
    user: dict = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> SuccessResponse:
    await user_service.disconnect_binance(user["id"])
    return SuccessResponse(message="Binance disconnected successfully")
