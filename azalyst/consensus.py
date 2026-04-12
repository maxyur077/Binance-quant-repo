from typing import Optional

import numpy as np
import pandas as pd

from azalyst.config import (
    BUY, SELL, MIN_AGREEMENT, WEIGHTED_THRESHOLD, MULTI_WEIGHTS,
)
from azalyst.strategies import MULTI_STRATEGIES
from azalyst.strategies.htf_filter import get_htf_trend


def multi_strategy_scan(df: pd.DataFrame, htf_df: Optional[pd.DataFrame] = None) -> Optional[dict]:
    if len(df) < 200:
        return None
        
    htf_trend = 0
    if htf_df is not None and not htf_df.empty:
        htf_trend = get_htf_trend(htf_df)

    buy_count = 0
    sell_count = 0
    buy_weight = 0.0
    sell_weight = 0.0
    buy_strategies = []
    sell_strategies = []

    for name, func in MULTI_STRATEGIES.items():
        sig = func(df)
        weight = MULTI_WEIGHTS.get(name, 1.0)

        if sig == BUY:
            # HTF Filter: Ignore long signals if macro trend is bearish
            if htf_trend == -1:
                continue
            buy_count += 1
            buy_weight += weight
            buy_strategies.append(name)
        elif sig == SELL:
             # HTF Filter: Ignore short signals if macro trend is bullish
            if htf_trend == 1:
                continue
            sell_count += 1
            sell_weight += weight
            sell_strategies.append(name)

    atr_val = df["atr_14"].iloc[-1]
    if np.isnan(atr_val) or atr_val <= 0:
        return None

    if buy_count >= MIN_AGREEMENT and buy_weight >= WEIGHTED_THRESHOLD and buy_count > sell_count:
        return {
            "direction": BUY,
            "atr": float(atr_val),
            "signal": f"CONSENSUS({buy_count} agree, w={buy_weight:.1f})",
            "strategies": buy_strategies,
        }

    if sell_count >= MIN_AGREEMENT and sell_weight >= WEIGHTED_THRESHOLD and sell_count > buy_count:
        return {
            "direction": SELL,
            "atr": float(atr_val),
            "signal": f"CONSENSUS({sell_count} agree, w={sell_weight:.1f})",
            "strategies": sell_strategies,
        }

    return None
