# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Approval Module       ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from core.database import (
    approve_user, unapprove_user,
    is_approved, get_approved_users, unapprove_all
)
from utils.helpers import get_target_user, mention


@Client.on_message(filters.command("approval") & filters.group)
async def cmd_approval(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        user = message.from_user
    status = await is_approved(message.chat.id, user.id)
    key = "approval.approved_yes" if status else "approval.approved_no"
    await message.reply(await _(message.chat.id, key, name=mention(user)))


@Client.on_message(filters.command("approve") & filters.group & admin_filter)
async def cmd_approve(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    await approve_user(message.chat.id, user.id)
    await message.reply(await _(message.chat.id, "approval.approve_done", name=mention(user)))


@Client.on_message(filters.command("unapprove") & filters.group & admin_filter)
async def cmd_unapprove(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    await unapprove_user(message.chat.id, user.id)
    await message.reply(await _(message.chat.id, "approval.unapprove_done", name=mention(user)))


@Client.on_message(filters.command("approved") & filters.group)
async def cmd_approved_list(client: Client, message: Message):
    users = await get_approved_users(message.chat.id)
    if not users:
        return await message.reply(await _(message.chat.id, "approval.approved_none"))
    lines = []
    for uid in users:
        try:
            u = await client.get_users(uid)
            lines.append(f"• {mention(u)}")
        except Exception:
            lines.append(f"• `{uid}`")
    await message.reply(await _(message.chat.id, "approval.approved_list", list="\n".join(lines)))


@Client.on_message(filters.command("unapproveall") & filters.group)
async def cmd_unapproveall(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status != "creator":
        return await message.reply(await _(message.chat.id, "general.only_creator"))
    await unapprove_all(message.chat.id)
    await message.reply(await _(message.chat.id, "approval.unapprove_all_done"))
