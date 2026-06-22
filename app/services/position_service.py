from __future__ import annotations

from datetime import datetime, timezone
from app.db.supabase_client import get_supabase_client
from app.services.broker_factory import broker_factory
from app.engine.trade_logger import TradeLogger

logger = TradeLogger()


class PositionService:
    @staticmethod
    async def process_pending_distributions() -> None:
        """
        Polls for pending signal distributions and executes them via the appropriate broker.
        """
        supabase = get_supabase_client()
        
        # 1. Fetch pending distributions
        res = supabase.table("signal_distributions").select(
            "id, signal_id, trading_account_id, signals(*), trading_accounts(*)"
        ).eq("status", "pending").execute()
        
        distributions = res.data if res.data else []
        if not distributions:
            return
            
        now = datetime.now(timezone.utc).isoformat()
        
        for dist in distributions:
            try:
                acc = dist["trading_accounts"]
                sig = dist["signals"]
                
                # Fetch user settings to determine position sizing
                us_res = supabase.table("user_settings").select("*").eq("user_id", acc["user_id"]).execute()
                settings = us_res.data[0] if us_res.data else {}
                
                # Skip if symbol is not whitelisted (if whitelist exists)
                whitelist = settings.get("symbol_whitelist", [])
                if whitelist and sig["symbol"] not in whitelist:
                    supabase.table("signal_distributions").update({"status": "skipped", "skip_reason": "not_whitelisted"}).eq("id", dist["id"]).execute()
                    continue

                mode = acc.get("mode", "demo")
                broker = broker_factory.create_broker(
                    mode=mode,
                    enc_api_key=acc.get("binance_api_key_enc"),
                    enc_api_secret=acc.get("binance_api_secret_enc"),
                    is_testnet=acc.get("is_testnet", False)
                )

                # Fetch current market price
                ticker = broker.fetch_ticker(sig["symbol"])
                entry_price = float(ticker.get("last", 0.0))
                if entry_price <= 0:
                    raise ValueError(f"Invalid entry price for {sig['symbol']}")

                # Simple position sizing calculation (can be expanded)
                balance = acc.get("current_balance", 100.0)
                margin_pct = float(settings.get("margin_per_trade_pct", 0.12))
                leverage = int(settings.get("leverage", 20))
                
                margin = balance * margin_pct
                notional = margin * leverage
                qty = notional / entry_price
                
                side = "buy" if sig["direction"] == 1 else "sell"
                
                if mode == "live":
                    broker.set_leverage(sig["symbol"], leverage)
                    # For safety, margin mode could be set here
                    order = broker.place_market_order(sig["symbol"], side, qty)
                    logger.info(f"LIVE Order placed: {order}")
                
                # Calculate SL/TP
                direction_mult = 1 if sig["direction"] == 1 else -1
                atr = float(sig["atr"])
                atr_mult = float(settings.get("atr_mult", 1.4))
                tp_rr = float(settings.get("tp_rr_ratio", 2.0))
                
                sl_dist = atr * atr_mult
                sl_price = entry_price - (sl_dist * direction_mult)
                tp_price = entry_price + (sl_dist * tp_rr * direction_mult)
                
                # Record position
                pos_data = {
                    "trading_account_id": acc["id"],
                    "signal_id": sig["id"],
                    "symbol": sig["symbol"],
                    "direction": sig["direction"],
                    "entry_price": entry_price,
                    "qty": qty,
                    "sl_price": sl_price,
                    "tp_price": tp_price,
                    "atr": atr,
                    "max_price": entry_price,
                    "min_price": entry_price,
                    "signal_name": sig["signal_name"],
                    "strategies": ",".join(sig["strategies"]),
                    "status": "open",
                    "entry_time": now,
                }
                
                pos_table = "positions" if mode == "live" else "demo_trades"
                pos_res = supabase.table(pos_table).insert(pos_data).execute()
                
                if pos_res.data:
                    supabase.table("signal_distributions").update({
                        "status": "executed",
                        "position_id": pos_res.data[0]["id"]
                    }).eq("id", dist["id"]).execute()
                    
            except Exception as e:
                logger.error(f"Failed to process distribution {dist['id']}: {e}")
                supabase.table("signal_distributions").update({
                    "status": "failed",
                    "skip_reason": str(e)
                }).eq("id", dist["id"]).execute()


position_service = PositionService()
