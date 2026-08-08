# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Broadcast Module      ║
# ╚══════════════════════════════════════════╝

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import sudo_filter
from core.translator import _
from core.database import get_all_chats, get_all_users


@Client.on_message(filters.command("broadcast") & sudo_filter)
async def cmd_broadcast(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply(await _(message.chat.id, "broadcast.no_reply"))

    args = message.text.split(None, 1)
    target = args[1].strip().lower() if len(args) > 1 else "all"
    # target: "all" | "groups" | "users"

    status_msg = await message.reply(await _(message.chat.id, "broadcast.started"))

    success = failed = total = 0
    original = message.reply_to_message

    async def send_to(chat_id):
        nonlocal success, failed
        try:
            await original.copy(chat_id)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    if target in ("all", "groups"):
        chats = await get_all_chats()
        total += len(chats)
        for chat in chats:
            await send_to(chat["_id"])

    if target in ("all", "users"):
        users = await get_all_users()
        total += len(users)
        for user in users:
            await send_to(user["_id"])

    await status_msg.edit(
        await _(message.chat.id, "broadcast.done",
                total=total, success=success, failed=failed)
    )
