from __future__ import annotations

import asyncio
from app.workers.base_worker import BaseWorker
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class NotificationWorker(BaseWorker):
    def __init__(self, interval_seconds: int = 10):
        super().__init__("NotificationWorker", interval_seconds)
        self.queue = asyncio.Queue()

    async def process(self) -> None:
        # In a robust system, this queue would be in Redis.
        # Here we just process an in-memory queue.
        while not self.queue.empty():
            task = await self.queue.get()
            try:
                # task could be a dict: {"func": func, "args": (), "kwargs": {}}
                func = task.get("func")
                if func:
                    if asyncio.iscoroutinefunction(func):
                        await func(*task.get("args", ()), **task.get("kwargs", {}))
                    else:
                        func(*task.get("args", ()), **task.get("kwargs", {}))
            except Exception as e:
                logger.error(f"Notification error: {e}")
            finally:
                self.queue.task_done()

    async def enqueue(self, func, *args, **kwargs) -> None:
        await self.queue.put({"func": func, "args": args, "kwargs": kwargs})


notification_worker = NotificationWorker()
