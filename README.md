# Miss Cherry 🍒 — Smart Group Moderator Bot
**Made by AlfaBots** | Professional Edition

---

## 📁 Project Structure

```
MissCherry/
├── main.py                   ← Entry point
├── config.env                ← Fill your credentials here
├── requirements.txt
│
├── core/                     ← Bot infrastructure
│   ├── config.py             ← Loads config.env
│   ├── database.py           ← MongoDB connection + all DB functions
│   ├── translator.py         ← i18n — reads from locales/
│   ├── filters.py            ← Custom Pyrogram filters
│   ├── logger.py             ← File + console logging
│   └── exceptions.py         ← Custom exceptions
│
├── utils/                    ← Reusable tools
│   ├── helpers.py            ← mention(), get_target_user()
│   ├── time_parser.py        ← "3h" → seconds
│   ├── keyboard.py           ← All inline keyboards
│   ├── string_helpers.py     ← fill_placeholders(), bl_pattern_to_regex()
│   └── chat_helpers.py       ← do_ban(), do_mute(), do_kick(), apply_action()
│
├── locales/                  ← Language files (i18n)
│   ├── en.json               ← English
│   ├── hi.json               ← Hindi
│   ├── bh.json               ← Bhojpuri
│   ├── ta.json               ← Tamil
│   ├── ar.json               ← Arabic
│   └── ru.json               ← Russian
│
└── modules/                  ← All bot features
    ├── start.py              ← /start /help + all callbacks
    ├── admin.py              ← /promote /demote /adminlist
    ├── antiflood.py          ← /setflood /floodmode + live tracker
    ├── antiraid.py           ← /antiraid /autoantiraid + join handler
    ├── approval.py           ← /approve /unapprove /approved
    ├── bans.py               ← /ban /mute /kick + variants
    ├── blocklist.py          ← /addblocklist + live scanner
    ├── filters_module.py     ← /filter /stop + live checker
    ├── greetings.py          ← /welcome /goodbye + member handler
    ├── warnings.py           ← /warn /warns /warnlimit
    ├── misc.py               ← rules/pin/purge/report/language/getlink
    ├── sudo_module.py        ← /addsudo /rmsudo /sudolist
    ├── chatbot.py            ← DeepSeek AI chatbot
    ├── games.py              ← WordSeek/WordChain/Hangman/Crossword/Wordle
    └── broadcast.py          ← /broadcast (owner/sudo only)
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Fill `config.env`
```env
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
OWNER_ID=123456789
DATABASE_URL=mongodb+srv://...
DEEPSEEK_API_KEY=your_key
START_IMG=https://your-image.jpg
SUPPORT_LINK=https://t.me/your_support
UPDATE_LINK=https://t.me/your_channel
DOCS_URL=https://your-docs.com
OWNER_USERNAME=@your_username
DEVELOPER_USERNAME=@dev_username
```

### 3. Run
```bash
python3 main.py
```

---

## 🌐 Language System (i18n)
- All bot output text is in `locales/*.json`
- **No hardcoded text in modules**
- To add a new language: create `locales/xx.json` with same keys as `en.json`
- Admin sets language with `/setlang hi` or via Language button

---

## 🤖 Chatbot Logic
- Direct group message (no reply/mention) → Miss Cherry replies
- Reply to another user → Miss Cherry stays silent
- Reply to Miss Cherry → She continues conversation
- History saved in MongoDB — **survives bot restarts**

---

## 📡 Broadcast
```
/broadcast          → Send to all groups + users
/broadcast groups   → Groups only
/broadcast users    → Users only
```
Reply to any media (text/photo/video/document/sticker) before using.

---

**Made with ❤️ by AlfaBots**
