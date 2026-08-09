# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Greetings Module      ║
# ╚══════════════════════════════════════════╝

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from core.filters import admin_filter
from core.translator import _
from core.database import set_greeting, get_greeting
from utils.string_helpers import fill_placeholders


@Client.on_message(filters.command("welcome") & ~filters.private & admin_filter)
async def cmd_welcome(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_greeting(message.chat.id, "welcome_enabled", val)
    key = "greetings.welcome_on" if val else "greetings.welcome_off"
    await message.reply(await _(message.chat.id, key))


@Client.on_message(filters.command("goodbye") & ~filters.private & admin_filter)
async def cmd_goodbye(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_greeting(message.chat.id, "goodbye_enabled", val)
    key = "greetings.goodbye_on" if val else "greetings.goodbye_off"
    await message.reply(await _(message.chat.id, key))


@Client.on_message(filters.command("setwelcome") & ~filters.private & admin_filter)
async def cmd_setwelcome(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/setwelcome <text>`\nFillings: `{mention}` `{first}` `{username}` `{chatname}` `{id}`")
    await set_greeting(message.chat.id, "welcome_text", args[1])
    await message.reply(await _(message.chat.id, "greetings.welcome_set"))


@Client.on_message(filters.command("resetwelcome") & ~filters.private & admin_filter)
async def cmd_resetwelcome(client: Client, message: Message):
    await set_greeting(message.chat.id, "welcome_text", "")
    await message.reply(await _(message.chat.id, "greetings.welcome_reset"))


@Client.on_message(filters.command("setgoodbye") & ~filters.private & admin_filter)
async def cmd_setgoodbye(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/setgoodbye <text>`")
    await set_greeting(message.chat.id, "goodbye_text", args[1])
    await message.reply(await _(message.chat.id, "greetings.goodbye_set"))


@Client.on_message(filters.command("resetgoodbye") & ~filters.private & admin_filter)
async def cmd_resetgoodbye(client: Client, message: Message):
    await set_greeting(message.chat.id, "goodbye_text", "")
    await message.reply(await _(message.chat.id, "greetings.goodbye_reset"))


@Client.on_message(filters.command("cleanwelcome") & ~filters.private & admin_filter)
async def cmd_cleanwelcome(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_greeting(message.chat.id, "clean_welcome", val)
    key = "greetings.clean_on" if val else "greetings.clean_off"
    await message.reply(await _(message.chat.id, key))


@Client.on_chat_member_updated(~filters.private)
async def greet_handler(client: Client, update: ChatMemberUpdated):
    if not update.new_chat_member or not update.old_chat_member:
        return
    old = update.old_chat_member.status
    new = update.new_chat_member.status
    chat = update.chat
    user = update.new_chat_member.user
    data = await get_greeting(chat.id)

    # Welcome
    if old in ("left", "banned") and new in ("member", "restricted"):
        if not data.get("welcome_enabled", True):
            return
        default = await _(chat.id, "greetings.default_welcome")
        text = fill_placeholders(data.get("welcome_text") or default, user, chat)
        try:
            sent = await client.send_message(chat.id, text, parse_mode="markdown")
            if data.get("clean_welcome"):
                await asyncio.sleep(300)
                await sent.delete()
        except Exception:
            pass

    # Goodbye
    elif old in ("member", "restricted") and new in ("left", "banned"):
        if not data.get("goodbye_enabled", False):
            return
        default = await _(chat.id, "greetings.default_goodbye")
        text = fill_placeholders(data.get("goodbye_text") or default, user, chat)
        try:
            await client.send_message(chat.id, text, parse_mode="markdown")
        except Exception:
            pass
