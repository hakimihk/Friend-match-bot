"""
=============================================================
 Scheduler — Auto-expires room codes, sends reminders, etc.
=============================================================
"""

import threading
import time
import logging

from database import db

logger = logging.getLogger(__name__)


def _expire_codes_loop():
    """Every 60 seconds, expire old room codes."""
    while True:
        time.sleep(60)
        try:
            count = db.expire_old_codes()
            if count:
                logger.debug(f"🕐 Expired {count} room code(s).")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")


def start_scheduler():
    t = threading.Thread(target=_expire_codes_loop, daemon=True)
    t.start()
    logger.info("⏰ Code expiry scheduler started.")
