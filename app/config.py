import os

DB_PATH = os.getenv("DB_PATH", "data/tracker.db")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))          # seconds
CURRENCY = os.getenv("CURRENCY", "usd")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")           # optional
ALERT_COOLDOWN_MIN = int(os.getenv("ALERT_COOLDOWN_MIN", "5"))
DEFAULT_COINS = os.getenv("DEFAULT_COINS", "bitcoin,ethereum,solana").split(",")

# Optional notification channels (console is always on)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")
