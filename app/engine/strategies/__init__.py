from __future__ import annotations

from typing import Dict, Type
from app.engine.strategies.base_strategy import BaseStrategy

from .alpha_x import AlphaXStrategy
from .band_rider import BandRiderStrategy
from .bb_trend import BbTrendStrategy
from .bnf import BnfStrategy
from .cbg import CbgStrategy
from .cvd_divergence import CvdDivergenceStrategy
from .ema5 import Ema5Strategy
from .fvg import FvgStrategy
from .htf_filter import get_htf_trend
from .jadecap import JadecapStrategy
from .jadecap_sweep import JadecapSweepStrategy
from .kane import KaneStrategy
from .liquidity_hunter import LiquidityHunterStrategy
from .marci import MarciStrategy
from .nbb import NbbStrategy
from .ote import OteStrategy
from .quantx import QuantxStrategy
from .rsi_divergence import RsiDivergenceStrategy
from .smt_divergence import SmtDivergenceStrategy
from .umar import UmarStrategy
from .vwap_bounce import VwapBounceStrategy
from .wyckoff import WyckoffStrategy
from .zamco import ZamcoStrategy

MULTI_STRATEGIES: Dict[str, BaseStrategy] = {
    "zamco": ZamcoStrategy(),
    "bnf": BnfStrategy(),
    "jadecap": JadecapStrategy(),
    "marci": MarciStrategy(),
    "nbb": NbbStrategy(),
    "umar": UmarStrategy(),
    "kane": KaneStrategy(),
    "fvg": FvgStrategy(),
    "ote": OteStrategy(),
    "cvd_divergence": CvdDivergenceStrategy(),
    "wyckoff": WyckoffStrategy(),
    "cbg": CbgStrategy(),
    "bb_trend": BbTrendStrategy(),
    "band_rider": BandRiderStrategy(),
    "liquidity_hunter": LiquidityHunterStrategy(),
    "alpha_x": AlphaXStrategy(),
    "vwap_bounce": VwapBounceStrategy(),
    "rsi_divergence": RsiDivergenceStrategy(),
    "quantx": QuantxStrategy(),
    "ema5": Ema5Strategy(),
    "smt_divergence": SmtDivergenceStrategy(),
    "jadecap_sweep": JadecapSweepStrategy(),
}

__all__ = ["MULTI_STRATEGIES", "BaseStrategy", "get_htf_trend"]
