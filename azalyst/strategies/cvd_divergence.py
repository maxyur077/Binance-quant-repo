import pandas as pd

from azalyst.config import BUY, SELL, HOLD

def signal(df: pd.DataFrame) -> int:
    if len(df) < 20 or "cvd" not in df.columns:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    atr = last.get("atr_14", 0)
    # Institutional divergence requires extreme volume exhaustion
    high_conviction_vol = last["volume"] > vol_ma * 2.0 if vol_ma > 0 else True

    # ── Divergence Engine (20-period lookback) ──
    recent_price_lows = df["low"].tail(10).min()
    prev_price_lows = df["low"].iloc[-21:-11].min()
    
    recent_cvd_lows = df["cvd"].tail(10).min()
    prev_cvd_lows = df["cvd"].iloc[-21:-11].min()

    # Bullish Divergence: Price making lower lows, but CVD making higher lows (Exhaustion)
    if recent_price_lows < prev_price_lows and recent_cvd_lows > prev_cvd_lows:
        # RSI must show recent oversold conditions to prove exhaustion
        oversold = df["rsi_14"].tail(10).min() < 35
        # Must be significantly below EMA 200 (stretched)
        is_stretched = last["close"] < (ema_200 - 1.0 * atr)
        if last["close"] > last["ema_9"] and last["close"] > ema_200 and oversold and is_stretched:
            if high_conviction_vol:
                return BUY
            
    recent_price_highs = df["high"].tail(10).max()
    prev_price_highs = df["high"].iloc[-21:-11].max()
    
    recent_cvd_highs = df["cvd"].tail(10).max()
    prev_cvd_highs = df["cvd"].iloc[-21:-11].max()

    # Bearish Divergence: Price making higher highs, but CVD making lower highs
    if recent_price_highs > prev_price_highs and recent_cvd_highs < prev_cvd_highs:
        # RSI must show recent overbought conditions to prove exhaustion
        overbought = df["rsi_14"].tail(10).max() > 65
        # Must be significantly above EMA 200 (stretched)
        is_stretched = last["close"] > (ema_200 + 1.0 * atr)
        if last["close"] < last["ema_9"] and last["close"] < ema_200 and overbought and is_stretched:
            if high_conviction_vol:
                return SELL

    return HOLD
