"""
=============================================================
 Database Manager
 Uses SQLite for persistent storage.
 All data survives bot restarts.
=============================================================
"""

import sqlite3
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from config.config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection with row_factory enabled."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Rows accessible like dicts
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent writes
    return conn


def initialize_database():
    """Create all tables if they don't exist. Called on bot startup."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Users table ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            username        TEXT,
            first_name      TEXT,
            last_name       TEXT,
            language        TEXT    DEFAULT 'so',
            is_banned       INTEGER DEFAULT 0,
            is_muted        INTEGER DEFAULT 0,
            mute_until      TEXT,
            is_premium      INTEGER DEFAULT 0,
            premium_until   TEXT,
            is_admin        INTEGER DEFAULT 0,
            points          INTEGER DEFAULT 0,
            wins            INTEGER DEFAULT 0,
            losses          INTEGER DEFAULT 0,
            codes_sent      INTEGER DEFAULT 0,
            codes_claimed   INTEGER DEFAULT 0,
            total_matches   INTEGER DEFAULT 0,
            referred_by     INTEGER,
            referral_count  INTEGER DEFAULT 0,
            joined_at       TEXT    DEFAULT (datetime('now')),
            last_seen       TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Admins table (separate for quick lookup) ──────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id     INTEGER PRIMARY KEY,
            added_by    INTEGER,
            added_at    TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Room codes table ─────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_codes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    NOT NULL,
            sender_id   INTEGER NOT NULL,
            claimer_id  INTEGER,
            chat_id     INTEGER NOT NULL,
            message_id  INTEGER,
            status      TEXT    DEFAULT 'active',  -- active/claimed/expired
            posted_at   TEXT    DEFAULT (datetime('now')),
            claimed_at  TEXT,
            expires_at  TEXT
        )
    """)

    # ── Cooldowns table ──────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id     INTEGER PRIMARY KEY,
            last_code   TEXT,
            count_hour  INTEGER DEFAULT 0,
            hour_reset  TEXT
        )
    """)

    # ── Spam tracking table ──────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spam_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            msg_time    TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Leagues table ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pin         TEXT    UNIQUE NOT NULL,
            creator_id  INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            mode        TEXT    NOT NULL,  -- knockout/round_robin
            max_players INTEGER NOT NULL,
            status      TEXT    DEFAULT 'waiting',  -- waiting/active/completed
            players     TEXT    DEFAULT '[]',       -- JSON list of user_ids
            fixtures    TEXT    DEFAULT '[]',       -- JSON list of match pairs
            results     TEXT    DEFAULT '{}',       -- JSON {match_id: result}
            created_at  TEXT    DEFAULT (datetime('now')),
            started_at  TEXT,
            ended_at    TEXT
        )
    """)

    # ── Match results table ──────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id   INTEGER NOT NULL,
            round_num   INTEGER NOT NULL,
            player1_id  INTEGER NOT NULL,
            player2_id  INTEGER NOT NULL,
            winner_id   INTEGER,
            score       TEXT,
            reported_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Settings table ───────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key     TEXT PRIMARY KEY,
            value   TEXT NOT NULL
        )
    """)

    # ── Statistics (daily) ───────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            date            TEXT PRIMARY KEY,
            new_users       INTEGER DEFAULT 0,
            matches_played  INTEGER DEFAULT 0,
            codes_posted    INTEGER DEFAULT 0,
            leagues_created INTEGER DEFAULT 0
        )
    """)

    # Insert default settings if not present
    defaults = {
        "maintenance_mode":      "0",
        "module_friend_match":   "1",
        "module_random_league":  "1",
        "module_premium":        "1",
        "module_referral":       "1",
        "module_ai_moderation":  "1",
        "code_expiry_seconds":   "300",
        "cooldown_seconds":      "30",
    }
    for key, value in defaults.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    conn.commit()
    conn.close()
    logger.info("✅ Database initialized successfully.")


# ════════════════════════════════════════════════════════════
#  USER FUNCTIONS
# ════════════════════════════════════════════════════════════

