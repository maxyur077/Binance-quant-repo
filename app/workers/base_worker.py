from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod

from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class BaseWorker(ABC):
    def __init__(self, name: str, interval_seconds: int):
        self.name = name
        self.interval_seconds = interval_seconds
        self._is_running = False
        self._task: asyncio.Task | None = None

    @abstractmethod
    async def process(self) -> None:
        """The core logic for the worker loop."""
        ...

    async def _loop(self) -> None:
        logger.info(f"Worker '{self.name}' started. Interval: {self.interval_seconds}s")
        while self._is_running:
            try:
                await self.process()
            except Exception as e:
                logger.error(f"Error in worker '{self.name}': {e}")
            await asyncio.sleep(self.interval_seconds)

    def start(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._loop())

    def stop(self) -> None:
        self._is_running = False
        if self._task:
            self._task.cancel()
        logger.info(f"Worker '{self.name}' stopped.")
