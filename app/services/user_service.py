from __future__ import annotations

import asyncio
import hashlib

from fastapi import HTTPException, status

from app.repositories.config_repository import ConfigRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.trading_account_repository import TradingAccountRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import BinanceConnectRequest, UserUpdateRequest
from app.security.encryption_handler import decrypt, encrypt


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        trading_account_repo: TradingAccountRepository,
        config_repo: ConfigRepository,
        subscription_repo: SubscriptionRepository,
    ) -> None:
        self._user_repo = user_repo
        self._ta_repo = trading_account_repo
        self._config_repo = config_repo
        self._sub_repo = subscription_repo

    async def get_profile(self, user_id: str) -> dict:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.pop("password_hash", None)
        return user

    async def update_profile(self, user_id: str, data: UserUpdateRequest) -> dict:
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await self.get_profile(user_id)
        await self._user_repo.update(user_id, update_data)
        return await self.get_profile(user_id)

    async def get_settings(self, user_id: str) -> dict:
        settings = await self._config_repo.get_by_user_id(user_id)
        if not settings:
            settings = await self._config_repo.upsert(user_id, {})
        settings.pop("id", None)
        settings.pop("user_id", None)
        settings.pop("created_at", None)
        settings.pop("updated_at", None)
        return settings

    async def update_settings(self, user_id: str, data: dict) -> dict:
        clean = {k: v for k, v in data.items() if v is not None}
        if clean:
            await self._config_repo.upsert(user_id, clean)
        return await self.get_settings(user_id)

    async def connect_binance(self, user_id: str, request: BinanceConnectRequest) -> dict:
        key_hash = hashlib.sha256(request.api_key.encode()).hexdigest()

        existing = await self._ta_repo.get_by_api_key_hash(key_hash)
        if existing and existing.get("user_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="These Binance API keys are already linked to another account",
            )

        validation = await self._validate_binance_connection(
            request.api_key, request.api_secret, request.is_testnet
        )
        if not validation.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation.get("error", "Failed to connect to Binance"),
            )

        encrypted_key = encrypt(request.api_key)
        encrypted_secret = encrypt(request.api_secret)

        accounts = await self._ta_repo.get_by_user_id(user_id)
        account_data = {
            "user_id": user_id,
            "mode": "live",
            "binance_api_key_enc": encrypted_key,
            "binance_api_secret_enc": encrypted_secret,
            "binance_api_key_hash": key_hash,
            "is_testnet": request.is_testnet,
            "is_active": True,
            "live_balance": validation.get("balance"),
        }

        if accounts:
            await self._ta_repo.update(accounts[0]["id"], account_data)
        else:
            await self._ta_repo.insert(account_data)

        return {
            "is_connected": True,
            "is_testnet": request.is_testnet,
            "is_active": True,
            "live_balance": validation.get("balance"),
        }

    async def get_binance_status(self, user_id: str) -> dict:
        accounts = await self._ta_repo.get_by_user_id(user_id, mode="live")
        if not accounts:
            return {"is_connected": False, "is_testnet": False, "is_active": False, "live_balance": None}
        acc = accounts[0]
        return {
            "is_connected": bool(acc.get("binance_api_key_enc")),
            "is_testnet": acc.get("is_testnet", False),
            "is_active": acc.get("is_active", False),
            "live_balance": acc.get("live_balance"),
        }

    async def disconnect_binance(self, user_id: str) -> None:
        accounts = await self._ta_repo.get_by_user_id(user_id, mode="live")
        if accounts:
            await self._ta_repo.update(accounts[0]["id"], {
                "mode": "demo",
                "binance_api_key_enc": None,
                "binance_api_secret_enc": None,
                "binance_api_key_hash": None,
                "is_active": True,
                "live_balance": None,
            })

    async def get_trading_accounts(self, user_id: str) -> list[dict]:
        return await self._ta_repo.get_by_user_id(user_id)

    async def get_subscription_status(self, user_id: str) -> dict:
        sub = await self._sub_repo.get_by_user_id(user_id)
        if not sub:
            return {"id": "", "plan": "none", "status": "expired"}
        return sub

    async def _validate_binance_connection(
        self, api_key: str, api_secret: str, is_testnet: bool
    ) -> dict:
        try:
            from app.engine.brokers.live_binance_broker import LiveBinanceBroker
            broker = await asyncio.to_thread(
                lambda: LiveBinanceBroker(api_key, api_secret, testnet=is_testnet)
            )
            return await asyncio.to_thread(broker.validate_connection)
        except Exception as e:
            return {"success": False, "error": str(e)}
