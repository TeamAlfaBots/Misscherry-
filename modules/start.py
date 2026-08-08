# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Start Module          ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from core.config import cfg
from core.translator import _
from core.database import set_language, save_chat, save_user
from utils.helpers import mention
from utils.keyboard import start_kb, help_kb, info_kb, lang_kb, back_close_kb
from utils.log_reporter import log_bot_started


# ══════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════

@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    user = message.from_user
    await save_user(user.id, user.username)
    text = await _(0, "start.welcome", name=mention(user))
    if cfg.START_IMG:
        await message.reply_photo(photo=cfg.START_IMG, caption=text, reply_markup=start_kb())
    else:
        await message.reply_text(text, reply_markup=start_kb())


@Client.on_message(filters.command("start") & ~filters.private)
async def start_group(client: Client, message: Message):
    from core.logger import logger
    logger.info(f"🐞 start_group HANDLER TRIGGERED chat_id={message.chat.id}")
    try:
        user = message.from_user
        await save_chat(message.chat.id, message.chat.title)
        await save_user(user.id, user.username)
        await log_bot_started(client, message)
        text = await _(message.chat.id, "start.group_welcome", name=mention(user))
        await message.reply_text(text, reply_markup=start_kb())
        logger.info("🐞 start_group COMPLETED successfully")
    except Exception as e:
        logger.info(f"🐞 start_group CRASHED: {e!r}")


# ══════════════════════════════════════════════
#  /help
# ══════════════════════════════════════════════

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        "📚 **Miss Cherry Help Menu**\n\nChoose a module:",
        reply_markup=help_kb()
    )


# ══════════════════════════════════════════════
#  CALLBACKS
# ══════════════════════════════════════════════

@Client.on_callback_query(filters.regex("^start_menu$"))
async def cb_start(client: Client, query: CallbackQuery):
    user = query.from_user
    text = await _(0, "start.welcome", name=mention(user))
    try:
        if cfg.START_IMG and query.message.photo:
            await query.message.edit_caption(caption=text, reply_markup=start_kb())
        else:
            await query.message.edit_text(text, reply_markup=start_kb())
    except Exception:
        pass


@Client.on_callback_query(filters.regex("^help_menu$"))
async def cb_help(client: Client, query: CallbackQuery):
    text = "📚 **Miss Cherry Help Menu**\n\nChoose a module:"
    try:
        if query.message.photo:
            await query.message.edit_caption(caption=text, reply_markup=help_kb())
        else:
            await query.message.edit_text(text, reply_markup=help_kb())
    except Exception as e:
        print(f"[cb_help] Error: {e}")


@Client.on_callback_query(filters.regex("^info_menu$"))
async def cb_info(client: Client, query: CallbackQuery):
    text = await _(query.message.chat.id, "info.title")
    try:
        if query.message.photo:
            await query.message.edit_caption(caption=text, reply_markup=info_kb())
        else:
            await query.message.edit_text(text, reply_markup=info_kb())
    except Exception as e:
        print(f"[cb_info] Error: {e}")


