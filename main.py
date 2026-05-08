"""
=============================================================
 eFootball Friend Match Bot — Main Entry Point
 Author  : Configurable in config/config.py
 Version : 2.0.0
 License : MIT
=============================================================

 HOW TO RUN:
   Webhook mode (production):
     python main.py --mode webhook

   Polling mode (local development):
     python main.py --mode polling

=============================================================
"""

import sys
import os
import argparse
import logging

# ── Add project root to path ──────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Internal imports ──────────────────────────────────────────
from utils.logger import setup_logging
from utils.helpers import STARTUP_BANNER
from utils.backup import start_backup_scheduler
from utils.scheduler import start_scheduler
from database.db import initialize_database
from config.config import BOT_TOKEN, BOT_NAME, VERSION, OWNER_ID

# ── Setup logging first ───────────────────────────────────────
logger = setup_logging()


def create_bot():
    """Initialize telebot instance with all modules registered."""
    import telebot
    from telebot import apihelper

    # Optional: use proxy if needed
    # apihelper.proxy = {'https': 'socks5h://user:pass@host:port'}

    bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, threaded=True)

    # ── Register all module handlers ──────────────────────────
    # ORDER MATTERS: core must come first, then specific modules,
    # then friend_match last (it catches all group messages).

    from modules.core import register_handlers as core_handlers
    from modules.league import register_handlers as league_handlers
    from modules.admin import register_handlers as admin_handlers
    from modules.friend_match import register_handlers as fm_handlers

    core_handlers(bot)
    league_handlers(bot)
    admin_handlers(bot)
    fm_handlers(bot)   # Must be last — catches all group text

    logger.info("✅ All modules registered.")
    return bot


def run_polling(bot):
    """Run bot in long-polling mode (for local development)."""
    logger.info("🔄 Starting in POLLING mode...")
    bot.remove_webhook()
    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=30,
        logger_level=logging.WARNING,
        allowed_updates=["message", "callback_query", "inline_query"]
    )


def run_webhook_mode(bot):
    """Run bot in webhook mode (for production servers)."""
    from webhook.server import run_webhook
    logger.info("🌐 Starting in WEBHOOK mode...")
    run_webhook(bot)


def main():
    parser = argparse.ArgumentParser(description="eFootball Friend Match Bot")
    parser.add_argument(
        "--mode",
        choices=["polling", "webhook"],
        default="webhook",
        help="Run mode: polling (dev) or webhook (prod)"
    )
    args = parser.parse_args()

    # ── Startup banner ────────────────────────────────────────
    print(STARTUP_BANNER)
    logger.info(f"🚀 Starting {BOT_NAME} v{VERSION}")
    logger.info(f"👑 Owner ID: {OWNER_ID}")

    # ── Initialize database ───────────────────────────────────
    logger.info("🗄️  Initializing database...")
    initialize_database()

    # ── Start background tasks ────────────────────────────────
    start_scheduler()          # Code expiry checker
    start_backup_scheduler()   # Auto database backup

    # ── Create bot ────────────────────────────────────────────
    bot = create_bot()
    logger.info(f"✅ Bot created: @{BOT_TOKEN.split(':')[0]}")

    # ── Run in selected mode ──────────────────────────────────
    try:
        if args.mode == "polling":
            run_polling(bot)
        else:
            run_webhook_mode(bot)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user.")
    except Exception as e:
        logger.critical(f"💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
