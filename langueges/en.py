"""
=============================================================
 Language File: English (en)
=============================================================
"""

STRINGS = {
    # ── General ──────────────────────────────────────────────
    "lang_name": "🇬🇧 English",
    "loading": "⏳ Loading...",
    "error": "❌ An error occurred. Please try again.",
    "no_permission": "🚫 You don't have permission for this action.",
    "admin_only": "👑 Only admins can use this command.",
    "owner_only": "🔒 Only the bot owner can use this command.",
    "cancelled": "✅ Cancelled.",
    "saved": "✅ Saved.",
    "not_found": "🔍 Not found.",
    "coming_soon": "🚀 Coming soon!",

    # ── Start / Welcome ──────────────────────────────────────
    "welcome": (
        "╔══════════════════════╗\n"
        "║  ⚽ {bot_name}  ⚽   ║\n"
        "╚══════════════════════╝\n\n"
        "👋 Welcome, *{user}*!\n\n"
        "🎮 This bot lets you post *eFootball Friend Match* room codes "
        "and create *Random Leagues* with friends.\n\n"
        "📋 Choose an option below:"
    ),
    "choose_option": "📋 Choose an option:",

    # ── Main Menu Buttons ────────────────────────────────────
    "btn_friend_match":  "🎮 Friend Match Challenge",
    "btn_random_league": "🎲 Random League",
    "btn_help":          "📖 Help",
    "btn_settings":      "⚙️ Settings",
    "btn_admin":         "👑 Admin Panel",
    "btn_profile":       "👤 My Profile",
    "btn_back":          "◀️ Back",
    "btn_cancel":        "❌ Cancel",
    "btn_confirm":       "✅ Confirm",
    "btn_close":         "🔒 Close",

    # ── Room Code System ─────────────────────────────────────
    "code_detected": (
        "🎮 *Room Code Detected!*\n\n"
        "📟 Code: `{code}`\n"
        "👤 Posted by: @{sender}\n"
        "⏰ Time: {time}\n\n"
        "⬇️ Press *Claim* to join the match!"
    ),
    "btn_claim":         "🎯 Claim Code",
    "code_claimed": (
        "✅ *Code Has Been Claimed!*\n\n"
        "📟 Code: `{code}`\n"
        "🏆 Claimed by: @{claimer}\n"
        "👤 Posted by: @{sender}\n"
        "⏰ Time: {time}"
    ),
    "cant_claim_own":    "❌ You cannot claim your own code!",
    "already_claimed":   "❌ This code has already been claimed!",
    "invalid_code":      "❌ Invalid code. Must be exactly 8 digits.",
    "code_expired":      "⏰ This code has expired.",
    "cooldown_active":   "⏳ Wait *{seconds}* seconds before posting another code.",
    "spam_warning":      "⚠️ Too many messages. You're muted for *{seconds}* seconds.",
    "duplicate_code":    "⚠️ This code was already posted.",
    "code_group_only":   "⚠️ Room codes must be posted in a group chat.",
    "group_only":        "⚠️ This command is only available in groups.",

    # ── Friend Match Info ────────────────────────────────────
    "friend_match_info": (
        "🎮 *Friend Match Challenge*\n\n"
        "📌 *How to use:*\n"
        "1️⃣ Open eFootball app\n"
        "2️⃣ Create a Friend Match\n"
        "3️⃣ Copy your 8-digit room code\n"
        "4️⃣ Post the code in this group\n"
        "5️⃣ Another player clicks *Claim* to join!\n\n"
        "⚡ *Rules:*\n"
        "• Codes must be exactly 8 digits\n"
        "• You can't claim your own code\n"
        "• Cooldown: {cooldown} seconds\n"
        "• Codes expire after {expiry} seconds"
    ),

    # ── League System ────────────────────────────────────────
    "league_menu": (
        "🎲 *Random League*\n\n"
        "Create a tournament bracket with random player assignments.\n\n"
        "Select league size:"
    ),
    "btn_league_4":  "👥 4 Players",
    "btn_league_8":  "👥 8 Players",
    "btn_league_16": "👥 16 Players",
    "league_mode_select": "🏆 Select tournament mode:",
    "btn_knockout":    "⚡ Knockout",
    "btn_roundrobin":  "🔄 Round Robin",
    "league_created": (
        "🏆 *League Created!*\n\n"
        "📌 *PIN Code:* `{pin}`\n"
        "👑 *Creator:* @{creator}\n"
        "🎯 *Mode:* {mode}\n"
        "👥 *Players:* {current}/{max}\n"
        "🎮 *Slots remaining:* {slots}\n\n"
        "📢 Share the PIN with your friends!\n"
        "To join: /joinleague `{pin}`"
    ),
    "league_joined": (
        "✅ *You joined the league!*\n\n"
        "🏆 *League:* {pin}\n"
        "👤 *You:* @{user}\n"
        "👥 *Players:* {current}/{max}\n"
        "⏳ *Remaining slots:* {slots}"
    ),
    "league_full_starting": (
        "🚀 *League is Full! Tournament Starting!*\n\n"
        "🏆 *PIN:* {pin}\n"
        "👥 *Players:*\n{players}\n\n"
        "📊 *Match Fixtures:*\n{fixtures}"
    ),
    "league_not_found":  "❌ No league found with this PIN.",
    "already_in_league": "❌ You've already joined this league.",
    "league_full":       "❌ This league is full.",
    "report_win": (
        "✅ *Result Recorded!*\n\n"
        "🏆 *Winner:* @{winner}\n"
        "❌ *Loser:* @{loser}\n"
        "⚽ *Score:* {score}"
    ),
    "btn_report_result": "📊 Report Result",
    "btn_join_league":   "🎯 Join League",
    "btn_view_bracket":  "📊 View Bracket",
    "btn_my_leagues":    "🏆 My Leagues",

    # ── Profile ──────────────────────────────────────────────
    "profile": (
        "👤 *Your Profile*\n\n"
        "🆔 *ID:* `{user_id}`\n"
        "👤 *Name:* {name}\n"
        "🌐 *Language:* {language}\n"
        "📅 *Joined:* {joined}\n\n"
        "📊 *Statistics:*\n"
        "🎮 *Codes Posted:* {codes_sent}\n"
        "✅ *Codes Claimed:* {codes_claimed}\n"
        "🏆 *Wins:* {wins}\n"
        "❌ *Losses:* {losses}\n"
        "⚽ *Total Matches:* {total_matches}\n"
        "🥇 *Global Rank:* #{rank}\n"
        "💎 *Premium:* {premium}\n"
        "🎁 *Points:* {points}"
    ),
    "premium_badge":   "💎 PREMIUM",
    "no_premium":      "❌ Not Premium",

    # ── Settings ─────────────────────────────────────────────
    "settings_menu": "⚙️ *Settings*\n\nChoose what to configure:",
    "btn_change_lang": "🌐 Change Language",
    "lang_changed":    "✅ Language changed to: {lang}",
    "select_lang":     "🌐 Select your language:",

    # ── Help ─────────────────────────────────────────────────
    "help": (
        "📖 *Help Guide*\n\n"
        "🎮 *Friend Match:*\n"
        "• Post an 8-digit code in a group\n"
        "• Another player clicks *Claim*\n\n"
        "🎲 *Random League:*\n"
        "• /createleague — Create a new league\n"
        "• /joinleague [PIN] — Join a league\n"
        "• /myleagues — View your leagues\n"
        "• /leaderboard — Global rankings\n\n"
        "👤 *Profile:*\n"
        "• /profile — Your stats\n"
        "• /stats — Statistics\n\n"
        "🔗 *Referral:*\n"
        "• /refer — Invite friends for rewards\n\n"
        "⚙️ *Other:*\n"
        "• /settings — Bot settings\n"
        "• /language — Change language\n\n"
        "💬 *Support:* {developer}"
    ),

    # ── Admin Panel ──────────────────────────────────────────
    "admin_panel": (
        "👑 *Admin Panel*\n\n"
        "🤖 Bot: *{bot_name}* v{version}\n"
        "📊 *Quick Stats:*\n"
        "👥 Users: {users}\n"
        "🎮 Matches today: {today_matches}\n"
        "🏆 Active leagues: {active_leagues}\n"
        "🚫 Banned users: {banned}\n\n"
        "Choose an option:"
    ),
    "btn_broadcast":     "📢 Broadcast Message",
    "btn_ban_user":      "🚫 Ban User",
    "btn_unban_user":    "✅ Unban User",
    "btn_add_admin":     "➕ Add Admin",
    "btn_remove_admin":  "➖ Remove Admin",
    "btn_view_stats":    "📊 View Statistics",
    "btn_active_leagues":"🏆 Active Leagues",
    "btn_export_data":   "💾 Export Data",
    "btn_maintenance":   "🔧 Maintenance Mode",
    "btn_modules":       "⚙️ Module Control",
    "broadcast_sent":    "✅ Message sent to {count} users.",
    "user_banned":       "🚫 @{user} has been banned.",
    "user_unbanned":     "✅ @{user} has been unbanned.",
    "admin_added":       "✅ @{user} is now an admin.",
    "admin_removed":     "➖ @{user} is no longer an admin.",
    "maintenance_on":    "🔧 Bot entered maintenance mode. Regular users cannot interact.",
    "maintenance_off":   "✅ Maintenance ended. Bot is back online.",

    # ── Statistics ───────────────────────────────────────────
    "global_stats": (
        "📊 *Global Statistics*\n\n"
        "👥 *Total Users:* {total_users}\n"
        "🎮 *Total Matches:* {total_matches}\n"
        "📟 *Total Codes:* {total_codes}\n"
        "🏆 *Total Leagues:* {total_leagues}\n"
        "💎 *Premium Users:* {premium_users}\n"
        "📅 *Today:*\n"
        "  👤 New Users: {new_users_today}\n"
        "  🎮 Matches: {matches_today}"
    ),

    # ── Leaderboard ──────────────────────────────────────────
    "leaderboard": (
        "🥇 *Global Leaderboard*\n\n"
        "{entries}\n\n"
        "📅 Updated: {updated}"
    ),
    "leaderboard_entry": "{rank}. {medal} @{username} — {wins}W/{losses}L",

    # ── Referral ─────────────────────────────────────────────
    "referral_info": (
        "🎁 *Referral System*\n\n"
        "🔗 *Your unique link:*\n{link}\n\n"
        "👥 *Referred users:* {count}\n"
        "🎯 *Referral points:* {points}\n\n"
        "💡 Earn *{bonus} points* for every friend you invite!"
    ),
    "referral_success": (
        "🎉 You were referred by @{referrer}!\n"
        "🎁 Both of you earned *{bonus} points*!"
    ),
}
