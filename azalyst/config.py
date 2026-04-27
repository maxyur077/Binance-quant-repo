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
LEVERAGE = 15
RISK_PER_TRADE = 0.08          # Boosted for Precision Strike
ATR_MULT = 4.0           # Max room for 45% Win Rate
TP_RR_RATIO = 2.0           
# RESTORED for $300+ Profit
SL_MIN_PCT = 0.01
SL_MAX_PCT = 0.05
MAX_OPEN_TRADES = 10
MAX_HOLD_SCANS = 48
BREAKEVEN_AFTER_SCANS = 10     # Middle ground: allows breath but protects wins
SCAN_INTERVAL_MIN = 5        # Alpha-X 15m Scan (Binance Support)
CANDLE_TF_MIN = 15              # Alpha-X 15m Candle (Binance Support)

PROP_MAX_DRAWDOWN_PCT = 50.0
PROP_DAILY_LOSS_PCT = 25.0

TAKER_FEE = 0.0004
SLIPPAGE_BPS = 1.0

MIN_AGREEMENT = 2               # Requires 2 strategies to agree
WEIGHTED_THRESHOLD = 5.5       # Precision Volume trigger

BUY = 1
SELL = -1
HOLD = 0

MULTI_WEIGHTS = {
    "bnf": 1.0,
    "nbb": 1.0,            # Reduced (lower accuracy)
    "kane": 0.5,
    "umar": 2.2,             
    "zamco": 0.5,
    "jadecap": 0.5,
    "marci": 0.1,          
    "fvg": 3.0,              # MASTER STRATEGY (100% Accuracy)
    "ote": 1.0,
    "cvd_divergence": 0.5,
    "wyckoff": 2.5,
    "cbg": 0.1,            
    "bb_trend": 2.2,         
    "band_rider": 2.5,       
    "liquidity_hunter": 1.0, 
    "alpha_x": 0.1,        
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
MIN_VOLUME_MA = 70000
TOP_N_COINS = 20

ORDER_CAP_TIERS = [
    (30,   5),
    (500, 10),
]

TRAILING_STOP_ENABLED = False
