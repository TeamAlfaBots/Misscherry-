# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Filters Module        ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from core.database import add_filter, remove_filter, get_filters, clear_filters


@Client.on_message(filters.command("filter") & filters.group & admin_filter)
async def cmd_add_filter(client: Client, message: Message):
    args = message.text.split(None, 2)
    if len(args) < 3:
        return await message.reply('Usage: `/filter <trigger> <reply>`')
    trigger = args[1].strip('"').lower()
    reply = args[2]
    await add_filter(message.chat.id, trigger, reply)
    await message.reply(await _(message.chat.id, "filters.added", trigger=trigger))


@Client.on_message(filters.command("filters") & filters.group)
async def cmd_list_filters(client: Client, message: Message):
    items = await get_filters(message.chat.id)
    if not items:
        return await message.reply(await _(message.chat.id, "filters.list_empty"))
    lines = [f"• `{i['trigger']}`" for i in items]
    await message.reply(await _(message.chat.id, "filters.list_title", list="\n".join(lines)))


@Client.on_message(filters.command("stop") & filters.group & admin_filter)
async def cmd_stop_filter(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/stop <trigger>`")
    trigger = args[1].strip('"').lower()
    await remove_filter(message.chat.id, trigger)
    await message.reply(await _(message.chat.id, "filters.removed", trigger=trigger))


@Client.on_message(filters.command("stopall") & filters.group & admin_filter)
async def cmd_stopall_filters(client: Client, message: Message):
    await clear_filters(message.chat.id)
    await message.reply(await _(message.chat.id, "filters.cleared"))


@Client.on_message(filters.group & filters.text & ~filters.service & ~filters.command(""))
async def check_filters(client: Client, message: Message):
    if not message.text:
        return
    items = await get_filters(message.chat.id)
    if not items:
        return
    text = message.text.lower()
    for item in items:
        if item["trigger"] in text:
            await message.reply(item["reply"])
            break
