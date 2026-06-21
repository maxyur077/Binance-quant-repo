from __future__ import annotations

import asyncio

from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("audit_logs")

    async def log(
        self,
        user_id: str | None,
        action: str,
        resource: str = "",
        resource_id: str = "",
        details: dict | None = None,
        ip_address: str = "",
        user_agent: str = "",
    ) -> None:
        data = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        await asyncio.to_thread(lambda: self._table().insert(data).execute())
