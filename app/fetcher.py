"""Data ingestion layer: calls CoinGecko and normalizes the response."""
import requests
from app import config

API_URL = "https://api.coingecko.com/api/v3/coins/markets"


def normalize(raw):
    """Convert CoinGecko's response into our internal format."""
    out = []
    for c in raw:
        out.append({
            "coin_id": c["id"],
            "symbol": c["symbol"].upper(),
            "name": c.get("name", c["id"]),
            "price": float(c["current_price"] or 0),
            "market_cap": float(c.get("market_cap") or 0),
            "volume": float(c.get("total_volume") or 0),
        })
    return out


def fetch_prices(coin_ids):
    if not coin_ids:
        return []
    headers = {}
    if config.COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = config.COINGECKO_API_KEY
    resp = requests.get(
        API_URL,
        params={"vs_currency": config.CURRENCY, "ids": ",".join(coin_ids)},
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    return normalize(resp.json())
