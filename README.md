# ⚽ eFootball Friend Match Bot

> **Professional Telegram bot for eFootball Friend Match Challenges and Random Leagues.**
> Multi-language · Webhook-ready · SQLite persistent storage · Admin panel · Anti-spam

---

## 📁 Project Structure

```
efootball_bot/
├── main.py                  ← Entry point (polling or webhook)
├── wsgi.py                  ← Gunicorn WSGI entry (production)
├── Procfile                 ← Railway/Render deployment
├── requirements.txt
├── .env.example             ← Copy to .env and fill in values
├── .gitignore
│
├── config/
│   └── config.py            ← All bot settings (editable)
│
├── database/
│   └── db.py                ← SQLite manager (all CRUD functions)
│
├── modules/
│   ├── core.py              ← /start, /help, /profile, settings
│   ├── friend_match.py      ← Room code detection & claiming
│   ├── league.py            ← Random league/tournament system
│   └── admin.py             ← Admin panel & commands
│
├── languages/
│   ├── __init__.py          ← Language manager (get_text)
│   ├── so.py                ← 🇸🇴 Somali strings
│   ├── en.py                ← 🇬🇧 English strings
│   └── ar.py                ← 🇸🇦 Arabic strings
│
├── webhook/
│   └── server.py            ← Flask webhook server
│
└── utils/
    ├── helpers.py           ← Keyboards, formatters, validators
    ├── logger.py            ← Logging setup
    ├── backup.py            ← Auto database backup
    └── scheduler.py         ← Background tasks (code expiry)
```

---

## 🚀 Quick Start (Local Development)

### 1. Clone / Download the project

```bash
git clone https://github.com/hakimihk/friend-match-bot.git
cd friend-match-bot
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
nano .env                       # Edit with your values
```

**Minimum required values in `.env`:**

```env
BOT_TOKEN=your_bot_token_here
OWNER_ID=your_telegram_user_id
WEBHOOK_HOST=https://your-domain.com   # Not needed for polling
```

### 5. Run in polling mode (development)

```bash
python main.py --mode polling
```

---

## 🌐 Production Deployment (Webhook)

### Option A — Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables:
   - `BOT_TOKEN`
   - `OWNER_ID`
   - `WEBHOOK_HOST` → copy your Railway public URL
4. Railway auto-detects `Procfile` and starts Gunicorn
5. Bot goes live automatically ✅

---

### Option B — Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
5. Add environment variables (same as Railway)
6. Deploy ✅

---

### Option C — VPS (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update && sudo apt install python3 python3-pip python3-venv nginx certbot -y

# Clone project
git clone https://github.com/yourname/efootball-bot.git /opt/efootball_bot
cd /opt/efootball_bot

# Setup virtual env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
nano .env

# Create systemd service
sudo nano /etc/systemd/system/efootball.service
```

**Systemd service file:**

```ini
[Unit]
Description=eFootball Friend Match Bot
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/efootball_bot
Environment="PATH=/opt/efootball_bot/venv/bin"
ExecStart=/opt/efootball_bot/venv/bin/gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 1 --threads 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable efootball
sudo systemctl start efootball
sudo systemctl status efootball
```

**Nginx reverse proxy:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# SSL certificate
sudo certbot --nginx -d yourdomain.com

# Restart nginx
sudo systemctl restart nginx
```

---

### Option D — Katabump Hosting

1. Upload all project files via File Manager or SSH
2. Create `.env` file with your variables
3. Set start command: `python main.py --mode webhook`
4. Set your Katabump URL as `WEBHOOK_HOST`
5. Done ✅

---

## 👑 Admin Setup

### Step 1 — Set your Owner ID

In `.env`:
```env
OWNER_ID=123456789
```

