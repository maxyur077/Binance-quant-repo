from __future__ import annotations

from .indicator_engine import compute_indicators
from .regime_detector import detect, MarketRegime, reset_regime_state
from .personality_manager import Personality, get_personality, DEFAULT_PERSONALITY
from .candlestick_patterns import is_bullish_engulfing, is_bearish_engulfing, is_hammer, is_inverted_hammer

__all__ = [
    "compute_indicators",
    "detect",
    "MarketRegime",
    "reset_regime_state",
    "Personality",
    "get_personality",
    "DEFAULT_PERSONALITY",
    "is_bullish_engulfing",
    "is_bearish_engulfing",
    "is_hammer",
    "is_inverted_hammer",
]
