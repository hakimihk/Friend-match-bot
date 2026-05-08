"""
=============================================================
 WSGI Entry Point — used by Gunicorn in production
 Command: gunicorn wsgi:app
=============================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logging
from utils.backup import start_backup_scheduler
from utils.scheduler import start_scheduler
from database.db import initialize_database
from webhook.server import create_webhook_server, setup_webhook

logger = setup_logging()

# ── Initialize everything ─────────────────────────────────────
initialize_database()
start_scheduler()
start_backup_scheduler()

# ── Create bot and register modules ──────────────────────────
from main import create_bot
bot = create_bot()

# ── Set webhook ───────────────────────────────────────────────
setup_webhook(bot)

# ── Create Flask app (Gunicorn will serve this) ───────────────
app = create_webhook_server(bot)

if __name__ == "__main__":
    app.run()
