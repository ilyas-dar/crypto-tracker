import datetime
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, redirect, render_template, request, url_for, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app import config, db, metrics
from app.alerts import run_alerts
from app.fetcher import fetch_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("tracker")


def poll_once():
    """One polling cycle: fetch -> store -> update metrics -> run alerts."""
    coins = db.list_coins()
    metrics.WATCHLIST.set(len(coins))
    if not coins:
        return
    try:
        items = fetch_prices(coins)
    except Exception as exc:
        metrics.POLL_ERRORS.inc()
        log.error("poll failed: %s", exc)
        return
    latest = {}
    for it in items:
        db.save_snapshot(it)
        metrics.PRICE.labels(it["coin_id"]).set(it["price"])
        metrics.VOLUME.labels(it["coin_id"]).set(it["volume"])
        latest[it["coin_id"]] = it
    metrics.POLLS.inc()
    metrics.LAST_POLL.set(time.time())
    for rule_type, _ in run_alerts(latest):
        metrics.ALERTS.labels(rule_type).inc()
    log.info("polled %d coins", len(items))


def create_app(start_scheduler=True):
    app = Flask(__name__)
    db.init_db()
    if not db.list_coins():
        for c in config.DEFAULT_COINS:
            db.add_coin(c)

    @app.after_request
    def count(resp):
        if request.endpoint != "metrics_endpoint":
            metrics.HTTP_REQUESTS.labels(request.method, request.endpoint or "unknown", resp.status_code).inc()
        return resp

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            prices=db.latest_snapshots(),
            coins=db.list_coins(),
            rules=db.list_rules(),
            alerts=db.list_alerts(),
            interval=config.POLL_INTERVAL,
            currency=config.CURRENCY.upper(),
        )

    @app.route("/watch", methods=["POST"])
    def watch():
        coin = request.form.get("coin", "").strip()
        if coin:
            db.add_coin(coin)
            poll_once()
        return redirect(url_for("index"))

    @app.route("/unwatch/<coin>", methods=["POST"])
    def unwatch(coin):
        db.remove_coin(coin)
        return redirect(url_for("index"))

    @app.route("/rules", methods=["POST"])
    def add_rule():
        f = request.form
        db.add_rule(f["coin"], f["rule_type"], float(f["value"]), int(f.get("window_min") or 60))
        return redirect(url_for("index"))

    @app.route("/rules/<int:rule_id>/delete", methods=["POST"])
    def delete_rule(rule_id):
        db.delete_rule(rule_id)
        return redirect(url_for("index"))

    @app.route("/api/prices")
    def api_prices():
        return jsonify(db.latest_snapshots())

    @app.route("/api/history/<coin>")
    def api_history(coin):
        return jsonify(db.get_history(coin))

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/metrics")
    def metrics_endpoint():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    if start_scheduler:
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(poll_once, "interval", seconds=config.POLL_INTERVAL,
                      next_run_time=datetime.datetime.now(), id="poll", max_instances=1)
        sched.start()
    return app

