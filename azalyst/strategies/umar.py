import pandas as pd

from azalyst.config import BUY, SELL, HOLD


def signal(df: pd.DataFrame) -> int:
    if len(df) < 25:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.5 if vol_ma > 0 else True

    # ── Day Range Breakout ──
    # Uses 24-period (e.g. 2 hours on 5m) as a 'Session' high/low proxy
    day_high = df["high"].tail(24).iloc[:-1].max()
    day_low = df["low"].tail(24).iloc[:-1].min()

    # Long: Price breaks above today's high with conviction
    if last["close"] > day_high:
        above_vwap = last["close"] > last.get("vwap", last["close"])
        ema_bullish = last["ema_9"] > last["ema_21"] and last["close"] > ema_200

        if above_vwap and ema_bullish and high_conviction_vol:
            # Entry on the breakout candle's strength
            if last["close"] > last["open"] and (last["close"] - last["open"]) > 0.5 * (last["high"] - last["low"]):
                return BUY

    # Short: Price breaks below today's low with conviction
    if last["close"] < day_low:
        below_vwap = last["close"] < last.get("vwap", last["close"])
        ema_bearish = last["ema_9"] < last["ema_21"] and last["close"] < ema_200

        if below_vwap and ema_bearish and high_conviction_vol:
            if last["close"] < last["open"] and (last["open"] - last["close"]) > 0.5 * (last["high"] - last["low"]):
                return SELL

    return HOLD
