"""
=============================================================
 Module: Admin Panel
 Full-featured admin control system.
=============================================================
"""

import io
import csv
import json
import logging

import telebot
from telebot import types

from database import db
from languages import get_text
from utils.helpers import admin_keyboard, module_toggle_keyboard, back_button
from config.config import OWNER_ID, VERSION, BOT_NAME

logger = logging.getLogger(__name__)

# Track pending admin actions per user
_pending_action: dict = {}  # {user_id: action_name}


def register_handlers(bot: telebot.TeleBot):

    # ════════════════════════════════════════════════════════
    #  COMMAND-STYLE ADMIN COMMANDS (!command)
    # ════════════════════════════════════════════════════════

    @bot.message_handler(func=lambda m: m.text and m.text.startswith("!"))
    def handle_admin_command(message: types.Message):
        user_id = message.from_user.id
        if not db.is_admin(user_id):
            return  # Silently ignore non-admins

        lang = db.get_user_language(user_id)
        parts = message.text.strip().split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "!addadmin":
            _cmd_add_admin(bot, message, parts, lang)
        elif cmd == "!removeadmin":
            _cmd_remove_admin(bot, message, parts, lang)
        elif cmd == "!ban":
            _cmd_ban(bot, message, parts, lang)
        elif cmd == "!unban":
            _cmd_unban(bot, message, parts, lang)
        elif cmd == "!stats":
            _cmd_stats(bot, message, lang)
        elif cmd == "!broadcast":
            _cmd_broadcast(bot, message, parts, lang)
        elif cmd == "!maintenance":
            _cmd_maintenance(bot, message, lang)
        elif cmd == "!clearchat":
            _cmd_clearchat(bot, message, lang)
        elif cmd == "!leagues":
            _cmd_leagues(bot, message, lang)
        elif cmd == "!help":
            _cmd_admin_help(bot, message, lang)

    # ════════════════════════════════════════════════════════
    #  INLINE PANEL CALLBACKS
    # ════════════════════════════════════════════════════════

    @bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
    def cb_admin(call: types.CallbackQuery):
        user_id = call.from_user.id
        if not db.is_admin(user_id):
            bot.answer_callback_query(call.id, "🚫 Admin only", show_alert=True)
            return

        lang   = db.get_user_language(user_id)
        action = call.data[6:]  # strip "admin_"

        if action == "stats":
            _show_stats(bot, call, lang)
        elif action == "broadcast":
            _pending_action[user_id] = "broadcast"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "📢 Send the broadcast message now:")
        elif action == "ban":
            _pending_action[user_id] = "ban"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "🚫 Send the user ID to ban:")
        elif action == "unban":
            _pending_action[user_id] = "unban"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "✅ Send the user ID to unban:")
        elif action == "addadmin":
            _pending_action[user_id] = "addadmin"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "➕ Send the user ID to make admin:")
        elif action == "removeadmin":
            _pending_action[user_id] = "removeadmin"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "➖ Send the user ID to remove admin:")
        elif action == "maintenance":
            current = db.get_setting("maintenance_mode", "0")
            new_val = "0" if current == "1" else "1"
            db.set_setting("maintenance_mode", new_val)
            status_msg = get_text("maintenance_on" if new_val == "1" else "maintenance_off", lang)
            bot.answer_callback_query(call.id, status_msg[:200])
            bot.edit_message_text(status_msg, call.message.chat.id, call.message.message_id)
        elif action == "modules":
            bot.answer_callback_query(call.id)
            bot.edit_message_text(
                "⚙️ *Module Control*",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=module_toggle_keyboard(lang)
            )
        elif action == "leagues":
            _show_active_leagues(bot, call, lang)
        elif action == "export":
            _export_data(bot, call, lang)

    # ── Module toggle callback ───────────────────────────────
    @bot.callback_query_handler(func=lambda c: c.data.startswith("toggle_module_"))
    def cb_toggle_module(call: types.CallbackQuery):
        user_id = call.from_user.id
        if not db.is_admin(user_id):
            bot.answer_callback_query(call.id, "🚫 Admin only", show_alert=True)
            return
        lang   = db.get_user_language(user_id)
        module = call.data[len("toggle_module_"):]
        current = db.get_setting(f"module_{module}", "1")
        new_val = "0" if current == "1" else "1"
        db.set_setting(f"module_{module}", new_val)
        bot.answer_callback_query(call.id, f"Module '{module}' {'enabled' if new_val=='1' else 'disabled'}")
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=module_toggle_keyboard(lang)
        )

    # ── Handle pending admin text input ─────────────────────
    @bot.message_handler(func=lambda m: m.from_user.id in _pending_action)
    def handle_pending_action(message: types.Message):
        user_id = message.from_user.id
        lang    = db.get_user_language(user_id)
        action  = _pending_action.pop(user_id, None)
        text    = message.text.strip()

        if action == "broadcast":
            users = db.get_all_users()
            count = 0
            for u in users:
                if u["is_banned"]:
                    continue
                try:
                    bot.send_message(u["user_id"], f"📢 *Broadcast:*\n\n{text}", parse_mode="Markdown")
                    count += 1
                except Exception:
                    pass
            bot.reply_to(message, get_text("broadcast_sent", lang, count=count))

        elif action == "ban":
            try:
                target_id = int(text)
                db.ban_user(target_id)
                target = db.get_user(target_id)
                uname = target.get("username", str(target_id)) if target else str(target_id)
                bot.reply_to(message, get_text("user_banned", lang, user=uname))
            except ValueError:
                bot.reply_to(message, "❌ Invalid user ID.")

        elif action == "unban":
            try:
                target_id = int(text)
                db.unban_user(target_id)
                target = db.get_user(target_id)
                uname = target.get("username", str(target_id)) if target else str(target_id)
                bot.reply_to(message, get_text("user_unbanned", lang, user=uname))
            except ValueError:
                bot.reply_to(message, "❌ Invalid user ID.")

        elif action == "addadmin":
            try:
                target_id = int(text)
                db.add_admin(target_id, user_id)
                target = db.get_user(target_id)
                uname = target.get("username", str(target_id)) if target else str(target_id)
                bot.reply_to(message, get_text("admin_added", lang, user=uname))
            except ValueError:
                bot.reply_to(message, "❌ Invalid user ID.")

        elif action == "removeadmin":
            try:
                target_id = int(text)
                if target_id == OWNER_ID:
                    bot.reply_to(message, "❌ Cannot remove bot owner from admins.")
                    return
                db.remove_admin(target_id)
                target = db.get_user(target_id)
                uname = target.get("username", str(target_id)) if target else str(target_id)
                bot.reply_to(message, get_text("admin_removed", lang, user=uname))
            except ValueError:
                bot.reply_to(message, "❌ Invalid user ID.")


