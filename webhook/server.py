"""
=============================================================
 Webhook Server (Flask)
 Compatible with: Render, Railway, Koyeb, VPS, Katabump
=============================================================
"""

import logging
import json

from flask import Flask, request, abort

import telebot

from config.config import (
    BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH,
    FLASK_HOST, FLASK_PORT
)

logger = logging.getLogger(__name__)

app = Flask(__name__)


def create_webhook_server(bot: telebot.TeleBot) -> Flask:
    """
    Configure Flask app for webhook mode.
    Returns the Flask app instance.
    """

    @app.route("/", methods=["GET"])
    def index():
        return "⚽ eFootball Bot is running! ✅", 200

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "bot": "running"}, 200

    @app.route(WEBHOOK_PATH, methods=["POST"])
    def webhook():
        if request.headers.get("content-type") == "application/json":
            json_string = request.get_data().decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return "", 200
        else:
            abort(403)

    return app


def setup_webhook(bot: telebot.TeleBot):
    """Remove old webhook and set new one."""
    bot.remove_webhook()
    result = bot.set_webhook(url=WEBHOOK_URL)
    if result:
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}")
    else:
        logger.error("❌ Failed to set webhook!")
    return result


def run_webhook(bot: telebot.TeleBot):
    """Full webhook startup sequence."""
    setup_webhook(bot)
    flask_app = create_webhook_server(bot)
    logger.info(f"🚀 Flask server starting on {FLASK_HOST}:{FLASK_PORT}")
    flask_app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=False,
        threaded=True
    )
