from app.alerts import evaluate_rule

NOW = 1_000_000.0


def rule(rtype, value, window=60):
    return {"coin_id": "bitcoin", "rule_type": rtype, "value": value,
            "window_min": window, "last_triggered": 0}


def test_price_above_fires():
    assert evaluate_rule(rule("price_above", 100), {"price": 120, "volume": 1}, now=NOW)


def test_price_above_quiet():
    assert evaluate_rule(rule("price_above", 100), {"price": 90, "volume": 1}, now=NOW) is None


def test_price_below_fires():
    assert evaluate_rule(rule("price_below", 100), {"price": 90, "volume": 1}, now=NOW)


def test_pct_change_fires_on_drop():
    msg = evaluate_rule(rule("pct_change", 5), {"price": 90, "volume": 1},
                        past={"price": 100, "volume": 1}, now=NOW)
    assert msg and "-10.00%" in msg


def test_pct_change_needs_history():
    assert evaluate_rule(rule("pct_change", 5), {"price": 90, "volume": 1}, past=None, now=NOW) is None


def test_volume_spike_fires():
    msg = evaluate_rule(rule("volume_spike", 20), {"price": 1, "volume": 150},
                        past={"price": 1, "volume": 100}, now=NOW)
    assert msg and "+50.00%" in msg


def test_cooldown_blocks_repeat():
    r = rule("price_above", 100)
    r["last_triggered"] = NOW - 10
    assert evaluate_rule(r, {"price": 120, "volume": 1}, now=NOW, cooldown_min=5) is None
