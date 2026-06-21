from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

from fastapi import APIRouter

from app import __version__
from app.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("/")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/db")
async def db_health() -> dict:
    start = time.monotonic()
    try:
        client = get_supabase_client()
        await asyncio.to_thread(
            lambda: client.table("system_settings").select("key").limit(1).execute()
        )
        latency = round((time.monotonic() - start) * 1000, 2)
        return {"status": "connected", "latency_ms": latency}
    except Exception as e:
        latency = round((time.monotonic() - start) * 1000, 2)
        return {"status": "error", "latency_ms": latency, "detail": str(e)}
