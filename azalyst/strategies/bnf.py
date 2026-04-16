import pandas as pd

from azalyst.config import BUY, SELL, HOLD


def signal(df: pd.DataFrame) -> int:
    if len(df) < 200:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.5 if vol_ma > 0 else True

    # ── RSI Rejection Rule ──
    if last["rsi_9"] < 30: # More oversold for higher conviction
        # Must be touching the band
        at_bb_lower = last["low"] <= last["bb_lower"]
        below_vwap = last["close"] < last.get("vwap", last["close"])
        above_ema200 = last["close"] > ema_200
        
        # Bullish Rejection candle (e.g. Hammer or recovery)
        rejection = last["close"] > last["open"] or last["close"] > prev["close"]

        if at_bb_lower and below_vwap and above_ema200 and rejection and high_conviction_vol:
            return BUY

    if last["rsi_9"] > 70: # More overbought
        at_bb_upper = last["high"] >= last["bb_upper"]
        above_vwap = last["close"] > last.get("vwap", last["close"])
        below_ema200 = last["close"] < ema_200
        
        rejection = last["close"] < last["open"] or last["close"] < prev["close"]

        if at_bb_upper and above_vwap and below_ema200 and rejection and high_conviction_vol:
            return SELL

    return HOLD
