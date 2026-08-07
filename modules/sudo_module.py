# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Sudo Module           ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import owner_filter
from core.translator import _
from core.database import add_sudo, remove_sudo, get_sudos
from core.config import cfg
from utils.helpers import get_target_user, mention


@Client.on_message(filters.command("addsudo") & owner_filter)
async def cmd_addsudo(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    if user.id in cfg.OWNER_ID:
        return await message.reply(await _(message.chat.id, "sudo.already_owner"))
    await add_sudo(user.id)
    await message.reply(await _(message.chat.id, "sudo.added", name=mention(user)))


@Client.on_message(filters.command("rmsudo") & owner_filter)
async def cmd_rmsudo(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    await remove_sudo(user.id)
    await message.reply(await _(message.chat.id, "sudo.removed", name=mention(user)))


@Client.on_message(filters.command("sudolist") & owner_filter)
async def cmd_sudolist(client: Client, message: Message):
    sudos = await get_sudos()
    if not sudos:
        return await message.reply(await _(message.chat.id, "sudo.list_empty"))
    lines = []
    for uid in sudos:
        try:
            u = await client.get_users(uid)
            lines.append(f"• {mention(u)}")
        except Exception:
            lines.append(f"• `{uid}`")
    await message.reply(await _(message.chat.id, "sudo.list_title", list="\n".join(lines)))
