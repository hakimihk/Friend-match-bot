"""
=============================================================
 Module: Core — Start, Help, Profile, Settings, Referral
=============================================================
"""

import logging
from datetime import datetime

import telebot
from telebot import types

from database import db
from languages import get_text, get_all_languages
from utils.helpers import (
    main_menu_keyboard, back_button, settings_keyboard,
    language_keyboard, admin_keyboard, format_leaderboard,
    security_check, STARTUP_BANNER
)
from config.config import (
    BOT_NAME, DEVELOPER_CONTACT, VERSION,
    COOLDOWN_SECONDS, CODE_EXPIRY_SECONDS, REFERRAL_BONUS_POINTS
)

logger = logging.getLogger(__name__)


def register_handlers(bot: telebot.TeleBot):

    # ════════════════════════════════════════════════════════
    #  /start
    # ════════════════════════════════════════════════════════

    @bot.message_handler(commands=["start"])
    def cmd_start(message: types.Message):
        user_id = message.from_user.id
        lang    = "so"  # default before we know user's preference

        # Register or update user
        db.upsert_user(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )

        # Handle referral link: /start ref_USER_ID
        args = message.text.split()
        if len(args) > 1 and args[1].startswith("ref_"):
            try:
                referrer_id = int(args[1][4:])
                if referrer_id != user_id:
                    first_time = db.set_referral(user_id, referrer_id)
                    if first_time:
                        db.add_points(user_id, REFERRAL_BONUS_POINTS)
                        db.add_points(referrer_id, REFERRAL_BONUS_POINTS)
                        referrer_lang = db.get_user_language(referrer_id)
                        referrer = db.get_user(referrer_id)
                        ref_uname = referrer.get("username", str(referrer_id)) if referrer else str(referrer_id)
                        bot.send_message(
                            user_id,
                            get_text("referral_success", lang,
                                     referrer=ref_uname, bonus=REFERRAL_BONUS_POINTS),
                            parse_mode="Markdown"
                        )
                        try:
                            bot.send_message(
                                referrer_id,
                                f"🎉 @{message.from_user.username or user_id} joined using your link!\n"
                                f"🎁 You earned *{REFERRAL_BONUS_POINTS} points*!",
                                parse_mode="Markdown"
                            )
                        except Exception:
                            pass
            except (ValueError, Exception) as e:
                logger.debug(f"Referral parse error: {e}")

        lang = db.get_user_language(user_id)
        name = message.from_user.first_name or "Player"

        text = get_text("welcome", lang, bot_name=BOT_NAME, user=name)
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(user_id, lang)
        )

    # ════════════════════════════════════════════════════════
    #  /help
    # ════════════════════════════════════════════════════════

    @bot.message_handler(commands=["help"])
    def cmd_help(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        bot.send_message(
            message.chat.id,
            get_text("help", lang, developer=DEVELOPER_CONTACT),
            parse_mode="Markdown",
            reply_markup=back_button(lang)
        )

    # ════════════════════════════════════════════════════════
    #  /profile
    # ════════════════════════════════════════════════════════

    @bot.message_handler(commands=["profile"])
    def cmd_profile(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        user    = db.get_user(user_id)
        if not user:
            bot.reply_to(message, get_text("error", lang))
            return

        rank     = db.get_user_rank(user_id)
        is_prem  = user.get("is_premium", 0)
        prem_str = get_text("premium_badge", lang) if is_prem else get_text("no_premium", lang)
        lang_names = get_all_languages()
        joined = user.get("joined_at", "")[:10]

        text = get_text(
            "profile", lang,
            user_id=user_id,
            name=user.get("first_name", "Player"),
            language=lang_names.get(user.get("language", "so"), "Somali"),
            joined=joined,
            codes_sent=user.get("codes_sent", 0),
            codes_claimed=user.get("codes_claimed", 0),
            wins=user.get("wins", 0),
            losses=user.get("losses", 0),
            total_matches=user.get("total_matches", 0),
            rank=rank,
            premium=prem_str,
            points=user.get("points", 0)
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    # ════════════════════════════════════════════════════════
    #  /settings & /language
    # ════════════════════════════════════════════════════════

    @bot.message_handler(commands=["settings"])
    def cmd_settings(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        bot.send_message(
            message.chat.id,
            get_text("settings_menu", lang),
            parse_mode="Markdown",
            reply_markup=settings_keyboard(lang)
        )

    @bot.message_handler(commands=["language"])
    def cmd_language(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        bot.send_message(
            message.chat.id,
            get_text("select_lang", lang),
            reply_markup=language_keyboard()
        )

    # ════════════════════════════════════════════════════════
    #  /refer
    # ════════════════════════════════════════════════════════

    @bot.message_handler(commands=["refer"])
    def cmd_refer(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        from config.config import BOT_USERNAME
        user = db.get_user(user_id)
        link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
        text = get_text(
            "referral_info", lang,
            link=link,
            count=user.get("referral_count", 0) if user else 0,
            points=user.get("points", 0) if user else 0,
            bonus=REFERRAL_BONUS_POINTS
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    # ════════════════════════════════════════════════════════
    #  /stats
    # ════════════════════════════════════════════════════════

    @bot.message_handler(commands=["stats"])
    def cmd_stats(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        stats   = db.get_global_stats()
        text = get_text(
            "global_stats", lang,
            total_users=stats["total_users"],
            total_matches=stats["total_matches"],
            total_codes=stats["total_codes"],
            total_leagues=stats["total_leagues"],
            premium_users=stats["premium_users"],
            new_users_today=stats["new_users_today"],
            matches_today=stats["matches_today"]
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    # ════════════════════════════════════════════════════════
    #  CALLBACK QUERY ROUTER
    # ════════════════════════════════════════════════════════

    @bot.callback_query_handler(func=lambda c: c.data.startswith("menu_"))
    def cb_menu(call: types.CallbackQuery):
        user_id = call.from_user.id
        lang    = db.get_user_language(user_id)
        action  = call.data[5:]

        if action == "main":
            name = call.from_user.first_name or "Player"
            text = get_text("welcome", lang, bot_name=BOT_NAME, user=name)
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard(user_id, lang)
            )

        elif action == "friendmatch":
            bot.edit_message_text(
                get_text("friend_match_info", lang,
                         cooldown=COOLDOWN_SECONDS,
                         expiry=CODE_EXPIRY_SECONDS),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=back_button(lang)
            )

        elif action == "league":
            bot.edit_message_text(
                get_text("league_menu", lang),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=_league_inline_keyboard(lang)
            )

        elif action == "help":
            bot.edit_message_text(
                get_text("help", lang, developer=DEVELOPER_CONTACT),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=back_button(lang)
            )

        elif action == "settings":
            bot.edit_message_text(
                get_text("settings_menu", lang),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=settings_keyboard(lang)
            )

        elif action == "profile":
            user = db.get_user(user_id)
            if not user:
                bot.answer_callback_query(call.id, get_text("error", lang))
                return
            rank = db.get_user_rank(user_id)
            is_prem = user.get("is_premium", 0)
            prem_str = get_text("premium_badge", lang) if is_prem else get_text("no_premium", lang)
            lang_names = get_all_languages()
            joined = user.get("joined_at", "")[:10]
            text = get_text(
                "profile", lang,
                user_id=user_id,
                name=user.get("first_name", "Player"),
                language=lang_names.get(user.get("language", "so"), "Somali"),
                joined=joined,
                codes_sent=user.get("codes_sent", 0),
                codes_claimed=user.get("codes_claimed", 0),
                wins=user.get("wins", 0),
                losses=user.get("losses", 0),
                total_matches=user.get("total_matches", 0),
                rank=rank,
                premium=prem_str,
                points=user.get("points", 0)
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=back_button(lang)
            )

        elif action == "admin":
            if not db.is_admin(user_id):
                bot.answer_callback_query(call.id, get_text("admin_only", lang), show_alert=True)
                return
            stats = db.get_global_stats()
            text = get_text(
                "admin_panel", lang,
                bot_name=BOT_NAME,
                version=VERSION,
                users=stats["total_users"],
                today_matches=stats["matches_today"],
                active_leagues=len(db.get_active_leagues()),
                banned=db.get_banned_count()
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=admin_keyboard(lang)
            )

        bot.answer_callback_query(call.id)

    # ── Settings callbacks ───────────────────────────────────

    @bot.callback_query_handler(func=lambda c: c.data == "settings_lang")
    def cb_settings_lang(call: types.CallbackQuery):
        user_id = call.from_user.id
        lang    = db.get_user_language(user_id)
        bot.edit_message_text(
            get_text("select_lang", lang),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=language_keyboard()
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("lang_"))
    def cb_lang_select(call: types.CallbackQuery):
        user_id  = call.from_user.id
        new_lang = call.data[5:]
        db.set_user_language(user_id, new_lang)
        lang_names = get_all_languages()
        lang_display = lang_names.get(new_lang, new_lang)
        bot.edit_message_text(
            get_text("lang_changed", new_lang, lang=lang_display),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button(new_lang, "menu_settings")
        )
        bot.answer_callback_query(call.id, f"✅ {lang_display}")


# ── Helper: League inline keyboard for main menu ──────────

def _league_inline_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    from utils.helpers import league_size_keyboard
    return league_size_keyboard(lang)
