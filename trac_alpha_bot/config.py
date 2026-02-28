import os

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8625731819:AAFBlS3mgOnMF4B6BLuKU3FhmQ8mp_I3UOQ")

# Trac API Endpoint (Polling)
TRAC_RPC_URL = os.getenv("TRAC_RPC_URL", "https://explorer.trac.network/api/transactions")

# Whale Alert Threshold in USD
WHALE_ALERT_USD = float(os.getenv("WHALE_ALERT_USD", "1000"))
