from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone


def setup_logger(name: str = "azalyst") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S UTC"
        )
        # Hack to enforce UTC for standard logging formatter
        formatter.converter = lambda *args: datetime.now(timezone.utc).timetuple()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


trade_logger = setup_logger("trade_logger")


class TradeLogger:
    """Wrapper to maintain backwards compatibility with existing engine code style."""
    @staticmethod
    def info(msg: str) -> None:
        trade_logger.info(msg)

    @staticmethod
    def warn(msg: str) -> None:
        trade_logger.warning(msg)
        
    @staticmethod
    def warning(msg: str) -> None:
        trade_logger.warning(msg)

    @staticmethod
    def error(msg: str) -> None:
        trade_logger.error(msg)

    @staticmethod
    def trade(msg: str) -> None:
        # Custom level behavior can be expanded later
        trade_logger.info(f"[TRADE] {msg}")


logger = TradeLogger()
