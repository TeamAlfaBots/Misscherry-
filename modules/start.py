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
        "📚 <b>Miss Cherry Help Menu</b>\n\nChoose a module:",
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
    text = "📚 <b>Miss Cherry Help Menu</b>\n\nChoose a module:"
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
    "admin": """👮 <b>Admin</b>

Make it easy to promote and demote users!

<b>Commands:</b>
- <code>/promote</code> — Promote a user
- <code>/demote</code> — Demote a user
- <code>/adminlist</code> — List all admins
- <code>/admincache</code> — Refresh admin cache
- <code>/anonadmin</code> <yes/no> — Allow anon admins
- <code>/adminerror</code> <yes/no> — Show error to normal users""",

    "antiflood": """🌊 <b>Antiflood</b>

Stop users from flooding the chat!

<b>Commands:</b>
- <code>/flood</code> — View current settings
- <code>/setflood</code> <number/off> — Set message limit
- <code>/setfloodtimer</code> <count> <time> — Set timed flood
- <code>/floodmode</code> <ban/mute/kick/tban/tmute> — Set action
- <code>/clearflood</code> <yes/no> — Delete flood messages""",

    "antiraid": """🛡 <b>AntiRaid</b>

Stop raid attacks on your group!

<b>Commands:</b>
- <code>/antiraid</code> <time/off> — Toggle antiraid
- <code>/raidtime</code> <time> — Set raid duration
- <code>/raidactiontime</code> <time> — Set ban duration
- <code>/autoantiraid</code> <number/off> — Auto trigger""",

    "approval": """✅ <b>Approval</b>

Trust certain users to bypass restrictions!

<b>Commands:</b>
- <code>/approval</code> — Check approval status
- <code>/approve</code> — Approve a user
- <code>/unapprove</code> — Unapprove a user
- <code>/approved</code> — List approved users
- <code>/unapproveall</code> — Remove all approvals""",

    "bans": """🔨 <b>Bans</b>

Ban, mute, and kick users!

<b>Commands:</b>
- <code>/ban</code> <code>/dban</code> <code>/sban</code> — Ban user
- <code>/tban</code> <time> — Temp ban
- <code>/unban</code> — Unban user
- <code>/mute</code> <code>/dmute</code> <code>/smute</code> — Mute user
- <code>/tmute</code> <time> — Temp mute
- <code>/unmute</code> — Unmute user
- <code>/kick</code> <code>/dkick</code> <code>/skick</code> — Kick user
- <code>/kickme</code> — Kick yourself""",

    "blocklist": """🚫 <b>Blocklist</b>

Block specific words and patterns!

<b>Commands:</b>
- <code>/addblocklist</code> <trigger> — Add trigger
- <code>/rmblocklist</code> <trigger> — Remove trigger
- <code>/unblocklistall</code> — Clear all (creator only)
- <code>/blocklist</code> — List all triggers
- <code>/blocklistmode</code> <mode> — Set action
- <code>/blocklistdelete</code> <yes/no> — Delete messages
- <code>/setblocklistreason</code> <reason> — Set reason

<b>Patterns:</b> <code>?</code> <code>*</code> <code>**</code>""",

    "filters": """🔍 <b>Filters</b>

Auto-reply to trigger words!

<b>Commands:</b>
- <code>/filter</code> <trigger> <reply> — Add filter
- <code>/filters</code> — List all filters
- <code>/stop</code> <trigger> — Remove filter
- <code>/stopall</code> — Remove all filters""",

    "greetings": """👋 <b>Greetings</b>

Welcome new members!

<b>Commands:</b>
- <code>/welcome</code> <yes/no> — Toggle welcome
- <code>/goodbye</code> <yes/no> — Toggle goodbye
- <code>/setwelcome</code> <text> — Set welcome message
- <code>/resetwelcome</code> — Reset welcome
- <code>/setgoodbye</code> <text> — Set goodbye message
- <code>/resetgoodbye</code> — Reset goodbye
- <code>/cleanwelcome</code> <yes/no> — Auto-delete old welcomes

<b>Fillings:</b> <code>{mention}</code> <code>{first}</code> <code>{username}</code> <code>{chatname}</code> <code>{id}</code>""",

    "language": """🌐 <b>Language</b>

Change bot reply language!

<b>Available:</b>
🇬🇧 EN | 🇮🇳 HI | 🇮🇳 BH | 🇮🇳 TA | 🇸🇦 AR | 🇷🇺 RU

<b>Commands:</b>
- <code>/setlang</code> <code> — Set language""",

    "pin": """📌 <b>Pin</b>

Pin and manage messages!

<b>Commands:</b>
- <code>/pinned</code> — Get pinned message
- <code>/pin</code> — Pin replied message
- <code>/permapin</code> <text> — Pin custom message
- <code>/unpin</code> — Unpin message
- <code>/unpinall</code> — Unpin all
- <code>/antichannelpin</code> <yes/no> — Stop auto-pin
- <code>/cleanlinked</code> <yes/no> — Delete linked channel messages""",

    "purge": """🗑 <b>Purge</b>

Delete many messages at once!

<b>Commands:</b>
- <code>/purge</code> — Delete from reply to now
- <code>/purge <X></code> — Delete X messages
- <code>/spurge</code> — Silent purge
- <code>/del</code> — Delete replied message
- <code>/purgefrom</code> — Mark start point
- <code>/purgeto</code> — Delete from start to here""",

    "report": """🚨 <b>Report</b>

Let users report rule-breakers!

<b>User Commands:</b>
- <code>/report</code> — Report a message (reply)
- <code>@admin</code> — Same as /report

<b>Admin Commands:</b>
- <code>/reports</code> <yes/no> — Enable/disable reports""",

    "rules": """📜 <b>Rules</b>

Set and manage group rules!

<b>User Commands:</b>
- <code>/rules</code> — View rules

<b>Admin Commands:</b>
- <code>/setrules</code> <text> — Set rules
- <code>/resetrules</code> — Reset rules
- <code>/privaterules</code> <yes/no> — Send rules in PM""",

    "warning": """⚠️ <b>Warnings</b>

Keep members in check!

<b>Commands:</b>
- <code>/warn</code> <reason> — Warn a user
- <code>/dwarn</code> — Warn + delete message
- <code>/swarn</code> — Silent warn
- <code>/warns</code> — View user's warnings
- <code>/rmwarn</code> — Remove last warning
- <code>/resetwarn</code> — Reset user warnings
- <code>/resetallwarns</code> — Reset all warnings
- <code>/warnmode</code> <mode> — Set warn action
- <code>/warnlimit</code> <number> — Set warn limit
- <code>/warntime</code> <time> — Set warn expiry""",

    "sudo": """🔑 <b>Sudo</b>

Grant trusted users owner-level access!

<b>Owner Commands:</b>
- <code>/addsudo</code> — Add sudo user
- <code>/rmsudo</code> — Remove sudo user
- <code>/sudolist</code> — List all sudo users""",

    "chatbot": """🤖 <b>Chatbot</b> (DeepSeek AI)

Miss Cherry chats with your members!

<b>Commands:</b>
- <code>/chatbot on</code> — Enable
- <code>/chatbot off</code> — Disable (default)

<b>Smart Logic:</b>
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
