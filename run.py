from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
import ccxt

from azalyst.config import LEVERAGE
from azalyst.logger import logger
from azalyst.trader import LiveTrader
from azalyst import db


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Azalyst Alpha X — Multi Strategy Live Trader")
    parser.add_argument("--dry-run", action="store_true", help="Force paper trading mode")
    parser.add_argument("--dashboard", action="store_true", default=True, help="Launch web dashboard")
    parser.add_argument("--no-dashboard", action="store_true", help="Disable web dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port")

    args = parser.parse_args()

    # Find the active user (the one who has setup the bot)
    # If no user set, we wait for a dashboard setup
    active_user_id = None
    client = db.get_client()
    try:
        res = client.table("bot_config").select("user_id").eq("key", "trading_mode").limit(1).execute()
        if res.data:
            active_user_id = res.data[0].get("user_id")
    except Exception as e:
         logger.error(f"Failed to check bot configuration: {e}")

    trading_mode = ""
    if active_user_id:
        trading_mode = db.get_config(active_user_id, "trading_mode", "")

    if args.dry_run:
        trading_mode = "dry_run"

    exchange_config = {
        "enableRateLimit": True,
        "options": {
            "defaultType": "future",
        },
    }

    dry_run = True
    if trading_mode == "live" and active_user_id:
        api_key = db.get_config(active_user_id, "binance_api_key", os.getenv("BINANCE_API_KEY", ""))
        api_secret = db.get_config(active_user_id, "binance_api_secret", os.getenv("BINANCE_API_SECRET", ""))
        if api_key and api_secret:
            exchange_config["apiKey"] = api_key
            exchange_config["secret"] = api_secret
            dry_run = False
            logger.info(f"Operating in LIVE TRADING mode for user {active_user_id}")
        else:
            logger.warn("Live mode selected but no API keys found. Falling back to dry run.")
    elif trading_mode == "dry_run" and active_user_id:
        logger.info(f"Operating in Signal-Only Mode for user {active_user_id}")
    else:
        logger.info("No active user configuration found. Bot will wait for setup via dashboard.")

    exchange = ccxt.binance(exchange_config)
    # We pass None for user_id initially if not found, it will be set during reconfigure/setup
    trader = LiveTrader(exchange, user_id=active_user_id, dry_run=dry_run)

    if args.dashboard and not args.no_dashboard:
        from dashboard.server import start_dashboard
        start_dashboard(trader, port=args.port)
        if not trading_mode:
            logger.info(f"Open http://localhost:{args.port}/auth/signup to create an account and select trading mode")
        else:
            logger.info(f"Dashboard running at http://localhost:{args.port}")

    if not trading_mode and not args.dry_run:
        logger.info("Waiting for configuration...")
        import time
        while not trader.user_id or not db.get_config(trader.user_id, "trading_mode", ""):
            time.sleep(2)
        
        # After setup, re-detect settings
        trading_mode = db.get_config(trader.user_id, "trading_mode", "")
        # The reconfigure method will handle the actual exchange/dry_run update
        logger.info(f"Configuration received for user {trader.user_id}. Starting trader...")

    trader.run()


if __name__ == "__main__":
    main()