def upsert_user(user_id: int, username: str = None,
                first_name: str = None, last_name: str = None) -> None:
    """Insert or update a user record. Called on every interaction."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username   = excluded.username,
            first_name = excluded.first_name,
            last_name  = excluded.last_name,
            last_seen  = datetime('now')
    """, (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()


def get_user(user_id: int) -> Optional[Dict]:
    """Fetch a user record by ID. Returns None if not found."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def set_user_language(user_id: int, lang: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()


def get_user_language(user_id: int) -> str:
    conn = get_connection()
    row = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row["language"] if row else "so"


def ban_user(user_id: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def unban_user(user_id: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_user_banned(user_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return bool(row["is_banned"]) if row else False


def mute_user(user_id: int, seconds: int) -> None:
    until = (datetime.utcnow() + timedelta(seconds=seconds)).isoformat()
    conn = get_connection()
    conn.execute("UPDATE users SET is_muted = 1, mute_until = ? WHERE user_id = ?", (until, user_id))
    conn.commit()
    conn.close()


def is_user_muted(user_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT is_muted, mute_until FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row or not row["is_muted"]:
        return False
    if row["mute_until"] and datetime.fromisoformat(row["mute_until"]) < datetime.utcnow():
        # Mute expired; clear it
        c2 = get_connection()
        c2.execute("UPDATE users SET is_muted = 0, mute_until = NULL WHERE user_id = ?", (user_id,))
        c2.commit()
        c2.close()
        return False
    return True


def get_all_users() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_count() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count


def get_banned_count() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1").fetchone()[0]
    conn.close()
    return count


def add_points(user_id: int, points: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()
    conn.close()


def record_win(winner_id: int, loser_id: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE users SET wins = wins + 1, total_matches = total_matches + 1 WHERE user_id = ?", (winner_id,))
    conn.execute("UPDATE users SET losses = losses + 1, total_matches = total_matches + 1 WHERE user_id = ?", (loser_id,))
    conn.commit()
    conn.close()


def get_leaderboard(limit: int = 10) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT user_id, username, wins, losses FROM users ORDER BY wins DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_rank(user_id: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) + 1 as rank FROM users WHERE wins > (SELECT wins FROM users WHERE user_id = ?)",
        (user_id,)
    ).fetchone()
    conn.close()
    return row["rank"] if row else 0


# ════════════════════════════════════════════════════════════
#  ADMIN FUNCTIONS
# ════════════════════════════════════════════════════════════

def add_admin(user_id: int, added_by: int) -> None:
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)", (user_id, added_by))
    conn.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def remove_admin(user_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    conn.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_admin(user_id: int) -> bool:
    from config.config import OWNER_ID
    if user_id == OWNER_ID:
        return True
    conn = get_connection()
    row = conn.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row is not None


# ════════════════════════════════════════════════════════════
#  ROOM CODE FUNCTIONS
# ════════════════════════════════════════════════════════════

def save_room_code(code: str, sender_id: int, chat_id: int,
                   message_id: int, expiry_seconds: int) -> int:
    expires_at = (datetime.utcnow() + timedelta(seconds=expiry_seconds)).isoformat()
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO room_codes (code, sender_id, chat_id, message_id, expires_at)
           VALUES (?, ?, ?, ?, ?)""",
        (code, sender_id, chat_id, message_id, expires_at)
    )
    conn.execute("UPDATE users SET codes_sent = codes_sent + 1 WHERE user_id = ?", (sender_id,))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    _bump_daily_stat("codes_posted")
    return row_id


