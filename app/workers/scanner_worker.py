from __future__ import annotations

import pandas as pd
from app.workers.base_worker import BaseWorker
from app.services.scanner_service import scanner_service
from app.services.signal_service import signal_service
from app.engine.trade_logger import TradeLogger

# In a real app, you would fetch these from an exchange or data provider.
# We're mocking the fetching for the structure.
from app.engine.brokers.demo_broker import DemoBroker
import ccxt

logger = TradeLogger()


class ScannerWorker(BaseWorker):
    def __init__(self, interval_seconds: int = 60 * 15): # Default 15m
        super().__init__("ScannerWorker", interval_seconds)
        self.exchange = ccxt.binanceusdm()
        self.broker = DemoBroker(self.exchange)
        self.symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"] # Mock symbols

    async def process(self) -> None:
        logger.info("Scanner worker starting scan cycle...")
        
        # 1. Fetch BTC data for regime detection
        try:
            btc_ohlcv = self.broker.fetch_ohlcv("BTC/USDT", "15m", 300)
            btc_htf_ohlcv = self.broker.fetch_ohlcv("BTC/USDT", "4h", 300)
            
            columns = ["timestamp", "open", "high", "low", "close", "volume"]
            btc_df = pd.DataFrame(btc_ohlcv, columns=columns)
            btc_htf_df = pd.DataFrame(btc_htf_ohlcv, columns=columns)
        except Exception as e:
            logger.error(f"Failed to fetch BTC data: {e}")
            return
            
        # 2. Fetch data for all symbols
        symbols_data = {}
        for sym in self.symbols:
            try:
                tf_ohlcv = self.broker.fetch_ohlcv(sym, "15m", 300)
                htf_ohlcv = self.broker.fetch_ohlcv(sym, "4h", 300)
                
                tf_df = pd.DataFrame(tf_ohlcv, columns=columns)
                htf_df = pd.DataFrame(htf_ohlcv, columns=columns)
                
                # In a real setup, compute_indicators is called here before passing to scan
                from app.engine.analysis.indicator_engine import compute_indicators
                
                tf_df = compute_indicators(tf_df)
                htf_df = compute_indicators(htf_df) # For htf_filter
                
                symbols_data[sym] = {"tf": tf_df, "htf": htf_df}
            except Exception as e:
                logger.error(f"Failed to fetch data for {sym}: {e}")
                
        # 3. Run scanner service
        if btc_df is not None and not btc_df.empty:
            signals = await scanner_service.scan_market(btc_df, btc_htf_df, symbols_data)
            logger.info(f"Scan complete. Found {len(signals)} signals.")
            
            # 4. Distribute signals
            for sig in signals:
                await signal_service.distribute_signal(sig)


scanner_worker = ScannerWorker()
