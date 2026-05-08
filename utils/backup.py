"""
=============================================================
 Auto Backup System
 Copies the SQLite database every N hours.
=============================================================
"""

import os
import shutil
import threading
import time
import logging
from datetime import datetime

from config.config import DB_PATH, BACKUP_DIR, BACKUP_INTERVAL_HOURS

logger = logging.getLogger(__name__)


def _do_backup():
    """Perform a single backup."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"efootball_{timestamp}.db")
    try:
        shutil.copy2(DB_PATH, dest)
        logger.info(f"✅ Backup saved: {dest}")
        # Keep only last 10 backups
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
            reverse=True
        )
        for old in backups[10:]:
            os.remove(os.path.join(BACKUP_DIR, old))
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")


def _backup_loop():
    while True:
        time.sleep(BACKUP_INTERVAL_HOURS * 3600)
        _do_backup()


def start_backup_scheduler():
    """Start the background backup thread."""
    thread = threading.Thread(target=_backup_loop, daemon=True)
    thread.start()
    logger.info(f"⏰ Auto-backup scheduler started (every {BACKUP_INTERVAL_HOURS}h)")
