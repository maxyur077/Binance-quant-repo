from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.db.supabase_client import get_supabase_client
from app.repositories.config_repository import ConfigRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.trading_account_repository import TradingAccountRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import LoginRequest, SignupRequest, TokenResponse
from app.security.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.security.password_handler import hash_password, verify_password
from app.settings import get_settings


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        subscription_repo: SubscriptionRepository,
        config_repo: ConfigRepository,
        trading_account_repo: TradingAccountRepository,
    ) -> None:
        self._user_repo = user_repo
        self._sub_repo = subscription_repo
        self._config_repo = config_repo
        self._ta_repo = trading_account_repo

    async def signup(self, request: SignupRequest) -> TokenResponse:
        settings = get_settings()

        max_limit = await self._get_max_user_limit()
        current_count = await self._user_repo.get_user_count()
        if current_count >= max_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Registration closed. Maximum {max_limit} users reached.",
            )

        existing = await self._user_repo.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = await self._user_repo.insert({
            "email": request.email,
            "password_hash": hash_password(request.password),
            "full_name": request.full_name,
        })

        now = datetime.now(timezone.utc)
        await self._config_repo.upsert(user["id"], {})

        await self._sub_repo.insert({
            "user_id": user["id"],
            "plan": "trial",
            "status": "active",
            "trial_started_at": now.isoformat(),
            "trial_ends_at": (now + timedelta(days=settings.TRIAL_DURATION_DAYS)).isoformat(),
        })

        await self._ta_repo.insert({
            "user_id": user["id"],
            "mode": "demo",
        })

        return self._build_token_response(user["id"], user.get("role", "user"))

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self._user_repo.get_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated",
            )

        await self._user_repo.update_last_login(user["id"])
        return self._build_token_response(user["id"], user.get("role", "user"))

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user = await self._user_repo.get_by_id(payload["sub"])
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated",
            )

        return self._build_token_response(user["id"], user.get("role", "user"))

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not verify_password(current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        await self._user_repo.update(user_id, {"password_hash": hash_password(new_password)})

    def _build_token_response(self, user_id: str, role: str) -> TokenResponse:
        settings = get_settings()
        token_data = {"sub": user_id, "role": role}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def _get_max_user_limit(self) -> int:
        settings = get_settings()
        try:
            client = get_supabase_client()
            result = await asyncio.to_thread(
                lambda: client.table("system_settings").select("value").eq("key", "max_user_limit").maybe_single().execute()
            )
            if result.data:
                return int(result.data["value"])
        except Exception:
            pass
        return settings.MAX_USER_LIMIT
