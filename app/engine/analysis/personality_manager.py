from __future__ import annotations

from dataclasses import dataclass

from app.engine.analysis.regime_detector import MarketRegime


@dataclass
class Personality:
    name: str
    regime: MarketRegime
    weights: dict[str, float]
    atr_mult: float
    tp_rr_ratio: float
    sl_min_pct: float
    sl_max_pct: float
    trailing_enabled: bool
    trail_trigger_pct: float
    trail_distance_pct: float
    max_open_trades: int
    max_same_direction: int
    risk_multiplier: float
    min_agreement: int
    weighted_threshold: float
    directional_bias: int
    scan_limit: int
    leverage: int = 20


_ZERO_WEIGHTS = {
    "bnf": 0.0,
    "nbb": 0.0,
    "kane": 0.0,
    "umar": 0.0,
    "zamco": 0.0,
    "jadecap": 0.0,
    "marci": 0.0,
    "fvg": 0.0,
    "ote": 0.0,
    "cvd_divergence": 0.0,
    "wyckoff": 0.0,
    "cbg": 0.0,
    "bb_trend": 0.0,
    "band_rider": 0.0,
    "liquidity_hunter": 0.0,
    "alpha_x": 0.0,
    "vwap_bounce": 0.0,
    "rsi_divergence": 0.0,
}

PERSONALITIES: dict[MarketRegime, Personality] = {
    MarketRegime.STRONG_UPTREND: Personality(
        name="Momentum Rider",
        regime=MarketRegime.STRONG_UPTREND,
        weights={
            **_ZERO_WEIGHTS,
            "nbb": 5.0,
            "bnf": 5.0,
            "bb_trend": 1.6,
            "umar": 2.8,
        },
        atr_mult=2.5,
        tp_rr_ratio=3.5,
        sl_min_pct=0.02,
        sl_max_pct=0.05,
        trailing_enabled=True,
        trail_trigger_pct=0.04,
        trail_distance_pct=0.035,
        max_open_trades=10,
        max_same_direction=10,
        risk_multiplier=2.5,
        min_agreement=2,
        weighted_threshold=5.0,
        directional_bias=1,
        scan_limit=20,
        leverage=20,
    ),
    MarketRegime.WEAK_UPTREND: Personality(
        name="Cautious Bull",
        regime=MarketRegime.WEAK_UPTREND,
        weights={
            **_ZERO_WEIGHTS,
            "nbb": 5.0,
            "umar": 3.0,
            "jadecap": 3.0,
            "bnf": 4.0,
        },
        atr_mult=2.0,
        tp_rr_ratio=3.0,
        sl_min_pct=0.015,
        sl_max_pct=0.04,
        trailing_enabled=False,
        trail_trigger_pct=0.0,
        trail_distance_pct=0.0,
        max_open_trades=10,
        max_same_direction=10,
        risk_multiplier=0.7,
        min_agreement=2,
        weighted_threshold=5.0,
        directional_bias=1,
        scan_limit=20,
        leverage=20,
    ),
    MarketRegime.SIDEWAYS: Personality(
        name="Range Sniper",
        regime=MarketRegime.SIDEWAYS,
        weights={**_ZERO_WEIGHTS},
        atr_mult=1.2,
        tp_rr_ratio=2.0,
        sl_min_pct=0.015,
        sl_max_pct=0.03,
        trailing_enabled=False,
        trail_trigger_pct=0.0,
        trail_distance_pct=0.0,
        max_open_trades=0,
        max_same_direction=0,
        risk_multiplier=0.0,
        min_agreement=1,
        weighted_threshold=99.0,
        directional_bias=0,
        scan_limit=15,
        leverage=20,
    ),
    MarketRegime.WEAK_DOWNTREND: Personality(
        name="Defensive Bear",
        regime=MarketRegime.WEAK_DOWNTREND,
        weights={
            **_ZERO_WEIGHTS,
            "jadecap": 2.0,
            "jadecap_sweep": 3.0,
            "liquidity_hunter": 3.0,
            "nbb": 3.0,
            "quantx": 3.0,
            "ema5": 2.5,
            "smt_divergence": 2.5,
        },
        atr_mult=1.5,
        tp_rr_ratio=2.5,
        sl_min_pct=0.015,
        sl_max_pct=0.03,
        trailing_enabled=False,
        trail_trigger_pct=0.0,
        trail_distance_pct=0.0,
        max_open_trades=10,
        max_same_direction=10,
        risk_multiplier=0.5,
        min_agreement=1,
        weighted_threshold=5.0,
        directional_bias=-1,
        scan_limit=10,
        leverage=20,
    ),
    MarketRegime.STRONG_DOWNTREND: Personality(
        name="Crisis Alpha",
        regime=MarketRegime.STRONG_DOWNTREND,
        weights={
            **_ZERO_WEIGHTS,
            "quantx": 5.0,
            "ema5": 4.0,
            "smt_divergence": 4.0,
            "jadecap_sweep": 3.0,
        },
        atr_mult=1.8,
        tp_rr_ratio=2.5,
        sl_min_pct=0.015,
        sl_max_pct=0.035,
        trailing_enabled=False,
        trail_trigger_pct=0.0,
        trail_distance_pct=0.0,
        max_open_trades=10,
        max_same_direction=10,
        risk_multiplier=0.8,
        min_agreement=1,
        weighted_threshold=4.0,
        directional_bias=-1,
        scan_limit=15,
        leverage=20,
    ),
}


def get_personality(regime: MarketRegime) -> Personality:
    return PERSONALITIES[regime]


DEFAULT_PERSONALITY = PERSONALITIES[MarketRegime.SIDEWAYS]
