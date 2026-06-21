from __future__ import annotations

import asyncio

from app.repositories.base_repository import BaseRepository


class TradingAccountRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("trading_accounts")

    async def get_by_user_id(self, user_id: str, mode: str | None = None) -> list[dict]:
        query = self._table().select("*").eq("user_id", user_id)
        if mode:
            query = query.eq("mode", mode)
        result = await asyncio.to_thread(lambda: query.execute())
        return result.data or []

    async def get_by_api_key_hash(self, key_hash: str) -> dict | None:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("binance_api_key_hash", key_hash).maybe_single().execute()
        )
        return result.data

    async def get_active_accounts(self) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("is_active", True).eq("is_paused", False).execute()
        )
        return result.data or []
