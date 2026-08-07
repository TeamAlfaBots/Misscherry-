# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - AntiRaid Module       ║
# ╚══════════════════════════════════════════╝

import time
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from core.filters import admin_filter
from core.translator import _
from core.database import (
    set_antiraid, get_antiraid,
    set_raidtime, set_raidactiontime, set_autoantiraid
)
from utils.time_parser import parse_time, seconds_to_str

join_tracker: dict = {}


@Client.on_message(filters.command("antiraid") & filters.group & admin_filter)
async def cmd_antiraid(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2 or args[1].lower() in ("off", "no"):
        await set_antiraid(message.chat.id, False)
        return await message.reply(await _(message.chat.id, "antiraid.disabled"))
    secs = parse_time(args[1]) if args[1].lower() not in ("on",) else 21600
    await set_antiraid(message.chat.id, True, secs)
    await message.reply(await _(message.chat.id, "antiraid.enabled", duration=seconds_to_str(secs)))


@Client.on_message(filters.command("raidtime") & filters.group & admin_filter)
async def cmd_raidtime(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        data = await get_antiraid(message.chat.id)
        return await message.reply(await _(message.chat.id, "antiraid.current_raidtime",
                                           time=seconds_to_str(data.get("raidtime", 21600))))
    secs = parse_time(args[1])
    if not secs:
        return await message.reply("❌ Invalid time. Example: `6h`")
    await set_raidtime(message.chat.id, secs)
    await message.reply(await _(message.chat.id, "antiraid.raidtime_set", time=args[1]))


@Client.on_message(filters.command("raidactiontime") & filters.group & admin_filter)
async def cmd_raidactiontime(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        data = await get_antiraid(message.chat.id)
        return await message.reply(await _(message.chat.id, "antiraid.current_actiontime",
                                           time=seconds_to_str(data.get("actiontime", 3600))))
    secs = parse_time(args[1])
    if not secs:
        return await message.reply("❌ Invalid time. Example: `1h`")
    await set_raidactiontime(message.chat.id, secs)
    await message.reply(await _(message.chat.id, "antiraid.actiontime_set", time=args[1]))


@Client.on_message(filters.command("autoantiraid") & filters.group & admin_filter)
async def cmd_autoantiraid(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2 or args[1].lower() in ("off", "no", "0"):
        await set_autoantiraid(message.chat.id, 0)
        return await message.reply(await _(message.chat.id, "antiraid.auto_off"))
    if not args[1].isdigit():
        return await message.reply("❌ Provide a valid number.")
    await set_autoantiraid(message.chat.id, int(args[1]))
    await message.reply(await _(message.chat.id, "antiraid.auto_set", joins=args[1]))


@Client.on_chat_member_updated(filters.group)
async def antiraid_handler(client: Client, update: ChatMemberUpdated):
    if not update.new_chat_member or not update.old_chat_member:
        return
    if update.old_chat_member.status not in ("left", "banned"):
        return
    if update.new_chat_member.status not in ("member", "restricted"):
        return

    chat_id = update.chat.id
    user = update.new_chat_member.user
    now = time.time()
    data = await get_antiraid(chat_id)

    # Auto antiraid check
    auto_joins = data.get("auto_joins", 0)
    if auto_joins:
        join_tracker.setdefault(chat_id, [])
        join_tracker[chat_id] = [t for t in join_tracker[chat_id] if now - t < 60]
        join_tracker[chat_id].append(now)
        if len(join_tracker[chat_id]) >= auto_joins:
            await set_antiraid(chat_id, True, data.get("raidtime", 21600))
            join_tracker[chat_id] = []
            try:
                await client.send_message(chat_id, await _(chat_id, "antiraid.auto_triggered"))
            except Exception:
                pass
            data = await get_antiraid(chat_id)

    # Ban raider if antiraid active
    if data.get("enabled"):
        action_secs = data.get("actiontime", 3600)
        until = datetime.datetime.now() + datetime.timedelta(seconds=action_secs)
        try:
            await client.ban_chat_member(chat_id, user.id, until_date=until)
        except Exception:
            pass
