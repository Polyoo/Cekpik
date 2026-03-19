import os
from dotenv import load_dotenv

load_dotenv()

# ── MODE ─────────────────────────────
DRY_RUN = False
SCAN_INTERVAL = 15

# ── MARKETS ──────────────────────────
ASSETS = {
    "btc": "BTCUSDT",
    "eth": "ETHUSDT",
    "sol": "SOLUSDT",
    "xrp": "XRPUSDT",
}

# ── BANKROLL ─────────────────────────
BANKROLL = 29.0

# ── POSITION ─────────────────────────
CONVICTION_SHARES = 3.0

MAX_POSITIONS = 20
MAX_EXPOSURE_PCT = 0.85
MAX_DRAWDOWN_PCT = 0.35

# ── API (SECURE) ─────────────────────
PRIVATE_KEY    = os.getenv("PRIVATE_KEY")
API_KEY        = os.getenv("API_KEY")
API_SECRET     = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("API_PASSPHRASE")

CLOB_URL = "https://clob.polymarket.com"

# ── TELEGRAM ─────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
