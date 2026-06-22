from __future__ import annotations

import ccxt

from app.engine.brokers.base_broker import BaseBroker
from app.engine.brokers.demo_broker import DemoBroker
from app.engine.brokers.live_binance_broker import LiveBinanceBroker
from app.security.encryption_handler import decrypt


class BrokerFactory:
    @staticmethod
    def create_broker(
        mode: str, 
        enc_api_key: str | None = None, 
        enc_api_secret: str | None = None, 
        is_testnet: bool = False
    ) -> BaseBroker:
        if mode == "demo" or not enc_api_key or not enc_api_secret:
            exchange = ccxt.binanceusdm()
            return DemoBroker(exchange)

        api_key = decrypt(enc_api_key)
        api_secret = decrypt(enc_api_secret)

        return LiveBinanceBroker(api_key=api_key, api_secret=api_secret, testnet=is_testnet)


broker_factory = BrokerFactory()
