from __future__ import annotations

import asyncio
from typing import Any

from app.db.supabase_client import get_supabase_client


class BaseRepository:
    def __init__(self, table_name: str) -> None:
        self._table_name = table_name
        self._client = get_supabase_client()

    def _table(self):
        return self._client.table(self._table_name)

    async def get_by_id(self, record_id: str) -> dict | None:
        result = await asyncio.to_thread(
            lambda: self._table().select("*").eq("id", record_id).maybe_single().execute()
        )
        return result.data

    async def get_all(
        self, filters: dict[str, Any] | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        query = self._table().select("*", count="exact")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        result = await asyncio.to_thread(
            lambda: query.range(offset, offset + page_size - 1).execute()
        )
        return result.data or [], result.count or 0

    async def insert(self, data: dict) -> dict:
        result = await asyncio.to_thread(
            lambda: self._table().insert(data).execute()
        )
        return result.data[0] if result.data else {}

    async def update(self, record_id: str, data: dict) -> dict:
        result = await asyncio.to_thread(
            lambda: self._table().update(data).eq("id", record_id).execute()
        )
        return result.data[0] if result.data else {}

    async def delete(self, record_id: str) -> None:
        await asyncio.to_thread(
            lambda: self._table().delete().eq("id", record_id).execute()
        )

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = self._table().select("id", count="exact")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        result = await asyncio.to_thread(lambda: query.execute())
        return result.count or 0
