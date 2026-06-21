from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("users")

    async def get_by_email(self, email: str) -> dict | None:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("email", email).maybe_single().execute()
        )
        return result.data

    async def get_user_count(self) -> int:
        return await self.count()

    async def update_last_login(self, user_id: str) -> None:
        await self.update(user_id, {"last_login_at": datetime.now(timezone.utc).isoformat()})
