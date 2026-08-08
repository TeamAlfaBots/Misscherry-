# ╔══════════════════════════════════════════╗
# ║   Miss Cherry - Antiflood Module         ║
# ╚══════════════════════════════════════════╝

import time
from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from core.database import (
    set_flood, get_flood, set_flood_mode,
    set_flood_timer, set_clear_flood, is_approved
)
from utils.time_parser import parse_time
from utils.chat_helpers import apply_action

flood_data: dict = {}


@Client.on_message(filters.command("flood") & ~filters.private)
async def cmd_flood_status(client: Client, message: Message):
    data = await get_flood(message.chat.id)
    limit = data.get("limit", 0)
    if not limit:
        return await message.reply(await _(message.chat.id, "antiflood.status_off"))
    mode = data.get("mode", "ban")
    clear = "Yes" if data.get("clear", True) else "No"
    await message.reply(await _(message.chat.id, "antiflood.status_on", limit=limit, mode=mode, clear=clear))


@Client.on_message(filters.command("setflood") & ~filters.private & admin_filter)
async def cmd_setflood(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/setflood <number/off>`")
    val = args[1].lower()
    if val in ("off", "no", "0"):
        await set_flood(message.chat.id, 0)
        return await message.reply(await _(message.chat.id, "antiflood.disabled"))
    if not val.isdigit():
        return await message.reply("❌ Provide a valid number.")
    await set_flood(message.chat.id, int(val))
    await message.reply(await _(message.chat.id, "antiflood.enabled", limit=val))


@Client.on_message(filters.command("setfloodtimer") & ~filters.private & admin_filter)
async def cmd_setfloodtimer(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 2:
        return await message.reply("Usage: `/setfloodtimer <count> <duration>` or `/setfloodtimer off`")
    if args[1].lower() in ("off", "no"):
        await set_flood_timer(message.chat.id, 0, 0)
        return await message.reply(await _(message.chat.id, "antiflood.timer_off"))
    if len(args) < 3:
        return await message.reply("Usage: `/setfloodtimer <count> <duration>`")
    count = int(args[1]) if args[1].isdigit() else 0
    duration = parse_time(args[2])
    if not count or not duration:
        return await message.reply("❌ Invalid format. Example: `/setfloodtimer 10 30s`")
    await set_flood_timer(message.chat.id, count, duration)
    await message.reply(await _(message.chat.id, "antiflood.timer_set", count=count, duration=args[2]))


@Client.on_message(filters.command("floodmode") & ~filters.private & admin_filter)
async def cmd_floodmode(client: Client, message: Message):
    valid = ("ban", "mute", "kick", "tban", "tmute")
    args = message.text.split(None, 1)
    if len(args) < 2 or args[1].lower() not in valid:
        return await message.reply(f"Options: `{'` | `'.join(valid)}`")
    await set_flood_mode(message.chat.id, args[1].lower())
    await message.reply(await _(message.chat.id, "antiflood.mode_set", mode=args[1].lower()))


@Client.on_message(filters.command("clearflood") & ~filters.private & admin_filter)
async def cmd_clearflood(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_clear_flood(message.chat.id, val)
    await message.reply(await _(message.chat.id, "antiflood.clear_set", value="Yes" if val else "No"))


@Client.on_message(~filters.private & ~filters.service & ~filters.command(""))
async def track_flood(client: Client, message: Message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if await is_approved(chat_id, user_id):
        return
    data = await get_flood(chat_id)
    limit = data.get("limit", 0)
    if not limit:
        return
    now = time.time()
    if chat_id not in flood_data:
        flood_data[chat_id] = {}
    ud = flood_data[chat_id].get(user_id, {"count": 0, "last": now})
    if now - ud["last"] > 5:
        ud = {"count": 1, "last": now}
    else:
        ud["count"] += 1
        ud["last"] = now
    flood_data[chat_id][user_id] = ud
    if ud["count"] >= limit:
        flood_data[chat_id][user_id] = {"count": 0, "last": now}
        mode = data.get("mode", "ban")
        if data.get("clear", True):
            try:
                await message.delete()
            except Exception:
                pass
        try:
            await apply_action(client, chat_id, user_id, mode)
            key = f"antiflood.triggered_{mode}"
            await message.reply(await _(chat_id, key, name=message.from_user.mention))
        except Exception:
            pass
