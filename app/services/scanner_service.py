from __future__ import annotations

import pandas as pd
from datetime import datetime, timezone

from app.engine.consensus_engine import multi_strategy_scan
from app.engine.analysis.regime_detector import detect_market_wide, get_regime_details
from app.engine.analysis.personality_manager import get_personality
from app.db.supabase_client import get_supabase_client
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class ScannerService:
    @staticmethod
    async def scan_market(
        btc_df: pd.DataFrame, 
        btc_htf_df: pd.DataFrame, 
        symbols_data: dict[str, dict[str, pd.DataFrame]]
    ) -> list[dict]:
        """
        Runs the core engine logic to find trading signals across all symbols.
        symbols_data should map symbol -> {"tf": df, "htf": df}
        """
        # 1. Detect market regime
        regime = detect_market_wide(btc_df, btc_htf_df)
        personality = get_personality(regime)
        
        logger.info(f"Market Regime: {regime.value} | Personality: {personality.name}")
        
        signals = []
        supabase = get_supabase_client()
        now = datetime.now(timezone.utc).isoformat()
        
        for symbol, dfs in symbols_data.items():
            df = dfs.get("tf")
            htf_df = dfs.get("htf")
            
            if df is None or df.empty:
                continue
                
            scan_result = multi_strategy_scan(
                df=df,
                symbol=symbol,
                htf_df=htf_df,
                personality=personality,
                silent=True,
                return_full=True
            )
            
            if scan_result and scan_result.get("sig"):
                sig_data = scan_result["sig"]
                scores = scan_result["scores"]
                
                # Format signal for database
                db_signal = {
                    "symbol": symbol,
                    "direction": sig_data["direction"],
                    "atr": sig_data["atr"],
                    "signal_name": sig_data["signal"],
                    "strategies": sig_data["strategies"],
                    "buy_count": scores["buy_count"],
                    "sell_count": scores["sell_count"],
                    "buy_weight": scores["buy_weight"],
                    "sell_weight": scores["sell_weight"],
                    "regime": regime.value,
                    "personality": personality.name,
                    "scan_timestamp": now,
                }
                
                res = supabase.table("signals").insert(db_signal).execute()
                if res.data:
                    db_signal["id"] = res.data[0]["id"]
                    signals.append(db_signal)
                    
        return signals


scanner_service = ScannerService()
