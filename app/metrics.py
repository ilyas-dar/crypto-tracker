"""Prometheus metrics exposed at /metrics."""
from prometheus_client import Counter, Gauge

PRICE = Gauge("crypto_price", "Latest price of a coin", ["coin"])
VOLUME = Gauge("crypto_volume", "Latest 24h volume of a coin", ["coin"])
POLLS = Counter("crypto_polls_total", "Number of successful API polls")
POLL_ERRORS = Counter("crypto_poll_errors_total", "Number of failed API polls")
LAST_POLL = Gauge("crypto_last_poll_timestamp", "Unix time of last successful poll")
ALERTS = Counter("crypto_alerts_triggered_total", "Alerts fired", ["rule_type"])
WATCHLIST = Gauge("crypto_watchlist_size", "Coins on the watchlist")
HTTP_REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "endpoint", "status"])
