import pandas as pd
import numpy as np
from azalyst.config import BUY, SELL, HOLD

def signal(df: pd.DataFrame) -> int:
    """
    Bollinger Band 200 Trend Continuation Strategy (5m)
    
    Logic:
    1. Breakout: Price closes outside the BB 200 (SD 1.5) band.
    2. Pullback: Price returns to touch or slightly cross the band.
    3. Bounce: Price moves back with momentum (Engulfing or Strong Body).
    """
    
    if "bb200_upper" not in df.columns:
        return HOLD

    if len(df) < 220:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # ── Trend Context ──
    # Long setup: Price above BB 200 mid (EMA/SMA 200 equivalent)
    # Short setup: Price below BB 200 mid
    
    lookback = 15
    full_tail = df.tail(lookback + 5)
    
    # 1. Breakout Check (occurred in the last 15 bars, but not CURRENTLY)
    # We want a recent historical breakout, then a pullback
    had_bull_breakout = any(full_tail["close"].iloc[:-3] > full_tail["bb200_upper"].iloc[:-3])
    had_bear_breakout = any(full_tail["close"].iloc[:-3] < full_tail["bb200_lower"].iloc[:-3])

    # 2. Retest/Pullback Check (within last 3 bars)
    # Price must actually 'kiss' the band within a tight tolerance
    is_retesting_upper = any(full_tail["low"].iloc[-3:] <= full_tail["bb200_upper"].iloc[-3:] * 1.001)
    is_retesting_lower = any(full_tail["high"].iloc[-3:] >= full_tail["bb200_lower"].iloc[-3:] * 0.999)

    # 3. Bounce/Conviction Check
    # Current candle must show strong rejection and high relative volume
    vol_ma = df["volume"].tail(20).mean()
    bullish_bounce = (
        last["close"] > prev["close"] and 
        last["close"] > last["bb200_upper"] and 
        last["volume"] > vol_ma * 1.5
    )
    
    bearish_bounce = (
        last["close"] < prev["close"] and 
        last["close"] < last["bb200_lower"] and 
        last["volume"] > vol_ma * 1.5
    )

    if had_bull_breakout and is_retesting_upper and bullish_bounce:
        return BUY
        
    if had_bear_breakout and is_retesting_lower and bearish_bounce:
        return SELL

    return HOLD