Get your ID from [@userinfobot](https://t.me/userinfobot) on Telegram.

### Step 2 — Add more admins

As owner, use the command:
```
!addadmin USER_ID
```

Or via the Admin Panel → ➕ Add Admin (enter user ID when prompted).

### Admin Commands

| Command | Description |
|---|---|
| `!addadmin USER_ID` | Make a user admin |
| `!removeadmin USER_ID` | Remove admin rights |
| `!ban USER_ID` | Ban a user |
| `!unban USER_ID` | Unban a user |
| `!broadcast Your message` | Send to all users |
| `!stats` | View global statistics |
| `!leagues` | View active leagues |
| `!maintenance` | Toggle maintenance mode |
| `!clearchat` | Delete recent messages |
| `!help` | Admin help menu |

---

## 🌐 Multi-Language System

Three languages are supported out of the box:

| Code | Language | Flag |
|---|---|---|
| `so` | Somali (default) | 🇸🇴 |
| `en` | English | 🇬🇧 |
| `ar` | Arabic | 🇸🇦 |

**To add a new language:**
1. Copy `languages/en.py` → `languages/fr.py`
2. Translate all string values
3. Add to `LANGUAGE_MODULES` in `languages/__init__.py`
4. Add to `LANGUAGE_NAMES` dict

---

## 🎮 Feature Overview

### Friend Match Challenge (Groups)
- Post an 8-digit eFootball room code in the group
- Bot auto-detects, validates, and deletes the raw message
- Displays styled card with **Claim** button
- Other player clicks Claim → code is marked taken
- Anti-duplicate, cooldown (30s), hourly limit, anti-spam protection

### Random League System
- Create leagues: 4 / 8 / 16 players
- Two modes: **Knockout** and **Round Robin**
- Unique PIN generated for each league
- Players join via `/joinleague PIN` or button
- When full → players shuffled → fixtures generated automatically
- Beautiful bracket display

### Profile & Ranking
- Tracks wins, losses, codes posted/claimed, points
- Global leaderboard (`/leaderboard`)
- User rank display in profile

### Referral System
- Unique invite link per user
- Both referrer and referred earn bonus points
- `/refer` command to get your link

### Premium System
- Premium badge in profile
- Ready for payment integration expansion

---

## ⚙️ Configuration Reference

All settings are in `config/config.py`:

| Setting | Default | Description |
|---|---|---|
| `ROOM_CODE_LENGTH` | `8` | eFootball code digit count |
| `CODE_EXPIRY_SECONDS` | `300` | Auto-expire unclaimed codes (5 min) |
| `COOLDOWN_SECONDS` | `30` | Wait between posting codes |
| `MAX_CODES_PER_HOUR` | `10` | Hourly code posting limit |
| `ANTI_SPAM_LIMIT` | `5` | Messages before mute triggers |
| `LEAGUE_SIZES` | `[4, 8, 16]` | Available tournament sizes |
| `BACKUP_INTERVAL_HOURS` | `6` | Auto-backup frequency |
| `REFERRAL_BONUS_POINTS` | `50` | Points per successful referral |
| `DEFAULT_LANGUAGE` | `"so"` | Default user language |

---

## 🛡️ Security Features

- ✅ Anti-flood & anti-spam (rate limiting + auto-mute)
- ✅ Per-user cooldowns on code posting
- ✅ Hourly code limits
- ✅ Duplicate code detection per chat
- ✅ Ban/unban system
- ✅ Maintenance mode (blocks non-admins)
- ✅ Module enable/disable switches
- ✅ Admin permission checks on all sensitive operations
- ✅ Owner-only protections
- ✅ Full error handling with logging

---

## 🗄️ Database Tables

| Table | Purpose |
|---|---|
| `users` | User profiles, stats, language, premium |
| `admins` | Admin user IDs |
| `room_codes` | Code history (posted, claimed, expired) |
| `cooldowns` | Per-user cooldown & hourly counters |
| `spam_log` | Recent message log for spam detection |
| `leagues` | Tournament data (players, fixtures, results) |
| `match_results` | Individual match outcomes |
| `settings` | Bot-wide settings (maintenance, modules) |
| `daily_stats` | Daily statistics counters |

---

## 🐛 Troubleshooting

**Bot not responding?**
- Check `logs/bot.log` for errors
- Verify `BOT_TOKEN` is correct
- Ensure webhook URL is HTTPS and publicly reachable

**Webhook not setting?**
- Your `WEBHOOK_HOST` must be a valid HTTPS URL
- Port 443, 80, 88, or 8443 must be open
- Try polling mode first to confirm bot token works

**Database errors?**
- Ensure `database/` directory exists
- Check file write permissions

**Codes not being detected?**
- Bot must be an admin in the group (to delete messages)
- Messages must contain exactly 8 consecutive digits

---

## 📞 Support

Configured in `config/config.py`:
```python
DEVELOPER_CONTACT = "@YourUsername"
```

---

## 📄 License

MIT License — Free to use, modify, and distribute.
