from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from app.repositories.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("subscriptions")

    async def get_by_user_id(self, user_id: str) -> dict | None:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("user_id", user_id).maybe_single().execute()
        )
        return result.data

    async def get_active_subscriptions(self) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("status", "active").execute()
        )
        return result.data or []

    async def get_expiring_soon(self, hours: int = 24) -> list[dict]:
        cutoff = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
        result = await asyncio.to_thread(
            lambda: self._table()
            .select("*")
            .eq("status", "active")
            .lt("current_period_end", cutoff)
            .execute()
        )
        return result.data or []
