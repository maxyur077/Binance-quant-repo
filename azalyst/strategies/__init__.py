from azalyst.strategies import zamco, bnf, jadecap, marci, nbb, umar, kane
from azalyst.strategies import fvg, ote, cvd_divergence, wyckoff

MULTI_STRATEGIES = {
    "zamco": zamco.signal,
    "bnf": bnf.signal,
    "jadecap": jadecap.signal,
    "marci": marci.signal,
    "nbb": nbb.signal,
    "umar": umar.signal,
    "kane": kane.signal,
    "fvg": fvg.signal,
    "ote": ote.signal,
    "cvd_divergence": cvd_divergence.signal,
    "wyckoff": wyckoff.signal,
}
