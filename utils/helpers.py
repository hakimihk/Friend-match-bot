"""
=============================================================
 Utilities — Keyboards, Formatting, Security, Helpers
=============================================================
"""

import re
import random
import string
import logging
from datetime import datetime
from typing import Optional

import telebot
from telebot import types

from languages import get_text, get_all_languages
from database import db
from config.config import (
    OWNER_ID, ROOM_CODE_LENGTH, COOLDOWN_SECONDS,
    CODE_EXPIRY_SECONDS, ANTI_SPAM_LIMIT, ANTI_SPAM_WINDOW,
    MAX_CODES_PER_HOUR, REFERRAL_BONUS_POINTS
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
#  KEYBOARD BUILDERS
# ════════════════════════════════════════════════════════════

def main_menu_keyboard(user_id: int, lang: str) -> types.InlineKeyboardMarkup:
    """Build the main start menu keyboard."""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text("btn_friend_match", lang),  callback_data="menu_friendmatch"),
        types.InlineKeyboardButton(get_text("btn_random_league", lang), callback_data="menu_league"),
    )
    kb.add(
        types.InlineKeyboardButton(get_text("btn_help", lang),     callback_data="menu_help"),
        types.InlineKeyboardButton(get_text("btn_settings", lang), callback_data="menu_settings"),
    )
    kb.add(
        types.InlineKeyboardButton(get_text("btn_profile", lang), callback_data="menu_profile"),
    )
    if db.is_admin(user_id):
        kb.add(
            types.InlineKeyboardButton(get_text("btn_admin", lang), callback_data="menu_admin"),
        )
    return kb


def back_button(lang: str, callback: str = "menu_main") -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(get_text("btn_back", lang), callback_data=callback))
    return kb


def claim_button(lang: str, code_id: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        get_text("btn_claim", lang),
        callback_data=f"claim_{code_id}"
    ))
    return kb


def language_keyboard() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    for code, name in get_all_languages().items():
        kb.add(types.InlineKeyboardButton(name, callback_data=f"lang_{code}"))
    return kb


def league_size_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(get_text("btn_league_4",  lang), callback_data="league_size_4"),
        types.InlineKeyboardButton(get_text("btn_league_8",  lang), callback_data="league_size_8"),
        types.InlineKeyboardButton(get_text("btn_league_16", lang), callback_data="league_size_16"),
    )
    kb.add(types.InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_main"))
    return kb


def league_mode_keyboard(lang: str, size: int) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text("btn_knockout",   lang), callback_data=f"league_mode_knockout_{size}"),
        types.InlineKeyboardButton(get_text("btn_roundrobin", lang), callback_data=f"league_mode_round_robin_{size}"),
    )
    kb.add(types.InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_league"))
    return kb


def admin_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text("btn_broadcast",      lang), callback_data="admin_broadcast"),
        types.InlineKeyboardButton(get_text("btn_view_stats",     lang), callback_data="admin_stats"),
    )
    kb.add(
        types.InlineKeyboardButton(get_text("btn_ban_user",       lang), callback_data="admin_ban"),
        types.InlineKeyboardButton(get_text("btn_unban_user",     lang), callback_data="admin_unban"),
    )
    kb.add(
        types.InlineKeyboardButton(get_text("btn_add_admin",      lang), callback_data="admin_addadmin"),
        types.InlineKeyboardButton(get_text("btn_remove_admin",   lang), callback_data="admin_removeadmin"),
    )
    kb.add(
        types.InlineKeyboardButton(get_text("btn_active_leagues", lang), callback_data="admin_leagues"),
        types.InlineKeyboardButton(get_text("btn_export_data",    lang), callback_data="admin_export"),
    )
    kb.add(
        types.InlineKeyboardButton(get_text("btn_maintenance",    lang), callback_data="admin_maintenance"),
        types.InlineKeyboardButton(get_text("btn_modules",        lang), callback_data="admin_modules"),
    )
    kb.add(types.InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_main"))
    return kb


def settings_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(get_text("btn_change_lang", lang), callback_data="settings_lang"))
    kb.add(types.InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_main"))
    return kb


def module_toggle_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=1)
    modules = ["friend_match", "random_league", "premium", "referral", "ai_moderation"]
    for mod in modules:
        enabled = db.is_module_enabled(mod)
        status = "✅" if enabled else "❌"
        kb.add(types.InlineKeyboardButton(
            f"{status} {mod.replace('_', ' ').title()}",
            callback_data=f"toggle_module_{mod}"
        ))
    kb.add(types.InlineKeyboardButton(get_text("btn_back", lang), callback_data="menu_admin"))
    return kb


