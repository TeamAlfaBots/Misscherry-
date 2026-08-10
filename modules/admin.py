# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Admin Module          ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from core.filters import admin_filter
from core.translator import _
from core.database import get_chat_settings, set_chat_setting
from utils.helpers import get_target_user, mention


@Client.on_message(filters.command("promote") & ~filters.private & admin_filter)
async def cmd_promote(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    try:
        await client.promote_chat_member(
            message.chat.id, user.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        await message.reply(await _(message.chat.id, "admin.promoted", name=mention(user)))
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("demote") & ~filters.private & admin_filter)
async def cmd_demote(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    try:
        await client.promote_chat_member(
            message.chat.id, user.id,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )
        await message.reply(await _(message.chat.id, "admin.demoted", name=mention(user)))
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("adminlist") & ~filters.private)
async def cmd_adminlist(client: Client, message: Message):
    lines = []
    async for member in client.get_chat_members(message.chat.id, filter="administrators"):
        title = f" [{member.custom_title}]" if member.custom_title else ""
        lines.append(f"• {mention(member.user)}{title}")
    text = await _(message.chat.id, "admin.adminlist_title", list="\n".join(lines))
    await message.reply(text)


@Client.on_message(filters.command("admincache") & ~filters.private & admin_filter)
async def cmd_admincache(client: Client, message: Message):
    count = 0
    async for member in client.get_chat_members(message.chat.id, filter="administrators"):
        count += 1
    await message.reply(await _(message.chat.id, "admin.cache_updated", count=count))


@Client.on_message(filters.command("anonadmin") & ~filters.private & admin_filter)
async def cmd_anonadmin(client: Client, message: Message):
    args = message.text.split(None, 1)
    settings = await get_chat_settings(message.chat.id)
    current = settings.get("anon_admin", False)

    if len(args) > 1 and args[1].lower() in ("on", "off"):
        new_value = args[1].lower() == "on"
    else:
        new_value = not current

    await set_chat_setting(message.chat.id, "anon_admin", new_value)
    state = await _(message.chat.id, "general.enabled" if new_value else "general.disabled")
    await message.reply(await _(message.chat.id, "admin.anon_updated", state=state))


@Client.on_message(filters.command("adminerror") & ~filters.private & admin_filter)
async def cmd_adminerror(client: Client, message: Message):
    args = message.text.split(None, 1)
    settings = await get_chat_settings(message.chat.id)
    current = settings.get("adminerror", False)

    if len(args) > 1 and args[1].lower() in ("on", "off"):
        new_value = args[1].lower() == "on"
    else:
        new_value = not current

    await set_chat_setting(message.chat.id, "adminerror", new_value)
    state = await _(message.chat.id, "general.enabled" if new_value else "general.disabled")
    await message.reply(await _(message.chat.id, "admin.error_updated", state=state))
