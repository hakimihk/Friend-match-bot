"""
=============================================================
 Module: Friend Match Challenge
 Handles room code detection, claiming, cooldowns, anti-spam.
=============================================================
"""

import logging
from datetime import datetime

import telebot
from telebot import types

from database import db
from languages import get_text
from utils.helpers import (
    is_valid_room_code, extract_room_code,
    claim_button, format_time, security_check, spam_check
)
from config.config import (
    COOLDOWN_SECONDS, CODE_EXPIRY_SECONDS, MAX_CODES_PER_HOUR,
    ANTI_SPAM_LIMIT
)

logger = logging.getLogger(__name__)


def register_handlers(bot: telebot.TeleBot):
    """Register all friend match handlers with the bot."""

    # ── Handle any group message for code detection ──────────
    @bot.message_handler(
        func=lambda m: m.chat.type in ("group", "supergroup") and m.text
    )
    def handle_group_message(message: types.Message):
        user_id  = message.from_user.id
        chat_id  = message.chat.id
        text     = message.text.strip()
        lang     = db.get_user_language(user_id)

        # Register user
        db.upsert_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )

        # Security gate
        blocked = security_check(user_id, chat_id, lang)
        if blocked:
            try:
                bot.delete_message(chat_id, message.message_id)
            except Exception:
                pass
            return

        # Check if module enabled
        if not db.is_module_enabled("friend_match"):
            return

        # Extract room code from message
        code = extract_room_code(text)
        if not code:
            # Not a room code — run spam check on non-code messages
            spam_warn = spam_check(user_id, chat_id, lang)
            if spam_warn:
                bot.send_message(chat_id, spam_warn, parse_mode="Markdown")
            return

        # Validate code format
        if not is_valid_room_code(code):
            try:
                bot.delete_message(chat_id, message.message_id)
            except Exception:
                pass
            bot.send_message(
                chat_id,
                get_text("invalid_code", lang),
                parse_mode="Markdown"
            )
            return

        # Delete the raw code message
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception:
            pass

        # Check hourly limit
        if db.check_hourly_limit(user_id, MAX_CODES_PER_HOUR):
            bot.send_message(
                chat_id,
                f"⚠️ {message.from_user.first_name}: hourly code limit reached.",
                parse_mode="Markdown"
            )
            return

        # Check cooldown
        remaining = db.check_and_set_cooldown(user_id, COOLDOWN_SECONDS)
        if remaining:
            bot.send_message(
                chat_id,
                get_text("cooldown_active", lang, seconds=remaining),
                parse_mode="Markdown"
            )
            return

        # Check duplicate code in this chat
        if db.is_code_duplicate(code, chat_id):
            bot.send_message(
                chat_id,
                get_text("duplicate_code", lang),
                parse_mode="Markdown"
            )
            return

        # Post the code with Claim button
        username = message.from_user.username or message.from_user.first_name
        now_str  = format_time(datetime.utcnow().isoformat())

        text_out = get_text(
            "code_detected", lang,
            code=code,
            sender=username,
            time=now_str
        )

        # Send placeholder to get message_id, then save to DB
        sent = bot.send_message(
            chat_id,
            text_out,
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup()  # Temporary
        )

        # Save code to DB
        code_id = db.save_room_code(
            code, user_id, chat_id, sent.message_id, CODE_EXPIRY_SECONDS
        )

        # Edit message with proper claim button
        bot.edit_message_reply_markup(
            chat_id,
            sent.message_id,
            reply_markup=claim_button(lang, code_id)
        )

        logger.info(f"Code {code} posted by {user_id} in chat {chat_id}, id={code_id}")

    # ── Handle Claim button ──────────────────────────────────
    @bot.callback_query_handler(func=lambda call: call.data.startswith("claim_"))
    def handle_claim(call: types.CallbackQuery):
        user_id    = call.from_user.id
        chat_id    = call.message.chat.id
        lang       = db.get_user_language(user_id)
        code_id    = int(call.data.split("_")[1])

        # Security
        blocked = security_check(user_id, chat_id, lang)
        if blocked:
            bot.answer_callback_query(call.id, blocked, show_alert=True)
            return

        # Get code from DB
        conn_row = db.get_code_by_message(call.message.message_id, chat_id)
        if not conn_row:
            bot.answer_callback_query(call.id, get_text("code_expired", lang), show_alert=True)
            return

        # Check if already claimed
        if conn_row["status"] == "claimed":
            bot.answer_callback_query(call.id, get_text("already_claimed", lang), show_alert=True)
            return

        # Check if claiming own code
        if conn_row["sender_id"] == user_id:
            bot.answer_callback_query(call.id, get_text("cant_claim_own", lang), show_alert=True)
            return

        # Check expiry
        if conn_row["status"] == "expired":
            bot.answer_callback_query(call.id, get_text("code_expired", lang), show_alert=True)
            return

        # Claim the code
        success = db.claim_code(code_id, user_id)
        if not success:
            bot.answer_callback_query(call.id, get_text("already_claimed", lang), show_alert=True)
            return

        # Build claimed message
        sender  = db.get_user(conn_row["sender_id"])
        claimer = db.get_user(user_id)
        sender_name  = f"@{sender['username']}"  if sender  and sender.get("username")  else f"User#{conn_row['sender_id']}"
        claimer_name = f"@{claimer['username']}" if claimer and claimer.get("username") else call.from_user.first_name

        text_out = get_text(
            "code_claimed", lang,
            code=conn_row["code"],
            claimer=claimer_name,
            sender=sender_name,
            time=format_time(datetime.utcnow().isoformat())
        )

        try:
            bot.edit_message_text(
                text_out,
                chat_id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=None
            )
        except Exception as e:
            logger.error(f"Edit message error: {e}")

        bot.answer_callback_query(call.id, "✅")
        logger.info(f"Code {conn_row['code']} claimed by {user_id}")
