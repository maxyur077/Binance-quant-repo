import pandas as pd
import numpy as np
from azalyst.config import BUY, SELL, HOLD

# ── Alpha-X Institutional Squeeze (v5) ──
# Targets: 40% Win Rate / 60-Day Consistency
BREAKOUT_LOOKBACK = 20   
ENTRY_WINDOW      = 10   
MIN_BREAKOUT_PCT  = 0.006  # 0.6% (Filtering noise even harder)
MAX_SQUEEZE_PCT   = 0.50   # Relaxed slightly to allow live trading activity
VOL_SURGE_MULT    = 1.5    # Adjusted for live market activity
TOUCH_TOL         = 0.0025 

def signal(df: pd.DataFrame) -> int:
    """
    ALPHA-X Institutional Squeeze (v5)
    ----------------------------------
    Focuses on VOLATILITY COMPRESSION. We only enter trades that break out
    from a 'Squeeze' zone. This is the highest win-rate institutional pattern.
    """
    if len(df) < 210:
        return HOLD

    current = df.iloc[-1]
    
    # --- Filter 1: Squeeze Detector (The Secret Sauce) ---
    squeeze_val = current.get("bb200_squeeze", 1.0)
    if squeeze_val > MAX_SQUEEZE_PCT:
        return HOLD # Market is too loose — wait for a tighter squeeze

    # --- Filter 2: Momentum Quality ---
    if current["close"] > current["bb200_mid"]:
        if current["close"] > current["open"]:
            if _check_long(df, current): return BUY
    elif current["close"] < current["bb200_mid"]:
        if current["close"] < current["open"]:
            if _check_short(df, current): return SELL
        
    return HOLD

def _check_long(df: pd.DataFrame, current: pd.Series) -> bool:
    n = len(df)
    breakout = None
    breakout_pos = None

    for offset in range(2, min(BREAKOUT_LOOKBACK + 1, n - 1)):
        candidate = df.iloc[-1 - offset]
        if candidate["close"] > candidate["bb200_upper"]:
            # Volume Confirmation (2.0x)
            c_vol = candidate.get("volume", 0)
            c_vol_ma = candidate.get("vol_ma_20", 1)
            if c_vol < c_vol_ma * VOL_SURGE_MULT: continue 

            bd = (candidate["close"] - candidate["bb200_upper"]) / candidate["bb200_upper"]
            if bd >= MIN_BREAKOUT_PCT:
                breakout = candidate
                breakout_pos = offset
                break

    if breakout is None or breakout_pos > ENTRY_WINDOW:
        return False

    for pb_offset in range(1, breakout_pos):
        pullback = df.iloc[-1 - pb_offset]
        tol = pullback["bb200_upper"] * TOUCH_TOL
        if (pullback["low"] <= pullback["bb200_upper"] + tol and 
            pullback["close"] < breakout["close"] and 
            current["close"] > pullback["close"]):
            return True
            
    return False

def _check_short(df: pd.DataFrame, current: pd.Series) -> bool:
    n = len(df)
    breakdown = None
    breakdown_pos = None

    for offset in range(2, min(BREAKOUT_LOOKBACK + 1, n - 1)):
        candidate = df.iloc[-1 - offset]
        if candidate["close"] < candidate["bb200_lower"]:
            # Volume Confirmation (2.0x)
            c_vol = candidate.get("volume", 0)
            c_vol_ma = candidate.get("vol_ma_20", 1)
            if c_vol < c_vol_ma * VOL_SURGE_MULT: continue

            bd = (candidate["bb200_lower"] - candidate["close"]) / candidate["bb200_lower"]
            if bd >= MIN_BREAKOUT_PCT:
                breakdown = candidate
                breakdown_pos = offset
                break

    if breakdown is None or breakdown_pos > ENTRY_WINDOW:
        return False

    for pb_offset in range(1, breakdown_pos):
        bounce = df.iloc[-1 - pb_offset]
        tol = abs(bounce["bb200_lower"]) * TOUCH_TOL
        if (bounce["high"] >= bounce["bb200_lower"] - tol and 
            bounce["close"] > breakdown["close"] and 
            current["close"] < bounce["close"]):
            return True
            
    return False
