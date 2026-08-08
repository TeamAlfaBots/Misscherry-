# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Blocklist Module      ║
# ╚══════════════════════════════════════════╝

import re
from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from core.database import (
    add_blocklist, remove_blocklist, get_blocklist,
    clear_blocklist, set_chat_setting, get_chat_settings, is_approved
)
from utils.string_helpers import bl_pattern_to_regex
from utils.chat_helpers import apply_action


@Client.on_message(filters.command("addblocklist") & filters.group & admin_filter)
async def cmd_addblocklist(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 2:
        return await message.reply('Usage: `/addblocklist <trigger> [reason]`')
    trigger = args[1].strip('"').lower()
    reason = args[2] if len(args) > 2 else ""
    await add_blocklist(message.chat.id, trigger, reason)
    await message.reply(await _(message.chat.id, "blocklist.added", trigger=trigger))


@Client.on_message(filters.command("rmblocklist") & filters.group & admin_filter)
async def cmd_rmblocklist(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/rmblocklist <trigger>`")
    trigger = args[1].strip('"').lower()
    await remove_blocklist(message.chat.id, trigger)
    await message.reply(await _(message.chat.id, "blocklist.removed", trigger=trigger))


@Client.on_message(filters.command("unblocklistall") & filters.group)
async def cmd_unblocklistall(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status != "creator":
        return await message.reply(await _(message.chat.id, "general.only_creator"))
    await clear_blocklist(message.chat.id)
    await message.reply(await _(message.chat.id, "blocklist.cleared"))


@Client.on_message(filters.command("blocklist") & filters.group)
async def cmd_list_blocklist(client: Client, message: Message):
    items = await get_blocklist(message.chat.id)
    if not items:
        return await message.reply(await _(message.chat.id, "blocklist.list_empty"))
    lines = [f"• `{i['trigger']}`" + (f" — {i['reason']}" if i.get("reason") else "") for i in items]
    await message.reply(await _(message.chat.id, "blocklist.list_title", list="\n".join(lines)))


@Client.on_message(filters.command("blocklistmode") & filters.group & admin_filter)
async def cmd_blocklistmode(client: Client, message: Message):
    valid = ("nothing", "ban", "mute", "kick", "warn", "tban", "tmute")
    args = message.text.split(None, 1)
    if len(args) < 2 or args[1].lower() not in valid:
        return await message.reply(f"Options: `{'` | `'.join(valid)}`")
    await set_chat_setting(message.chat.id, "blmode", args[1].lower())
    await message.reply(await _(message.chat.id, "blocklist.mode_set", mode=args[1].lower()))


@Client.on_message(filters.command("blocklistdelete") & filters.group & admin_filter)
async def cmd_blocklistdelete(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_chat_setting(message.chat.id, "bldelete", val)
    await message.reply(await _(message.chat.id, "blocklist.delete_set", value="Yes" if val else "No"))


@Client.on_message(filters.command("setblocklistreason") & filters.group & admin_filter)
async def cmd_setblocklistreason(client: Client, message: Message):
    args = message.text.split(None, 1)
    reason = args[1] if len(args) > 1 else ""
    await set_chat_setting(message.chat.id, "blreason", reason)
    await message.reply(await _(message.chat.id, "blocklist.reason_set", reason=reason))


@Client.on_message(filters.command("resetblocklistreason") & filters.group & admin_filter)
async def cmd_resetblocklistreason(client: Client, message: Message):
    await set_chat_setting(message.chat.id, "blreason", "")
    await message.reply(await _(message.chat.id, "blocklist.reason_reset"))


@Client.on_message(filters.group & filters.text & ~filters.service & ~filters.command(""))
async def check_blocklist(client: Client, message: Message):
    if not message.from_user or not message.text:
        return
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        return
    if await is_approved(message.chat.id, message.from_user.id):
        return
    items = await get_blocklist(message.chat.id)
    if not items:
        return
    text = message.text.lower()
    for item in items:
        if re.search(bl_pattern_to_regex(item["trigger"]), text):
            settings = await get_chat_settings(message.chat.id)
            mode = settings.get("blmode", "nothing")
            if settings.get("bldelete", True):
                try:
                    await message.delete()
                except Exception:
                    pass
            if mode != "nothing":
                await apply_action(client, message.chat.id, message.from_user.id, mode)
            break
