from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.repositories.base_repository import BaseRepository


class ConfigRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("user_settings")

    async def get_by_user_id(self, user_id: str) -> dict | None:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("user_id", user_id).maybe_single().execute()
        )
        return result.data

    async def upsert(self, user_id: str, data: dict) -> dict:
        data["user_id"] = user_id
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = await asyncio.to_thread(
            lambda: self._table().upsert(data, on_conflict="user_id").execute()
        )
        return result.data[0] if result.data else {}