def get_active_code(code: str, chat_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM room_codes
           WHERE code = ? AND chat_id = ? AND status = 'active'
           AND expires_at > datetime('now')
           ORDER BY posted_at DESC LIMIT 1""",
        (code, chat_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_code_by_message(message_id: int, chat_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM room_codes WHERE message_id = ? AND chat_id = ?",
        (message_id, chat_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def claim_code(code_id: int, claimer_id: int) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT status FROM room_codes WHERE id = ?", (code_id,)
    ).fetchone()
    if not row or row["status"] != "active":
        conn.close()
        return False
    conn.execute(
        """UPDATE room_codes SET status = 'claimed', claimer_id = ?, claimed_at = datetime('now')
           WHERE id = ?""",
        (claimer_id, code_id)
    )
    conn.execute("UPDATE users SET codes_claimed = codes_claimed + 1 WHERE user_id = ?", (claimer_id,))
    conn.commit()
    conn.close()
    _bump_daily_stat("matches_played")
    return True


def is_code_duplicate(code: str, chat_id: int) -> bool:
    conn = get_connection()
    row = conn.execute(
        """SELECT id FROM room_codes
           WHERE code = ? AND chat_id = ? AND status = 'active'
           AND expires_at > datetime('now')""",
        (code, chat_id)
    ).fetchone()
    conn.close()
    return row is not None


def expire_old_codes() -> int:
    """Mark all expired active codes as 'expired'. Returns count expired."""
    conn = get_connection()
    cursor = conn.execute(
        """UPDATE room_codes SET status = 'expired'
           WHERE status = 'active' AND expires_at < datetime('now')"""
    )
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


# ════════════════════════════════════════════════════════════
#  COOLDOWN & ANTI-SPAM
# ════════════════════════════════════════════════════════════

def check_and_set_cooldown(user_id: int, cooldown_secs: int) -> Optional[int]:
    """
    Check if user is in cooldown.
    Returns remaining seconds if in cooldown, else None (and sets cooldown).
    """
    conn = get_connection()
    row = conn.execute("SELECT last_code FROM cooldowns WHERE user_id = ?", (user_id,)).fetchone()
    now = datetime.utcnow()
    if row and row["last_code"]:
        last = datetime.fromisoformat(row["last_code"])
        diff = (now - last).total_seconds()
        if diff < cooldown_secs:
            conn.close()
            return int(cooldown_secs - diff)
    conn.execute(
        "INSERT OR REPLACE INTO cooldowns (user_id, last_code) VALUES (?, ?)",
        (user_id, now.isoformat())
    )
    conn.commit()
    conn.close()
    return None


def check_hourly_limit(user_id: int, max_per_hour: int) -> bool:
    """Returns True if user has exceeded hourly code limit."""
    conn = get_connection()
    row = conn.execute("SELECT count_hour, hour_reset FROM cooldowns WHERE user_id = ?", (user_id,)).fetchone()
    now = datetime.utcnow()
    if row:
        reset = datetime.fromisoformat(row["hour_reset"]) if row["hour_reset"] else now - timedelta(hours=2)
        if (now - reset).total_seconds() > 3600:
            conn.execute("UPDATE cooldowns SET count_hour = 1, hour_reset = ? WHERE user_id = ?",
                         (now.isoformat(), user_id))
            conn.commit()
            conn.close()
            return False
        if row["count_hour"] >= max_per_hour:
            conn.close()
            return True
        conn.execute("UPDATE cooldowns SET count_hour = count_hour + 1 WHERE user_id = ?", (user_id,))
    else:
        conn.execute("INSERT OR IGNORE INTO cooldowns (user_id, count_hour, hour_reset) VALUES (?, 1, ?)",
                     (user_id, now.isoformat()))
    conn.commit()
    conn.close()
    return False


def log_message(user_id: int, chat_id: int) -> int:
    """Log a message for spam detection. Returns message count in spam window."""
    conn = get_connection()
    conn.execute("INSERT INTO spam_log (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id))
    # Clean old entries
    conn.execute("DELETE FROM spam_log WHERE msg_time < datetime('now', '-60 seconds')")
    row = conn.execute(
        "SELECT COUNT(*) FROM spam_log WHERE user_id = ? AND chat_id = ? AND msg_time > datetime('now', '-60 seconds')",
        (user_id, chat_id)
    ).fetchone()
    conn.commit()
    count = row[0]
    conn.close()
    return count


# ════════════════════════════════════════════════════════════
#  LEAGUE FUNCTIONS
# ════════════════════════════════════════════════════════════

def create_league(pin: str, creator_id: int, chat_id: int,
                  mode: str, max_players: int) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO leagues (pin, creator_id, chat_id, mode, max_players, players)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (pin, creator_id, chat_id, mode, max_players, json.dumps([creator_id]))
    )
    conn.commit()
    league_id = cursor.lastrowid
    conn.close()
    _bump_daily_stat("leagues_created")
    return league_id


def get_league(pin: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM leagues WHERE pin = ?", (pin,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["players"] = json.loads(d["players"])
    d["fixtures"] = json.loads(d["fixtures"])
    d["results"] = json.loads(d["results"])
    return d


def join_league(pin: str, user_id: int) -> Dict:
    """
    Add user to league. Returns dict with status and updated league.
    status: 'joined' | 'already_in' | 'full' | 'not_found' | 'started'
    """
    conn = get_connection()
    row = conn.execute("SELECT * FROM leagues WHERE pin = ?", (pin,)).fetchone()
    if not row:
        conn.close()
        return {"status": "not_found"}
    league = dict(row)
    players = json.loads(league["players"])
    if user_id in players:
        conn.close()
        return {"status": "already_in"}
    if len(players) >= league["max_players"]:
        conn.close()
        return {"status": "full"}
    if league["status"] != "waiting":
        conn.close()
        return {"status": "started"}
    players.append(user_id)
    conn.execute("UPDATE leagues SET players = ? WHERE pin = ?", (json.dumps(players), pin))
    if len(players) == league["max_players"]:
        # League is full — generate fixtures
        import random
        random.shuffle(players)
        fixtures = _generate_fixtures(players, league["mode"])
        conn.execute(
            "UPDATE leagues SET players = ?, fixtures = ?, status = 'active', started_at = datetime('now') WHERE pin = ?",
            (json.dumps(players), json.dumps(fixtures), pin)
        )
    conn.commit()
    conn.close()
    return {"status": "joined", "league": get_league(pin)}


def _generate_fixtures(players: list, mode: str) -> list:
    """Generate match fixtures for knockout or round-robin."""
    fixtures = []
    if mode == "knockout":
        # Pair up for round 1
        pairs = [(players[i], players[i + 1]) for i in range(0, len(players), 2)]
        fixtures.append({"round": 1, "matches": [{"p1": p[0], "p2": p[1], "winner": None} for p in pairs]})
    elif mode == "round_robin":
        # Everyone plays everyone
        matches = []
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                matches.append({"p1": players[i], "p2": players[j], "winner": None, "score": None})
        fixtures.append({"round": 1, "matches": matches})
    return fixtures


def report_match_result(pin: str, winner_id: int, loser_id: int, score: str) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT * FROM leagues WHERE pin = ?", (pin,)).fetchone()
    if not row:
        conn.close()
        return False
    conn.execute(
        """INSERT INTO match_results (league_id, round_num, player1_id, player2_id, winner_id, score)
           VALUES (?, 1, ?, ?, ?, ?)""",
        (row["id"], winner_id, loser_id, winner_id, score)
    )
    conn.commit()
    conn.close()
    record_win(winner_id, loser_id)
    return True


def get_active_leagues(chat_id: int = None) -> List[Dict]:
    conn = get_connection()
    if chat_id:
        rows = conn.execute(
            "SELECT * FROM leagues WHERE status != 'completed' AND chat_id = ?", (chat_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM leagues WHERE status != 'completed'").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["players"] = json.loads(d["players"])
        result.append(d)
    return result


def get_user_leagues(user_id: int) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM leagues WHERE status != 'completed'").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["players"] = json.loads(d["players"])
        if user_id in d["players"]:
            result.append(d)
    return result


# ════════════════════════════════════════════════════════════
#  SETTINGS FUNCTIONS
# ════════════════════════════════════════════════════════════

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def is_maintenance() -> bool:
    return get_setting("maintenance_mode", "0") == "1"


def is_module_enabled(module: str) -> bool:
    return get_setting(f"module_{module}", "1") == "1"


# ════════════════════════════════════════════════════════════
#  STATISTICS FUNCTIONS
# ════════════════════════════════════════════════════════════

def _bump_daily_stat(field: str) -> None:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_connection()
    conn.execute(f"INSERT OR IGNORE INTO daily_stats (date) VALUES (?)", (today,))
    conn.execute(f"UPDATE daily_stats SET {field} = {field} + 1 WHERE date = ?", (today,))
    conn.commit()
    conn.close()


def get_today_stats() -> Dict:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_connection()
    row = conn.execute("SELECT * FROM daily_stats WHERE date = ?", (today,)).fetchone()
    conn.close()
    return dict(row) if row else {
        "date": today, "new_users": 0, "matches_played": 0,
        "codes_posted": 0, "leagues_created": 0
    }


def get_global_stats() -> Dict:
    conn = get_connection()
    total_users    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_matches  = conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0]
    total_codes    = conn.execute("SELECT COUNT(*) FROM room_codes").fetchone()[0]
    total_leagues  = conn.execute("SELECT COUNT(*) FROM leagues").fetchone()[0]
    premium_users  = conn.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1").fetchone()[0]
    conn.close()
    today = get_today_stats()
    return {
        "total_users":    total_users,
        "total_matches":  total_matches,
        "total_codes":    total_codes,
        "total_leagues":  total_leagues,
        "premium_users":  premium_users,
        "new_users_today": today["new_users"],
        "matches_today":   today["matches_played"],
    }


# ════════════════════════════════════════════════════════════
#  REFERRAL FUNCTIONS
# ════════════════════════════════════════════════════════════

def set_referral(referred_id: int, referrer_id: int) -> bool:
    """Link referred user to referrer. Returns True if first time."""
    conn = get_connection()
    row = conn.execute("SELECT referred_by FROM users WHERE user_id = ?", (referred_id,)).fetchone()
    if row and row["referred_by"]:
        conn.close()
        return False
    conn.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referrer_id, referred_id))
    conn.execute("UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?", (referrer_id,))
    conn.commit()
    conn.close()
    return True
