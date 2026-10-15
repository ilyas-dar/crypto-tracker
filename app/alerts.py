"""Alert engine. evaluate_rule() is a pure function so it is easy to unit test."""
import time
from app import db, config
from app.notifier import notify


def evaluate_rule(rule, current, past=None, now=None, cooldown_min=None):
    """Return an alert message if the rule fires, otherwise None.

    rule    : dict with rule_type, value, window_min, last_triggered, coin_id
    current : dict with price, volume
    past    : dict with price, volume from `window_min` ago (or None)
    """
    now = now or time.time()
    cooldown_min = config.ALERT_COOLDOWN_MIN if cooldown_min is None else cooldown_min
    if now - (rule.get("last_triggered") or 0) < cooldown_min * 60:
        return None

    rtype, value, coin = rule["rule_type"], rule["value"], rule["coin_id"]

    if rtype == "price_above" and current["price"] > value:
        return f"{coin}: price {current['price']:.2f} is ABOVE {value:.2f}"
    if rtype == "price_below" and current["price"] < value:
        return f"{coin}: price {current['price']:.2f} is BELOW {value:.2f}"

    if rtype == "pct_change" and past and past["price"]:
        change = (current["price"] - past["price"]) / past["price"] * 100
        if abs(change) >= value:
            return f"{coin}: price moved {change:+.2f}% in {rule['window_min']} min (limit {value}%)"

    if rtype == "volume_spike" and past and past["volume"]:
        change = (current["volume"] - past["volume"]) / past["volume"] * 100
        if change >= value:
            return f"{coin}: volume up {change:+.2f}% in {rule['window_min']} min (limit {value}%)"

    return None


def run_alerts(latest_by_coin):
    """Evaluate every active rule against the newest prices."""
    fired = []
    for rule in db.list_rules():
        if not rule["active"]:
            continue
        current = latest_by_coin.get(rule["coin_id"])
        if not current:
            continue
        past = db.get_past_snapshot(rule["coin_id"], rule["window_min"])
        msg = evaluate_rule(rule, current, past)
        if msg:
            db.mark_triggered(rule["id"])
            db.log_alert(rule["id"],rule["coin_id"], msg)
            notify(msg)
            fired.append((rule["rule_type"], msg))
    return fired
