import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TRAC_RPC_URL = os.getenv("TRAC_RPC_URL", "")
WHALE_ALERT_USD = float(os.getenv("WHALE_ALERT_USD", "10000"))
