from __future__ import annotations

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
import json

from app.db.supabase_client import get_supabase_client
from app.services.notification_service import notification_service
from app.engine.backtest_engine import backtest_engine
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class BacktestService:
    async def start_backtest(self, user_id: str, config: Dict[str, Any], symbols: List[str], start_date: str, end_date: str) -> dict:
        """
        Initiates a backtest asynchronously and returns the backtest ID immediately.
        """
        supabase = get_supabase_client()
        
        # 1. Create a backtest record in the DB
        backtest_data = {
            "user_id": user_id,
            "config": config,
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "status": "running"
        }
        res = supabase.table("backtests").insert(backtest_data).execute()
        if not res.data:
            return {"success": False, "error": "Failed to initialize backtest."}
            
        backtest_id = res.data[0]["id"]
        
        # 2. Fire and forget the async runner
        asyncio.create_task(self._run_backtest_async(backtest_id, user_id, config, symbols, start_date, end_date))
        
        return {"success": True, "backtest_id": backtest_id, "status": "running"}

    async def _run_backtest_async(self, backtest_id: str, user_id: str, config: Dict[str, Any], symbols: List[str], start_date: str, end_date: str):
        """
        Background task that executes the backtest, saves results, and notifies the user.
        """
        logger.info(f"Background backtest {backtest_id} started for user {user_id}")
        supabase = get_supabase_client()
        
        try:
            results_summary = {}
            all_trades = []
            
            # TODO: Fetch historical data from a provider (e.g., Binance via ccxt or historical CSVs)
            # For now, we simulate data fetch and engine execution.
            import pandas as pd
            import numpy as np
            
            for symbol in symbols:
                # MOCK DATA GENERATION FOR STRUCTURE
                # In production, this data loader will fetch real OHLCV arrays
                dates = pd.date_range(start=start_date, end=end_date, freq="15min")
                df = pd.DataFrame({
                    "timestamp": dates,
                    "open": np.random.uniform(30000, 60000, len(dates)),
                    "high": np.random.uniform(30000, 60000, len(dates)),
                    "low": np.random.uniform(30000, 60000, len(dates)),
                    "close": np.random.uniform(30000, 60000, len(dates)),
                    "volume": np.random.uniform(10, 1000, len(dates)),
                })
                
                # Mock BTC data for regime
                btc_df = df.copy() 
                
                # Run the engine
                res = await backtest_engine.run(symbol, df, btc_df, config)
                
                if "error" not in res:
                    results_summary[symbol] = {
                        "total_trades": res["total_trades"],
                        "win_rate": res["win_rate"],
                        "net_profit": res["net_profit"]
                    }
                    
                    # Store trades for this symbol
                    for t in res.get("trades", []):
                        all_trades.append({
                            "backtest_id": backtest_id,
                            "symbol": symbol,
                            "direction": 1, # Mocked
                            "entry_price": t["entry"],
                            "exit_price": t["exit"],
                            "pnl_usd": t["pnl"],
                            "close_reason": t["reason"],
                            "strategies": "MACD,RSI", # Mocked
                            # Timestamps omitted for mock simplicity
                        })
                        
            # Insert all trades to the DB
            if all_trades:
                # Batch insert (max 1000 per request usually, but we assume small for now)
                supabase.table("backtest_trades").insert(all_trades).execute()
                
            # Aggregate total metrics
            total_profit = sum(r["net_profit"] for r in results_summary.values())
            
            # 3. Update backtest record to complete
            now = datetime.now(timezone.utc).isoformat()
            supabase.table("backtests").update({
                "status": "completed",
                "result_summary": {
                    "per_symbol": results_summary,
                    "total_profit_usd": total_profit,
                    "total_trades": len(all_trades)
                },
                "completed_at": now
            }).eq("id", backtest_id).execute()
            
            logger.info(f"Backtest {backtest_id} completed successfully.")
            
            # 4. Notify user via Telegram
            msg = f"📊 *Backtest Completed!*\nID: `{backtest_id}`\nTotal Profit: `${total_profit:.2f}`\nTrades: `{len(all_trades)}`"
            await notification_service.send_telegram_message(user_id, msg)
            
        except Exception as e:
            logger.error(f"Backtest {backtest_id} failed: {e}")
            supabase.table("backtests").update({
                "status": "failed",
                "result_summary": {"error": str(e)}
            }).eq("id", backtest_id).execute()
            
            await notification_service.send_telegram_message(user_id, f"❌ *Backtest Failed*\nID: `{backtest_id}`\nError: {e}")


backtest_service = BacktestService()