@Client.on_callback_query(filters.regex("^lang_menu$"))
async def cb_lang_menu(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    text = await _(chat_id, "language.current", lang="Current")
    try:
        if query.message.photo:
            await query.message.edit_caption(caption=text, reply_markup=lang_kb())
        else:
            await query.message.edit_text(text, reply_markup=lang_kb())
    except Exception as e:
        print(f"[cb_lang_menu] Error: {e}")


@Client.on_callback_query(filters.regex(r"^setlang_(\w+)$"))
async def cb_setlang(client: Client, query: CallbackQuery):
    lang = query.data.split("_")[1]
    chat_id = query.message.chat.id
    await set_language(chat_id, lang)
    text = await _(chat_id, "language.set", lang=lang.upper())
    await query.answer(text, show_alert=False)
    new_text = await _(chat_id, "language.current", lang=lang.upper())
    try:
        if query.message.photo:
            await query.message.edit_caption(caption=new_text, reply_markup=lang_kb())
        else:
            await query.message.edit_text(new_text, reply_markup=lang_kb())
    except Exception as e:
        print(f"[cb_setlang] Error: {e}")


@Client.on_callback_query(filters.regex("^close$"))
async def cb_close(client: Client, query: CallbackQuery):
    await query.message.delete()


# ── Help module callbacks ──────────────────────
HELP_TEXTS = {
    "admin": """👮 **Admin**

Make it easy to promote and demote users!

**Commands:**
- `/promote` — Promote a user
- `/demote` — Demote a user
- `/adminlist` — List all admins
- `/admincache` — Refresh admin cache
- `/anonadmin` <yes/no> — Allow anon admins
- `/adminerror` <yes/no> — Show error to normal users""",

    "antiflood": """🌊 **Antiflood**

Stop users from flooding the chat!

**Commands:**
- `/flood` — View current settings
- `/setflood` <number/off> — Set message limit
- `/setfloodtimer` <count> <time> — Set timed flood
- `/floodmode` <ban/mute/kick/tban/tmute> — Set action
- `/clearflood` <yes/no> — Delete flood messages""",

    "antiraid": """🛡 **AntiRaid**

Stop raid attacks on your group!

**Commands:**
- `/antiraid` <time/off> — Toggle antiraid
- `/raidtime` <time> — Set raid duration
- `/raidactiontime` <time> — Set ban duration
- `/autoantiraid` <number/off> — Auto trigger""",

    "approval": """✅ **Approval**

Trust certain users to bypass restrictions!

**Commands:**
- `/approval` — Check approval status
- `/approve` — Approve a user
- `/unapprove` — Unapprove a user
- `/approved` — List approved users
- `/unapproveall` — Remove all approvals""",

    "bans": """🔨 **Bans**

Ban, mute, and kick users!

**Commands:**
- `/ban` `/dban` `/sban` — Ban user
- `/tban` <time> — Temp ban
- `/unban` — Unban user
- `/mute` `/dmute` `/smute` — Mute user
- `/tmute` <time> — Temp mute
- `/unmute` — Unmute user
- `/kick` `/dkick` `/skick` — Kick user
- `/kickme` — Kick yourself""",

    "blocklist": """🚫 **Blocklist**

Block specific words and patterns!

**Commands:**
- `/addblocklist` <trigger> — Add trigger
- `/rmblocklist` <trigger> — Remove trigger
- `/unblocklistall` — Clear all (creator only)
- `/blocklist` — List all triggers
- `/blocklistmode` <mode> — Set action
- `/blocklistdelete` <yes/no> — Delete messages
- `/setblocklistreason` <reason> — Set reason

**Patterns:** `?` `*` `**`""",

    "filters": """🔍 **Filters**

Auto-reply to trigger words!

**Commands:**
- `/filter` <trigger> <reply> — Add filter
- `/filters` — List all filters
- `/stop` <trigger> — Remove filter
- `/stopall` — Remove all filters""",

    "greetings": """👋 **Greetings**

Welcome new members!

**Commands:**
- `/welcome` <yes/no> — Toggle welcome
- `/goodbye` <yes/no> — Toggle goodbye
- `/setwelcome` <text> — Set welcome message
- `/resetwelcome` — Reset welcome
- `/setgoodbye` <text> — Set goodbye message
- `/resetgoodbye` — Reset goodbye
- `/cleanwelcome` <yes/no> — Auto-delete old welcomes

**Fillings:** `{mention}` `{first}` `{username}` `{chatname}` `{id}`""",

    "language": """🌐 **Language**

Change bot reply language!

**Available:**
🇬🇧 EN | 🇮🇳 HI | 🇮🇳 BH | 🇮🇳 TA | 🇸🇦 AR | 🇷🇺 RU

**Commands:**
- `/setlang` <code> — Set language""",

    "pin": """📌 **Pin**

Pin and manage messages!

**Commands:**
- `/pinned` — Get pinned message
- `/pin` — Pin replied message
- `/permapin` <text> — Pin custom message
- `/unpin` — Unpin message
- `/unpinall` — Unpin all
- `/antichannelpin` <yes/no> — Stop auto-pin
- `/cleanlinked` <yes/no> — Delete linked channel messages""",

    "purge": """🗑 **Purge**

Delete many messages at once!

**Commands:**
- `/purge` — Delete from reply to now
- `/purge <X>` — Delete X messages
- `/spurge` — Silent purge
- `/del` — Delete replied message
- `/purgefrom` — Mark start point
- `/purgeto` — Delete from start to here""",

    "report": """🚨 **Report**

Let users report rule-breakers!

**User Commands:**
- `/report` — Report a message (reply)
- `@admin` — Same as /report

**Admin Commands:**
- `/reports` <yes/no> — Enable/disable reports""",

    "rules": """📜 **Rules**

Set and manage group rules!

**User Commands:**
- `/rules` — View rules

**Admin Commands:**
- `/setrules` <text> — Set rules
- `/resetrules` — Reset rules
- `/privaterules` <yes/no> — Send rules in PM""",

    "warning": """⚠️ **Warnings**

Keep members in check!

**Commands:**
- `/warn` <reason> — Warn a user
- `/dwarn` — Warn + delete message
- `/swarn` — Silent warn
- `/warns` — View user's warnings
- `/rmwarn` — Remove last warning
- `/resetwarn` — Reset user warnings
- `/resetallwarns` — Reset all warnings
- `/warnmode` <mode> — Set warn action
- `/warnlimit` <number> — Set warn limit
- `/warntime` <time> — Set warn expiry""",

    "getlink": """🔗 **Getlink**

Fetch invite links of all groups!

**Commands:**
- `/getlink` — List all group links

**Output:**
```
1.
Chat: GroupName
ID: -100xxx
Link: t.me/joinchat/...
```""",

    "sudo": """🔑 **Sudo**

Grant trusted users owner-level access!

**Owner Commands:**
- `/addsudo` — Add sudo user
- `/rmsudo` — Remove sudo user
- `/sudolist` — List all sudo users""",

    "games": """🎮 **Word Games**

Fun games for your group!

🔎 **Word Seek:** `/wordseek`
🔗 **Word Chain:** `/wordchain`
🙈 **Hangman:** `/hangman`
🧩 **Crossword:** `/crossword`
🟩 **Wordle:** `/wordle`

Each game supports: `hint` `skip` `stop` `stats`""",

    "chatbot": """🤖 **Chatbot** (DeepSeek AI)

Miss Cherry chats with your members!

**Commands:**
- `/chatbot on` — Enable
- `/chatbot off` — Disable (default)

**Smart Logic:**
• Direct message → Miss Cherry replies 🍒
• Reply to another user → Miss Cherry stays silent 🤫
• Chat history saved in DB — survives restarts! 🧠"""
}


@Client.on_callback_query(filters.regex(r"^help_(\w+)$"))
async def cb_help_module(client: Client, query: CallbackQuery):
    module = query.data.replace("help_", "")
    text = HELP_TEXTS.get(module, "❌ Module not found.")
    try:
        if query.message.photo:
            await query.message.edit_caption(
                caption=text,
                reply_markup=back_close_kb("help_menu")
            )
        else:
            await query.message.edit_text(
                text,
                reply_markup=back_close_kb("help_menu"),
                parse_mode="markdown"
            )
    except Exception as e:
        print(f"[cb_help_module] Error: {e}")
