"""
=============================================================
 Language File: Somali (so)
=============================================================
"""

STRINGS = {
    # ── General ──────────────────────────────────────────────
    "lang_name": "🇸🇴 Soomaali",
    "loading": "⏳ Sug...",
    "error": "❌ Khalad ayaa dhacay. Isku day mar kale.",
    "no_permission": "🚫 Fasax kuma haysid amarka kan.",
    "admin_only": "👑 Admins kaliya ayaa amarka kan isticmaali kara.",
    "owner_only": "🔒 Mulkiga bot-ka kaliya ayaa amarka kan isticmaali kara.",
    "cancelled": "✅ Waa la joojiyay.",
    "saved": "✅ Waa la keydsaday.",
    "not_found": "🔍 Lama helin.",
    "coming_soon": "🚀 Dhawaan ayuu yimaadaa!",

    # ── Start / Welcome ──────────────────────────────────────
    "welcome": (
        "╔══════════════════════╗\n"
        "║  ⚽ {bot_name}  ⚽   ║\n"
        "╚══════════════════════╝\n\n"
        "👋 Soo dhawoow, *{user}*!\n\n"
        "🎮 Bot-kan waxaad ku tartami kartaa *eFootball Friend Matches* oo "
        "aad ku abuuri kartaa *Random Leagues*.\n\n"
        "📋 Dooro xulashada hoose:"
    ),
    "choose_option": "📋 Dooro xulashada:",

    # ── Main Menu Buttons ────────────────────────────────────
    "btn_friend_match":  "🎮 Friend Match Challenge",
    "btn_random_league": "🎲 Random League",
    "btn_help":          "📖 Caawimo",
    "btn_settings":      "⚙️ Dejinta",
    "btn_admin":         "👑 Admin Panel",
    "btn_profile":       "👤 Profile-kayga",
    "btn_back":          "◀️ Dib",
    "btn_cancel":        "❌ Jooji",
    "btn_confirm":       "✅ Xaqiiji",
    "btn_close":         "🔒 Xidh",

    # ── Room Code System ─────────────────────────────────────
    "code_detected": (
        "🎮 *Room Code La Helay!*\n\n"
        "📟 Code: `{code}`\n"
        "👤 Waxaa soo diray: @{sender}\n"
        "⏰ Wakhti: {time}\n\n"
        "⬇️ Riix *Qaado* si aad u qaadato!"
    ),
    "btn_claim":         "🎯 Qaado Code-ka",
    "code_claimed": (
        "✅ *Code-ka Waa La Qaatay!*\n\n"
        "📟 Code: `{code}`\n"
        "🏆 Qaatay: @{claimer}\n"
        "👤 Soo diray: @{sender}\n"
        "⏰ Wakhti: {time}"
    ),
    "cant_claim_own":    "❌ Code-kaaga adiga ah ma qaadan kartid!",
    "already_claimed":   "❌ Code-kan horey ayaa loo qaatay!",
    "invalid_code":      "❌ Code-ka waa khalad. Waxaa loo baahan yahay 8 tirood oo xaqiiqda ah.",
    "code_expired":      "⏰ Code-kan waa xilligii dhacay.",
    "cooldown_active":   "⏳ Sug *{seconds}* ilbiriqsi ka hor intaadan code kale soo dirin.",
    "spam_warning":      "⚠️ Fariimo badan ayaad soo dirtay. Waxaad xidnaatay *{seconds}* ilbiriqsi.",
    "duplicate_code":    "⚠️ Code-kan horey ayaa loo geeyay.",
    "code_group_only":   "⚠️ Code-yada waa in la soo diro koox (group) dhex.",
    "group_only":        "⚠️ Amarka kan waxaa loo isticmaalaa kooxaha kaliya.",

    # ── Friend Match Info ────────────────────────────────────
    "friend_match_info": (
        "🎮 *Friend Match Challenge*\n\n"
        "📌 *Sida loo isticmaalo:*\n"
        "1️⃣ Fur eFootball app-kaaga\n"
        "2️⃣ Abuuro Friend Match\n"
        "3️⃣ Nuqul gal oo code-ka 8-tiroodka ah\n"
        "4️⃣ Soo dir code-ka kooxdan\n"
        "5️⃣ Ciyaaryahankale wuxuu gujiyaa *Qaado* oo ku biira!\n\n"
        "⚡ *Xeerarka:*\n"
        "• Code-yadu waa inay ahaadaan 8 tirood\n"
        "• Midkiiba wuxuu qaadan karaa code-giisa\n"
        "• Cooldown: {cooldown} ilbiriqsi\n"
        "• Code-yadu way dhacaan {expiry} ilbiriqsi kadib"
    ),

    # ── League System ────────────────────────────────────────
    "league_menu": (
        "🎲 *Random League*\n\n"
        "Abuur koox ciyaar ah oo si toos ah loo kala diri karo.\n\n"
        "Dooro baaxadda kooxda:"
    ),
    "btn_league_4":  "👥 4 Ciyaaryahan",
    "btn_league_8":  "👥 8 Ciyaaryahan",
    "btn_league_16": "👥 16 Ciyaaryahan",
    "league_mode_select": "🏆 Dooro nooca tartanka:",
    "btn_knockout":    "⚡ Knockout",
    "btn_roundrobin":  "🔄 Round Robin",
    "league_created": (
        "🏆 *Koox La Abuuray!*\n\n"
        "📌 *PIN Code:* `{pin}`\n"
        "👑 *Abuuraha:* @{creator}\n"
        "🎯 *Nooc:* {mode}\n"
        "👥 *Ciyaaryahanada:* {current}/{max}\n"
        "🎮 *Meelaynta joogtada:* {slots} ayaa hadaan\n\n"
        "📢 Ku wadaag PIN-ka saaxiibadaada!\n"
        "Ku biir adiguuna: /joinleague `{pin}`"
    ),
    "league_joined": (
        "✅ *Waad ku biiray kooxda!*\n\n"
        "🏆 *Koox:* {pin}\n"
        "👤 *Adigu:* @{user}\n"
        "👥 *Ciyaaryahanada:* {current}/{max}\n"
        "⏳ *Hadaan joogta ah:* {slots}"
    ),
    "league_full_starting": (
        "🚀 *Kooxdu Way Buuxday! Tartanka Waa Bilaabmay!*\n\n"
        "🏆 *PIN:* {pin}\n"
        "👥 *Ciyaaryahanada:*\n{players}\n\n"
        "📊 *Jadwalka Ciyaaraha:*\n{fixtures}"
    ),
    "league_not_found":  "❌ Koox laga heli waaye PIN-kan.",
    "already_in_league": "❌ Horey ayaad ugu biirtay kooxdan.",
    "league_full":       "❌ Kooxdu way buuxday.",
    "report_win": (
        "✅ *Guushii Waa La Diiwaan Galiyay!*\n\n"
        "🏆 *Ku guuleystay:* @{winner}\n"
        "❌ *Ku waayay:* @{loser}\n"
        "⚽ *Natiijo:* {score}"
    ),
    "btn_report_result": "📊 Natiijada Soo Gudbi",
    "btn_join_league":   "🎯 Ku Biir Kooxda",
    "btn_view_bracket":  "📊 Eeg Jadwalka",
    "btn_my_leagues":    "🏆 Kooxaheeyga",

    # ── Profile ──────────────────────────────────────────────
    "profile": (
        "👤 *Profile-kaaga*\n\n"
        "🆔 *ID:* `{user_id}`\n"
        "👤 *Magac:* {name}\n"
        "🌐 *Luqad:* {language}\n"
        "📅 *Isdiiwaan gelintii:* {joined}\n\n"
        "📊 *Tirakoobka:*\n"
        "🎮 *Code-yada La Diray:* {codes_sent}\n"
        "✅ *La Qaatay:* {codes_claimed}\n"
        "🏆 *Guulaha:* {wins}\n"
        "❌ *Waayaasha:* {losses}\n"
        "⚽ *Ciyaarada:* {total_matches}\n"
        "🥇 *Daraja Adduunka:* #{rank}\n"
        "💎 *Premium:* {premium}\n"
        "🎁 *Dhibcaha:* {points}"
    ),
    "premium_badge":   "💎 PREMIUM",
    "no_premium":      "❌ Aan Premium Ahayn",

    # ── Settings ─────────────────────────────────────────────
    "settings_menu": "⚙️ *Dejinta*\n\nDooro waxa aad bedeli rabto:",
    "btn_change_lang": "🌐 Bedel Luqadda",
    "lang_changed":    "✅ Luqadda waa la bedeley: {lang}",
    "select_lang":     "🌐 Dooro luqaddaada:",

    # ── Help ─────────────────────────────────────────────────
    "help": (
        "📖 *Caawimada*\n\n"
        "🎮 *Friend Match:*\n"
        "• Soo dir code 8-tiroodka ah (group-ka)\n"
        "• Ciyaaryahankale wuxuu gujiyaa *Qaado*\n\n"
        "🎲 *Random League:*\n"
        "• /createleague — Abuur koox cusub\n"
        "• /joinleague [PIN] — Ku biir koox\n"
        "• /myleagues — Kooxaheeyga\n"
        "• /leaderboard — Daraja guud\n\n"
        "👤 *Profile:*\n"
        "• /profile — Macluumaadkaaga\n"
        "• /stats — Tirakoobkaaga\n\n"
        "🔗 *Kumanaan:*\n"
        "• /refer — Raalli galinta saaxiibadaada\n\n"
        "⚙️ *Kale:*\n"
        "• /settings — Dejinta\n"
        "• /language — Bedel luqadda\n\n"
        "💬 *Caawimaad:* {developer}"
    ),

    # ── Admin Panel ──────────────────────────────────────────
    "admin_panel": (
        "👑 *Admin Panel*\n\n"
        "🤖 Bot: *{bot_name}* v{version}\n"
        "📊 *Tirakoob degdeg ah:*\n"
        "👥 Isticmaalayaasha: {users}\n"
        "🎮 Ciyaarada maanta: {today_matches}\n"
        "🏆 Kooxaha firfircoon: {active_leagues}\n"
        "🚫 Kuwa la mamnuucay: {banned}\n\n"
        "Dooro xulashada:"
    ),
    "btn_broadcast":     "📢 Fariin u Dir Dhammaan",
    "btn_ban_user":      "🚫 Mamnuuc User",
    "btn_unban_user":    "✅ Ka Saar Mamnuucka",
    "btn_add_admin":     "➕ Kudar Admin",
    "btn_remove_admin":  "➖ Ka Saar Admin",
    "btn_view_stats":    "📊 Tirakoobka",
    "btn_active_leagues":"🏆 Kooxaha Firfircoon",
    "btn_export_data":   "💾 Soo Dajiso Xogta",
    "btn_maintenance":   "🔧 Dayactir Hab",
    "btn_modules":       "⚙️ Modulyada",
    "broadcast_sent":    "✅ Farintii waa la diray {count} isticmaaleyaasha.",
    "user_banned":       "🚫 @{user} waa la mamnuucay.",
    "user_unbanned":     "✅ @{user} mamnuucihii waa ka saaray.",
    "admin_added":       "✅ @{user} waa admin cusub.",
    "admin_removed":     "➖ @{user} adminnimadiisii waa ka saaray.",
    "maintenance_on":    "🔧 Bot-ka wuxuu galay xaalad dayactir. Isticmaalayaasha caadiga ah ma heli karaan.",
    "maintenance_off":   "✅ Dayactirkii waa dhamaaday. Bot-ku wuu soo noqday.",

    # ── Statistics ───────────────────────────────────────────
    "global_stats": (
        "📊 *Tirakoobka Guud*\n\n"
        "👥 *Isticmaalayaasha:* {total_users}\n"
        "🎮 *Ciyaarada Dhammaan:* {total_matches}\n"
        "📟 *Code-yada Oo Dhan:* {total_codes}\n"
        "🏆 *Kooxaha:* {total_leagues}\n"
        "💎 *Premium:* {premium_users}\n"
        "📅 *Maanta:*\n"
        "  👤 Cusub: {new_users_today}\n"
        "  🎮 Ciyaar: {matches_today}"
    ),

    # ── Leaderboard ──────────────────────────────────────────
    "leaderboard": (
        "🥇 *Daraja Guud — Adduunka*\n\n"
        "{entries}\n\n"
        "📅 Cusboonaysiinta: {updated}"
    ),
    "leaderboard_entry": "{rank}. {medal} @{username} — {wins}W/{losses}L",

    # ── Referral ─────────────────────────────────────────────
    "referral_info": (
        "🎁 *Nidaamka Raalli galinta*\n\n"
        "🔗 *Linkigaaga gaarka ah:*\n{link}\n\n"
        "👥 *Kuwa aad soo geysay:* {count}\n"
        "🎯 *Dhibcaha Raallinta:* {points}\n\n"
        "💡 Saaxiib kasta oo aad soo geliso waxaad helaysaa "
        "*{bonus} dhibcood* oo ah abaal!"
    ),
    "referral_success": (
        "🎉 @{referrer} ayaa kuu soo diray!\n"
        "🎁 Labadiin waxaydiin hesheen *{bonus} dhibcood*!"
    ),
}
