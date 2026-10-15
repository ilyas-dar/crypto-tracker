"""Storage layer (SQLite)."""
import os
import sqlite3
import time
from app import config


def _conn():
    os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS watchlist (
            coin_id TEXT PRIMARY KEY
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            symbol TEXT,
            price REAL, market_cap REAL, volume REAL,
            ts REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_snap ON snapshots(coin_id, ts);
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            rule_type TEXT NOT NULL,
            value REAL NOT NULL,
            window_min INTEGER DEFAULT 60,
            active INTEGER DEFAULT 1,
            last_triggered REAL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER, coin_id TEXT, message TEXT, ts REAL
        );
        """)


# ---- watchlist ----
def add_coin(coin_id):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO watchlist(coin_id) VALUES (?)", (coin_id.lower().strip(),))


def remove_coin(coin_id):
    with _conn() as c:
        c.execute("DELETE FROM watchlist WHERE coin_id=?", (coin_id,))


def list_coins():
    with _conn() as c:
        return [r["coin_id"] for r in c.execute("SELECT coin_id FROM watchlist ORDER BY coin_id")]


# ---- snapshots ----
def save_snapshot(item, ts=None):
    with _conn() as c:
        c.execute(
            "INSERT INTO snapshots(coin_id,symbol,price,market_cap,volume,ts) VALUES (?,?,?,?,?,?)",
            (item["coin_id"], item["symbol"], item["price"], item["market_cap"], item["volume"], ts or time.time()),
        )


def latest_snapshots():
    with _conn() as c:
        rows = c.execute("""
            SELECT s.* FROM snapshots s
            JOIN (SELECT coin_id, MAX(ts) m FROM snapshots GROUP BY coin_id) x
              ON s.coin_id = x.coin_id AND s.ts = x.m
            WHERE s.coin_id IN (SELECT coin_id FROM watchlist)
            ORDER BY s.coin_id""").fetchall()
        return [dict(r) for r in rows]


def get_history(coin_id, limit=100):
    with _conn() as c:
        rows = c.execute(
            "SELECT price, volume, ts FROM snapshots WHERE coin_id=? ORDER BY ts DESC LIMIT ?",
            (coin_id, limit)).fetchall()
        return [dict(r) for r in reversed(rows)]


def get_past_snapshot(coin_id, minutes_ago):
    """Oldest snapshot inside the window (used for % change / volume spike)."""
    since = time.time() - minutes_ago * 60
    with _conn() as c:
        r = c.execute(
            "SELECT price, volume, ts FROM snapshots WHERE coin_id=? AND ts>=? ORDER BY ts ASC LIMIT 1",
            (coin_id, since)).fetchone()
        return dict(r) if r else None


# ---- rules ----
def add_rule(coin_id, rule_type, value, window_min=60):
    with _conn() as c:
        c.execute("INSERT INTO rules(coin_id,rule_type,value,window_min) VALUES (?,?,?,?)",
                  (coin_id.lower().strip(), rule_type, value, window_min))


def list_rules():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM rules ORDER BY id DESC")]


def delete_rule(rule_id):
    with _conn() as c:
        c.execute("DELETE FROM rules WHERE id=?", (rule_id,))


def mark_triggered(rule_id, ts=None):
    with _conn() as c:
        c.execute("UPDATE rules SET last_triggered=? WHERE id=?", (ts or time.time(), rule_id))


# ---- alert log ----
def log_alert(rule_id, coin_id, message, ts=None):
    with _conn() as c:
        c.execute("INSERT INTO alert_log(rule_id,coin_id,message,ts) VALUES (?,?,?,?)",
                  (rule_id, coin_id, message, ts or time.time()))


def list_alerts(limit=20):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM alert_log ORDER BY ts DESC LIMIT ?", (limit,))]
