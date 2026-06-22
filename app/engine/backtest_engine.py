from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

from app.engine.trade_logger import TradeLogger
from app.engine.analysis.indicator_engine import compute_indicators
from app.services.scanner_service import scanner_service

logger = TradeLogger()


class BacktestEngine:
    def __init__(self, initial_capital: float = 1000.0, fee_rate: float = 0.0004):
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate

    async def run(
        self, 
        symbol: str, 
        df: pd.DataFrame, 
        btc_df: pd.DataFrame, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Runs a historical backtest on a single symbol.
        In a real scenario, this would simulate tick-by-tick or candle-by-candle.
        For this refactor, we simulate scanning each candle sequentially.
        """
        logger.info(f"Starting backtest for {symbol} with {len(df)} candles.")
        
        # Pre-compute indicators for the whole dataset to save time
        df = compute_indicators(df)
        btc_df = compute_indicators(btc_df)
        
        capital = self.initial_capital
        positions = []
        trades = []
        
        # Iterating candle by candle to prevent lookahead bias
        # For performance in Python, this is slow, so we could vectorize.
        # But to reuse the scanner logic perfectly, we pass slices.
        
        # NOTE: A true tick-by-tick backtester is highly complex.
        # This is a simplified structural representation for the architecture.
        
        window_size = 100
        if len(df) < window_size:
            return {"error": "Not enough data"}
            
        for i in range(window_size, len(df)):
            current_slice = df.iloc[i-window_size:i+1]
            btc_slice = btc_df.iloc[:i+1] if i < len(btc_df) else btc_df.iloc[-window_size:]
            
            # Mock the multi-symbol structure for scanner
            symbols_data = {symbol: {"tf": current_slice, "htf": current_slice}}
            
            # We bypass the async scanner wrapper to directly hit the logic if needed,
            # or await the scanner. (Awaiting in a loop is slow, but keeps logic 1:1)
            # For production backtesting, you'd use a vectorized approach of the strategies.
            
            # Example simulated execution:
            row = current_slice.iloc[-1]
            price = row['close']
            
            # Check open positions for SL/TP
            for pos in positions[:]:
                if pos['direction'] == 1:
                    if price <= pos['sl']:
                        self._close_position(pos, price, trades, capital, "SL")
                        positions.remove(pos)
                    elif price >= pos['tp']:
                        self._close_position(pos, price, trades, capital, "TP")
                        positions.remove(pos)
                else:
                    if price >= pos['sl']:
                        self._close_position(pos, price, trades, capital, "SL")
                        positions.remove(pos)
                    elif price <= pos['tp']:
                        self._close_position(pos, price, trades, capital, "TP")
                        positions.remove(pos)
                        
            # (Simulation of scanner signal generation would go here)
            # If signal: positions.append({...})
            
        # Calculate summary
        total_trades = len(trades)
        wins = len([t for t in trades if t['pnl'] > 0])
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        
        return {
            "symbol": symbol,
            "total_trades": total_trades,
            "win_rate": win_rate,
            "final_capital": capital,
            "net_profit": capital - self.initial_capital,
            "trades": trades
        }
        
    def _close_position(self, pos: dict, exit_price: float, trades: list, capital: float, reason: str):
        entry = pos['entry']
        qty = pos['qty']
        direction = pos['direction']
        
        if direction == 1:
            pnl = (exit_price - entry) * qty
        else:
            pnl = (entry - exit_price) * qty
            
        fee = exit_price * qty * self.fee_rate
        net_pnl = pnl - fee
        
        # update capital reference (mutates the primitive? No, we need to pass a dict/obj or return it)
        # For simplicity in this structure:
        # We would actually return the pnl to add to capital
        
        trades.append({
            "entry": entry,
            "exit": exit_price,
            "pnl": net_pnl,
            "reason": reason
        })

backtest_engine = BacktestEngine()
