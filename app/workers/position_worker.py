from __future__ import annotations

from app.workers.base_worker import BaseWorker
from app.services.position_service import position_service
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class PositionWorker(BaseWorker):
    def __init__(self, interval_seconds: int = 5): # Poll frequently for pending signals
        super().__init__("PositionWorker", interval_seconds)

    async def process(self) -> None:
        # Process distributions (entry)
        await position_service.process_pending_distributions()
        
        # Here we would also add logic to check open positions,
        # update PnL, trail stops, and close positions if TP/SL hit.
        # This requires tracking the live price which could be done via WS
        # or polling.


position_worker = PositionWorker()
