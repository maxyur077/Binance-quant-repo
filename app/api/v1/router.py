from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.auth_endpoints import router as auth_router
from app.api.v1.endpoints.binance_endpoints import router as binance_router
from app.api.v1.endpoints.health_endpoints import router as health_router
from app.api.v1.endpoints.user_endpoints import router as user_router

from app.api.v1.endpoints.trading_endpoints import router as trading_router
from app.api.v1.endpoints.positions_endpoints import router as positions_router
from app.api.v1.endpoints.subscriptions_endpoints import router as subscriptions_router
from app.api.v1.endpoints.payments_endpoints import router as payments_router
from app.api.v1.endpoints.telegram_endpoints import router as telegram_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(binance_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(trading_router)
api_v1_router.include_router(positions_router)
api_v1_router.include_router(subscriptions_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(telegram_router)
