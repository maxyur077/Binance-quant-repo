from __future__ import annotations

import asyncio

from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("payments")

    async def get_pending_payments(self) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("status", "pending").execute()
        )
        return result.data or []

    async def get_by_reference_key(self, ref: str) -> dict | None:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("reference_key", ref).maybe_single().execute()
        )
        return result.data

    async def get_user_payments(self, user_id: str) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        )
        return result.data or []
