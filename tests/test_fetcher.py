from unittest.mock import patch, Mock
from app import fetcher

SAMPLE = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin",
           "current_price": 60000, "market_cap": 1.2e12, "total_volume": 3e10}]


def test_normalize():
    out = fetcher.normalize(SAMPLE)
    assert out[0]["symbol"] == "BTC" and out[0]["price"] == 60000.0


def test_fetch_prices_uses_mocked_api():
    resp = Mock()
    resp.json.return_value = SAMPLE
    resp.raise_for_status.return_value = None
    with patch("app.fetcher.requests.get", return_value=resp) as g:
        out = fetcher.fetch_prices(["bitcoin"])
    assert g.called and out[0]["coin_id"] == "bitcoin"


def test_fetch_prices_empty_list():
    assert fetcher.fetch_prices([]) == []
