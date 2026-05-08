"""
=============================================================
 Module: Random League
 Creates and manages eFootball random tournaments.
=============================================================
"""

import logging
import random

import telebot
from telebot import types

from database import db
from languages import get_text
from utils.helpers import (
    generate_pin, league_size_keyboard, league_mode_keyboard,
    format_players_list, format_fixtures, back_button, security_check
)
from config.config import MAX_ACTIVE_LEAGUES

logger = logging.getLogger(__name__)


def register_handlers(bot: telebot.TeleBot):

    # ── /createleague command ────────────────────────────────
    @bot.message_handler(commands=["createleague"])
    def cmd_create_league(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        lang    = db.get_user_language(user_id)

        db.upsert_user(user_id, message.from_user.username,
                       message.from_user.first_name, message.from_user.last_name)

        blocked = security_check(user_id, chat_id, lang)
        if blocked:
            bot.reply_to(message, blocked)
            return

        if not db.is_module_enabled("random_league"):
            bot.reply_to(message, get_text("coming_soon", lang))
            return

        # Check group limit
        active = db.get_active_leagues(chat_id)
        if len(active) >= MAX_ACTIVE_LEAGUES:
            bot.reply_to(message, f"⚠️ Max {MAX_ACTIVE_LEAGUES} active leagues per group.")
            return

        bot.send_message(
            chat_id,
            get_text("league_menu", lang),
            parse_mode="Markdown",
            reply_markup=league_size_keyboard(lang)
        )

    # ── /joinleague [PIN] command ────────────────────────────
    @bot.message_handler(commands=["joinleague"])
    def cmd_join_league(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        lang    = db.get_user_language(user_id)

        db.upsert_user(user_id, message.from_user.username,
                       message.from_user.first_name, message.from_user.last_name)

        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❓ Usage: /joinleague PIN")
            return

        pin = args[1].upper()
        _process_join(bot, chat_id, user_id, pin, lang)

    # ── /myleagues command ───────────────────────────────────
    @bot.message_handler(commands=["myleagues"])
    def cmd_my_leagues(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        lang    = db.get_user_language(user_id)

        leagues = db.get_user_leagues(user_id)
        if not leagues:
            bot.reply_to(message, "🏆 You have no active leagues.")
            return

        text = "🏆 *Your Active Leagues:*\n\n"
        for lg in leagues:
            text += (
                f"📌 PIN: `{lg['pin']}` | Mode: {lg['mode']} | "
                f"Players: {len(lg['players'])}/{lg['max_players']} | Status: {lg['status']}\n"
            )
        bot.reply_to(message, text, parse_mode="Markdown")

    # ── /leaderboard command ─────────────────────────────────
    @bot.message_handler(commands=["leaderboard"])
    def cmd_leaderboard(message: types.Message):
        from utils.helpers import format_leaderboard
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        entries = db.get_leaderboard(10)
        if not entries:
            bot.reply_to(message, "📊 No leaderboard data yet.")
            return
        text = get_text(
            "leaderboard", lang,
            entries=format_leaderboard(entries),
            updated="now"
        )
        bot.reply_to(message, text, parse_mode="Markdown")

    # ── Callback: league size selection ─────────────────────
    @bot.callback_query_handler(func=lambda c: c.data.startswith("league_size_"))
    def cb_league_size(call: types.CallbackQuery):
        user_id = call.from_user.id
        lang    = db.get_user_language(user_id)
        size    = int(call.data.split("_")[2])

        bot.edit_message_text(
            get_text("league_mode_select", lang),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=league_mode_keyboard(lang, size)
        )
        bot.answer_callback_query(call.id)

    # ── Callback: league mode selection + create ─────────────
    @bot.callback_query_handler(func=lambda c: c.data.startswith("league_mode_"))
    def cb_league_mode(call: types.CallbackQuery):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang    = db.get_user_language(user_id)

        # Data format: league_mode_{mode}_{size}
        parts = call.data.split("_")
        # parts: ['league', 'mode', 'knockout'|'round', 'robin'|size, (size)]
        # Handle "round_robin" having underscore
        if parts[2] == "round":
            mode = "round_robin"
            size = int(parts[4])
        else:
            mode = parts[2]
            size = int(parts[3])

        # Generate unique PIN
        pin = generate_pin()
        while db.get_league(pin):
            pin = generate_pin()

        creator_username = call.from_user.username or call.from_user.first_name

        # Create league in DB
        db.create_league(pin, user_id, chat_id, mode, size)

        text = get_text(
            "league_created", lang,
            pin=pin,
            creator=creator_username,
            mode=mode.replace("_", " ").title(),
            current=1,
            max=size,
            slots=size - 1
        )

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            get_text("btn_join_league", lang),
            callback_data=f"join_league_{pin}"
        ))
        kb.add(types.InlineKeyboardButton(
            get_text("btn_view_bracket", lang),
            callback_data=f"view_bracket_{pin}"
        ))

        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=kb
        )
        bot.answer_callback_query(call.id, "✅ League created!")

    # ── Callback: join league via button ────────────────────
    @bot.callback_query_handler(func=lambda c: c.data.startswith("join_league_"))
    def cb_join_league(call: types.CallbackQuery):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        lang    = db.get_user_language(user_id)
        pin     = call.data.split("_")[2]

        _process_join(bot, chat_id, user_id, pin, lang, call=call)

    # ── Callback: view bracket ───────────────────────────────
    @bot.callback_query_handler(func=lambda c: c.data.startswith("view_bracket_"))
    def cb_view_bracket(call: types.CallbackQuery):
        user_id = call.from_user.id
        lang    = db.get_user_language(user_id)
        pin     = call.data.split("_")[2]

        league = db.get_league(pin)
        if not league:
            bot.answer_callback_query(call.id, get_text("league_not_found", lang), show_alert=True)
            return

        players_str  = format_players_list(league["players"], bot)
        fixtures_str = format_fixtures(league["fixtures"], league["players"], bot)

        text = (
            f"📊 *League Bracket*\n"
            f"📌 PIN: `{pin}` | Mode: {league['mode']}\n"
            f"👥 Players: {len(league['players'])}/{league['max_players']}\n\n"
            f"*Players:*\n{players_str}\n\n"
            f"*Fixtures:*\n{fixtures_str}"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


def _process_join(bot, chat_id, user_id, pin, lang, call=None):
    """Shared logic for joining a league."""
    result = db.join_league(pin, user_id)
    status = result["status"]

    if status == "not_found":
        msg = get_text("league_not_found", lang)
    elif status == "already_in":
        msg = get_text("already_in_league", lang)
    elif status == "full":
        msg = get_text("league_full", lang)
    elif status == "started":
        msg = "❌ This league has already started."
    elif status == "joined":
        league = result["league"]
        username = db.get_user(user_id)
        uname = f"@{username['username']}" if username and username.get("username") else f"User#{user_id}"

        msg = get_text(
            "league_joined", lang,
            pin=pin,
            user=uname,
            current=len(league["players"]),
            max=league["max_players"],
            slots=league["max_players"] - len(league["players"])
        )

        # If league is now full and active, announce bracket
        if league["status"] == "active":
            players_str  = format_players_list(league["players"], bot)
            fixtures_str = format_fixtures(league["fixtures"], league["players"], bot)
            full_msg = get_text(
                "league_full_starting", lang,
                pin=pin,
                players=players_str,
                fixtures=fixtures_str
            )
            bot.send_message(chat_id, full_msg, parse_mode="Markdown")
    else:
        msg = get_text("error", lang)

    if call:
        bot.answer_callback_query(call.id, msg[:200], show_alert=status != "joined")
        if status == "joined":
            bot.send_message(chat_id, msg, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, msg, parse_mode="Markdown")
