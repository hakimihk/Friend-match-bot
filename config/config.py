"""
=============================================================
 eFootball Friend Match Bot - Configuration File
 All settings are editable here. Use environment variables
 for production deployment.
=============================================================
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

# ─── BOT IDENTITY ────────────────────────────────────────────
BOT_TOKEN        = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
BOT_NAME         = os.getenv("BOT_NAME", "eFootball Match Bot")
BOT_USERNAME     = os.getenv("BOT_USERNAME", "efootball_match_bot")
DEVELOPER_NAME   = os.getenv("DEVELOPER_NAME", "YourName")
DEVELOPER_CONTACT= os.getenv("DEVELOPER_CONTACT", "@YourUsername")
VERSION          = "2.0.0"

# ─── OWNER / SUPER ADMIN ─────────────────────────────────────
# Set your Telegram user ID here (integer). 
# Get it from @userinfobot
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

# ─── WEBHOOK SETTINGS ────────────────────────────────────────
WEBHOOK_HOST   = os.getenv("WEBHOOK_HOST", "https://your-domain.com")
WEBHOOK_PORT   = int(os.getenv("PORT", "5000"))
WEBHOOK_PATH   = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL    = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
FLASK_HOST     = "0.0.0.0"
FLASK_PORT     = WEBHOOK_PORT

# ─── DATABASE ────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "database/efootball.db")

# ─── MATCH SYSTEM ────────────────────────────────────────────
ROOM_CODE_LENGTH    = 8          # eFootball room codes are exactly 8 digits
CODE_EXPIRY_SECONDS = 300        # Auto-delete unclaimed codes after 5 minutes
COOLDOWN_SECONDS    = 30         # Wait time between posting codes
MAX_CODES_PER_HOUR  = 10         # Max codes a single user can post per hour
ANTI_SPAM_WINDOW    = 60         # Seconds for spam detection window
ANTI_SPAM_LIMIT     = 5          # Max messages in spam window

# ─── LEAGUE SYSTEM ───────────────────────────────────────────
LEAGUE_SIZES           = [4, 8, 16]
LEAGUE_JOIN_TIMEOUT    = 3600    # 1 hour to fill league before auto-cancel
LEAGUE_MODES           = ["knockout", "round_robin"]
MAX_ACTIVE_LEAGUES     = 5       # Per group

# ─── PREMIUM ─────────────────────────────────────────────────
PREMIUM_PRICE_USD      = 5.00
PREMIUM_DURATION_DAYS  = 30

# ─── REFERRAL REWARDS ────────────────────────────────────────
REFERRAL_BONUS_POINTS  = 50

# ─── BACKUP ──────────────────────────────────────────────────
BACKUP_INTERVAL_HOURS  = 6       # Auto-backup every N hours
BACKUP_DIR             = "backups/"

# ─── LOGGING ─────────────────────────────────────────────────
LOG_FILE   = "logs/bot.log"
LOG_LEVEL  = "INFO"             # DEBUG / INFO / WARNING / ERROR

# ─── DEFAULT LANGUAGE ────────────────────────────────────────
DEFAULT_LANGUAGE = "so"         # so=Somali, en=English, ar=Arabic

# ─── MODULES TOGGLE ──────────────────────────────────────────
# Admins can toggle these from the panel too
MODULES = {
    "friend_match": True,
    "random_league": True,
    "premium":       True,
    "referral":      True,
    "ai_moderation": True,
}