# ════════════════════════════════════════════════════════════
#  ROOM CODE VALIDATION
# ════════════════════════════════════════════════════════════

ROOM_CODE_PATTERN = re.compile(r'^\d{8}$')


def is_valid_room_code(text: str) -> bool:
    """Check if text is exactly an 8-digit number."""
    return bool(ROOM_CODE_PATTERN.match(text.strip()))


def extract_room_code(text: str) -> Optional[str]:
    """Extract 8-digit code from message text if present."""
    match = re.search(r'\b\d{8}\b', text)
    return match.group(0) if match else None


# ════════════════════════════════════════════════════════════
#  SECURITY CHECKS
# ════════════════════════════════════════════════════════════

def security_check(user_id: int, chat_id: int, lang: str) -> Optional[str]:
    """
    Run all security checks for incoming messages.
    Returns an error string if blocked, None if OK.
    """
    if db.is_user_banned(user_id):
        return get_text("no_permission", lang)

    if db.is_user_muted(user_id):
        return get_text("no_permission", lang)

    if db.is_maintenance() and not db.is_admin(user_id):
        return "🔧 Bot is under maintenance. Please wait."

    return None  # All checks passed


def spam_check(user_id: int, chat_id: int, lang: str) -> Optional[str]:
    """Check for spam. Returns warning message or None."""
    count = db.log_message(user_id, chat_id)
    if count > ANTI_SPAM_LIMIT:
        db.mute_user(user_id, 60)
        return get_text("spam_warning", lang, seconds=60)
    return None


# ════════════════════════════════════════════════════════════
#  PIN GENERATOR
# ════════════════════════════════════════════════════════════

def generate_pin(length: int = 6) -> str:
    """Generate a unique league PIN code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ════════════════════════════════════════════════════════════
#  MESSAGE FORMATTERS
# ════════════════════════════════════════════════════════════

def format_time(dt_str: str) -> str:
    """Format ISO datetime string to human readable."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%H:%M — %d/%m/%Y")
    except Exception:
        return dt_str


def format_players_list(player_ids: list, bot: telebot.TeleBot) -> str:
    """Format list of player IDs to @username display string."""
    lines = []
    for i, uid in enumerate(player_ids, 1):
        user = db.get_user(uid)
        name = f"@{user['username']}" if user and user.get("username") else f"User#{uid}"
        lines.append(f"  {i}. {name}")
    return "\n".join(lines)


def format_fixtures(fixtures: list, player_ids: list, bot: telebot.TeleBot) -> str:
    """Format fixtures list to a readable bracket string."""
    if not fixtures:
        return "—"
    lines = []
    for round_data in fixtures:
        round_num = round_data.get("round", 1)
        lines.append(f"\n🏆 *Round {round_num}*")
        for i, match in enumerate(round_data.get("matches", []), 1):
            p1 = db.get_user(match["p1"])
            p2 = db.get_user(match["p2"])
            n1 = f"@{p1['username']}" if p1 and p1.get("username") else f"#{match['p1']}"
            n2 = f"@{p2['username']}" if p2 and p2.get("username") else f"#{match['p2']}"
            winner = ""
            if match.get("winner"):
                wu = db.get_user(match["winner"])
                winner = f" ✅ *{wu['username'] if wu else 'Winner'}*"
            lines.append(f"  ⚔️ Match {i}: {n1} vs {n2}{winner}")
    return "\n".join(lines)


def format_leaderboard(entries: list) -> str:
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 20
    lines = []
    for i, entry in enumerate(entries):
        medal = medals[i] if i < len(medals) else "  "
        uname = entry.get("username") or f"User#{entry['user_id']}"
        lines.append(f"{i+1}. {medal} @{uname} — {entry['wins']}W/{entry['losses']}L")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════
#  STARTUP ANIMATION TEXT
# ════════════════════════════════════════════════════════════

STARTUP_BANNER = """
╔══════════════════════════════════════╗
║  ⚽  eFootball Friend Match Bot  ⚽  ║
║         Starting up...               ║
║  ✅ Database initialized             ║
║  ✅ Language system loaded           ║
║  ✅ Webhook configured               ║
║  🚀 Bot is LIVE!                     ║
╚══════════════════════════════════════╝
"""
