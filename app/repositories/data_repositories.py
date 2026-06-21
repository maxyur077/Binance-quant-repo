from __future__ import annotations

import asyncio

from app.repositories.base_repository import BaseRepository


class EquityRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("equity_logs")

    async def get_by_account(self, account_id: str, limit: int = 500) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table()
            .select("*")
            .eq("trading_account_id", account_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []


class PositionRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("positions")

    async def get_open_by_account(self, account_id: str) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table()
            .select("*")
            .eq("trading_account_id", account_id)
            .eq("status", "open")
            .execute()
        )
        return result.data or []

    async def get_closed_by_account(
        self, account_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        result = await asyncio.to_thread(
            lambda: self._table()
            .select("*", count="exact")
            .eq("trading_account_id", account_id)
            .eq("status", "closed")
            .order("exit_time", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return result.data or [], result.count or 0


class ScanLogRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("scan_logs")

    async def get_latest(self, limit: int = 50) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table()
            .select("*")
            .order("scan_timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []


class WalletRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("wallet_snapshots")

    async def get_by_account(self, account_id: str, limit: int = 100) -> list[dict]:
        result = await asyncio.to_thread(
            lambda: self._table()
            .select("*")
            .eq("trading_account_id", account_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