# ════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════

def _show_stats(bot, call, lang):
    stats = db.get_global_stats()
    active = len(db.get_active_leagues())
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
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=back_button(lang, "menu_admin")
    )


def _show_active_leagues(bot, call, lang):
    leagues = db.get_active_leagues()
    if not leagues:
        bot.answer_callback_query(call.id, "No active leagues.", show_alert=True)
        return
    text = "🏆 *Active Leagues:*\n\n"
    for lg in leagues:
        text += f"📌 `{lg['pin']}` | {lg['mode']} | {len(lg['players'])}/{lg['max_players']} | {lg['status']}\n"
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=back_button(lang, "menu_admin")
    )


def _export_data(bot, call, lang):
    """Export user list as CSV."""
    users = db.get_all_users()
    output = io.StringIO()
    if users:
        writer = csv.DictWriter(output, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    output.seek(0)
    byte_data = output.getvalue().encode("utf-8")
    bot.answer_callback_query(call.id, "📁 Exporting...")
    bot.send_document(
        call.message.chat.id,
        io.BytesIO(byte_data),
        visible_file_name="users_export.csv",
        caption="📊 User data export"
    )


def _cmd_add_admin(bot, message, parts, lang):
    if len(parts) < 2:
        bot.reply_to(message, "Usage: !addadmin USER_ID")
        return
    try:
        target_id = int(parts[1])
        db.add_admin(target_id, message.from_user.id)
        target = db.get_user(target_id)
        uname = target.get("username", str(target_id)) if target else str(target_id)
        bot.reply_to(message, get_text("admin_added", lang, user=uname))
    except ValueError:
        bot.reply_to(message, "❌ Invalid user ID.")


def _cmd_remove_admin(bot, message, parts, lang):
    if len(parts) < 2:
        bot.reply_to(message, "Usage: !removeadmin USER_ID")
        return
    try:
        target_id = int(parts[1])
        if target_id == OWNER_ID:
            bot.reply_to(message, "❌ Cannot remove bot owner.")
            return
        db.remove_admin(target_id)
        bot.reply_to(message, get_text("admin_removed", lang, user=str(target_id)))
    except ValueError:
        bot.reply_to(message, "❌ Invalid user ID.")


def _cmd_ban(bot, message, parts, lang):
    if len(parts) < 2:
        bot.reply_to(message, "Usage: !ban USER_ID")
        return
    try:
        target_id = int(parts[1])
        db.ban_user(target_id)
        bot.reply_to(message, get_text("user_banned", lang, user=str(target_id)))
    except ValueError:
        bot.reply_to(message, "❌ Invalid user ID.")


def _cmd_unban(bot, message, parts, lang):
    if len(parts) < 2:
        bot.reply_to(message, "Usage: !unban USER_ID")
        return
    try:
        target_id = int(parts[1])
        db.unban_user(target_id)
        bot.reply_to(message, get_text("user_unbanned", lang, user=str(target_id)))
    except ValueError:
        bot.reply_to(message, "❌ Invalid user ID.")


def _cmd_stats(bot, message, lang):
    stats = db.get_global_stats()
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


def _cmd_broadcast(bot, message, parts, lang):
    if len(parts) < 2:
        bot.reply_to(message, "Usage: !broadcast Your message here")
        return
    text = parts[1] if len(parts) == 2 else " ".join(parts[1:])
    users = db.get_all_users()
    count = 0
    for u in users:
        if u["is_banned"]:
            continue
        try:
            bot.send_message(u["user_id"], f"📢 *Broadcast:*\n\n{text}", parse_mode="Markdown")
            count += 1
        except Exception:
            pass
    bot.reply_to(message, get_text("broadcast_sent", lang, count=count))


def _cmd_maintenance(bot, message, lang):
    current = db.get_setting("maintenance_mode", "0")
    new_val = "0" if current == "1" else "1"
    db.set_setting("maintenance_mode", new_val)
    msg = get_text("maintenance_on" if new_val == "1" else "maintenance_off", lang)
    bot.reply_to(message, msg)


def _cmd_clearchat(bot, message, lang):
    # Attempt to delete recent messages - requires admin rights in group
    try:
        for i in range(1, 20):
            try:
                bot.delete_message(message.chat.id, message.message_id - i)
            except Exception:
                pass
        bot.reply_to(message, "🧹 Chat cleared (recent messages).")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


def _cmd_leagues(bot, message, lang):
    leagues = db.get_active_leagues()
    if not leagues:
        bot.reply_to(message, "No active leagues.")
        return
    text = "🏆 *Active Leagues:*\n\n"
    for lg in leagues:
        text += f"📌 `{lg['pin']}` | {lg['mode']} | {len(lg['players'])}/{lg['max_players']} | {lg['status']}\n"
    bot.reply_to(message, text, parse_mode="Markdown")


def _cmd_admin_help(bot, message, lang):
    text = (
        "👑 *Admin Commands:*\n\n"
        "`!addadmin USER_ID` — Add admin\n"
        "`!removeadmin USER_ID` — Remove admin\n"
        "`!ban USER_ID` — Ban user\n"
        "`!unban USER_ID` — Unban user\n"
        "`!broadcast MESSAGE` — Send to all users\n"
        "`!stats` — View statistics\n"
        "`!leagues` — View active leagues\n"
        "`!maintenance` — Toggle maintenance mode\n"
        "`!clearchat` — Delete recent messages\n"
    )
    bot.reply_to(message, text, parse_mode="Markdown")
