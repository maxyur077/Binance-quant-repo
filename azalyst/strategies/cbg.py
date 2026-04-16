import pandas as pd

from azalyst.config import BUY, SELL, HOLD

def signal(df: pd.DataFrame) -> int:
    """
    CBG Swing High Low MA Strategy
    Green Bar (BUY): Price > EMA50 and a 5-candle Swing Low is confirmed.
    Red Bar (SELL): Price < EMA50 and a 5-candle Swing High is confirmed.
    """
    # Need at least 5 candles to form a fractal, plus EMA 50
    if len(df) < 50:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    # High conviction volume for breakout rejection
    high_conviction_vol = last["volume"] > vol_ma * 1.3 if vol_ma > 0 else True

    # ── Trend & Momentum Filter ──
    # RSI Correlated Momentum: We only buy if RSI is in the Bullish Power Zone (>50)
    rsi_bullish = last["rsi_14"] > 50 and last["rsi_14"] > prev["rsi_14"]
    rsi_bearish = last["rsi_14"] < 50 and last["rsi_14"] < prev["rsi_14"]

    trend_up = last["close"] > last["ema_50"] and last["close"] > ema_200
    trend_down = last["close"] < last["ema_50"] and last["close"] < ema_200
    
    # ── Fractal (Swing) Detection ──
    # A true 5-candle non-repainting fractal swing evaluates the middle candle (t-2).
    low_t0 = df["low"].iloc[-1]
    low_t1 = df["low"].iloc[-2]
    low_t2 = df["low"].iloc[-3]  # The pivot
    low_t3 = df["low"].iloc[-4]
    low_t4 = df["low"].iloc[-5]
    
    high_t0 = df["high"].iloc[-1]
    high_t1 = df["high"].iloc[-2]
    high_t2 = df["high"].iloc[-3] # The pivot
    high_t3 = df["high"].iloc[-4]
    high_t4 = df["high"].iloc[-5]
    
    swing_low_formed = (low_t2 < low_t1) and (low_t2 <= low_t0) and (low_t2 < low_t3) and (low_t2 <= low_t4)
    swing_high_formed = (high_t2 > high_t1) and (high_t2 >= high_t0) and (high_t2 > high_t3) and (high_t2 >= high_t4)
    
    # ── Signal Generation ──
    if trend_up and swing_low_formed and rsi_bullish and high_conviction_vol:
        return BUY
        
    if trend_down and swing_high_formed and rsi_bearish and high_conviction_vol:
        return SELL
        
    # Transcript equivalent: "orange bars and that's when we should stay out"
    return HOLD
