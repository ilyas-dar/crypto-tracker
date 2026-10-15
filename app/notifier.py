"""Notification layer: console always, Telegram / email if configured."""
import logging
import smtplib
from email.message import EmailMessage
import requests
from app import config

log = logging.getLogger("alerts")


def _console(msg):
    log.warning("ALERT: %s", msg)
    print(f"[ALERT] {msg}", flush=True)


def _telegram(msg):
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": msg}, timeout=10)


def _email(msg):
    if config.SMTP_HOST and config.EMAIL_TO:
        m = EmailMessage()
        m["Subject"] = "Crypto alert"
        m["From"] = config.SMTP_USER
        m["To"] = config.EMAIL_TO
        m.set_content(msg)
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as s:
            s.starttls()
            s.login(config.SMTP_USER, config.SMTP_PASS)
            s.send_message(m)


def notify(msg):
    _console(msg)
    for channel in (_telegram, _email):
        try:
            channel(msg)
        except Exception as exc:  # a failing channel must never stop the poller
            log.error("notification channel failed: %s", exc)
