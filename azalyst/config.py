import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

INITIAL_BALANCE = 100.0
LEVERAGE = 10
RISK_PER_TRADE = 0.10
ATR_MULT = 1.2
TP_RR_RATIO = 1.8              # BALANCED config — proven profitable in backtest
SL_MIN_PCT = 0.01
SL_MAX_PCT = 0.03
MAX_OPEN_TRADES = 10
MAX_HOLD_SCANS = 24
BREAKEVEN_AFTER_SCANS = 8       # Delayed from 4 to reduce fee-drain breakeven exits
SCAN_INTERVAL_MIN = 30
CANDLE_TF_MIN = 15

PROP_MAX_DRAWDOWN_PCT = 50.0
PROP_DAILY_LOSS_PCT = 25.0

TAKER_FEE = 0.0004
SLIPPAGE_BPS = 1.0

MIN_AGREEMENT = 3
WEIGHTED_THRESHOLD = 2.5

BUY = 1
SELL = -1
HOLD = 0

MULTI_WEIGHTS = {
    "bnf": 0.5,             # Almost never fires — reduce weight
    "nbb": 1.5,             # Marginal performer — slight reduce
    "kane": 1.0,
    "umar": 1.2,
    "zamco": 0.5,           # 11.8% win rate with 3-agree — nerf
    "jadecap": 1.5,         # Profitable in BALANCED — boost
    "marci": 1.0,
    "fvg": 1.0,             # Good but was overvoted at 2.0
    "ote": 1.2,             # Slight reduce from 1.5
    "cvd_divergence": 0.5,  # 20.3% win rate — heavily nerf
    "wyckoff": 2.5,         # BEST strategy (+$25) — boost
}

HTF_TIMEFRAME = "4h"
HTF_CANDLE_LIMIT = 200
HTF_EMA_FAST = 50
HTF_EMA_SLOW = 200

MAX_SAME_DIRECTION = 5

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

EXCLUDE_SYMBOLS = {
    "USDCUSDT", "TUSDUSDT", "USDPUSDT", "EURUSDT", "FDUSDUSDT",
    "DAIUSDT", "BUSDUSDT", "PAXGUSDT", "USDDUSDT",
}
MIN_VOLUME_MA = 75_000
TOP_N_COINS = 100
