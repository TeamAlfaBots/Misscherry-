# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Bans Module           ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from utils.helpers import get_target_user, mention
from utils.chat_helpers import do_ban, do_unban, do_kick, do_mute, do_unmute, tban_until
from utils.log_reporter import log_action


async def _resolve_target(message: Message, client: Client):
    """Wraps get_target_user, turning the deleted-account case into a
    clear reply instead of letting a generic error surface."""
    try:
        return await get_target_user(client, message)
    except ValueError:
        await message.reply(
            "❌ That account has been deleted on Telegram, so it can't "
            "be targeted anymore."
        )
        return None, None


@Client.on_message(filters.command(["ban", "dban", "sban"]) & ~filters.private & admin_filter)
async def cmd_ban(client: Client, message: Message):
    user, reason = await _resolve_target(message, client)
    if reason is None:
        return  # deleted-account message already sent
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    cmd = message.command[0]
    try:
        await do_ban(client, message.chat.id, user.id)
        await log_action(client, message, "Banned", user, reason=reason)
        if cmd == "dban" and message.reply_to_message:
            await message.reply_to_message.delete()
        if cmd == "sban":
            await message.delete()
            return
        text = await _(message.chat.id, "bans.banned", name=mention(user))
        if reason:
            text += await _(message.chat.id, "bans.reason", reason=reason)
        await message.reply(text)
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("tban") & ~filters.private & admin_filter)
async def cmd_tban(client: Client, message: Message):
    user, time_str = await _resolve_target(message, client)
    if time_str is None:
        return
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    time_str = time_str.split()[0] if time_str else "1h"
    try:
        until = await tban_until(time_str)
        await do_ban(client, message.chat.id, user.id, until)
        await log_action(client, message, "Temp Banned", user, duration=time_str)
        await message.reply(await _(message.chat.id, "bans.tban", name=mention(user), time=time_str))
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("unban") & ~filters.private & admin_filter)
async def cmd_unban(client: Client, message: Message):
    user, reason = await _resolve_target(message, client)
    if reason is None:
        return
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    try:
        await do_unban(client, message.chat.id, user.id)
        await log_action(client, message, "Unbanned", user)
        await message.reply(await _(message.chat.id, "bans.unbanned", name=mention(user)))
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command(["mute", "dmute", "smute"]) & ~filters.private & admin_filter)
async def cmd_mute(client: Client, message: Message):
    user, reason = await _resolve_target(message, client)
    if reason is None:
        return
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    cmd = message.command[0]
    try:
        await do_mute(client, message.chat.id, user.id)
        await log_action(client, message, "Muted", user, reason=reason)
        if cmd == "dmute" and message.reply_to_message:
            await message.reply_to_message.delete()
        if cmd == "smute":
            await message.delete()
            return
        text = await _(message.chat.id, "bans.muted", name=mention(user))
        if reason:
            text += await _(message.chat.id, "bans.reason", reason=reason)
        await message.reply(text)
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("tmute") & ~filters.private & admin_filter)
async def cmd_tmute(client: Client, message: Message):
    user, time_str = await _resolve_target(message, client)
    if time_str is None:
        return
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    time_str = time_str.split()[0] if time_str else "1h"
    try:
        until = await tban_until(time_str)
        await do_mute(client, message.chat.id, user.id, until)
        await log_action(client, message, "Temp Muted", user, duration=time_str)
        await message.reply(await _(message.chat.id, "bans.tmute", name=mention(user), time=time_str))
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("unmute") & ~filters.private & admin_filter)
async def cmd_unmute(client: Client, message: Message):
    user, reason = await _resolve_target(message, client)
    if reason is None:
        return
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    try:
        await do_unmute(client, message.chat.id, user.id)
        await log_action(client, message, "Unmuted", user)
        await message.reply(await _(message.chat.id, "bans.unmuted", name=mention(user)))
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command(["kick", "dkick", "skick"]) & ~filters.private & admin_filter)
async def cmd_kick(client: Client, message: Message):
    user, reason = await _resolve_target(message, client)
    if reason is None:
        return
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    cmd = message.command[0]
    try:
        await do_kick(client, message.chat.id, user.id)
        await log_action(client, message, "Kicked", user, reason=reason)
        if cmd == "dkick" and message.reply_to_message:
            await message.reply_to_message.delete()
        if cmd == "skick":
            await message.delete()
            return
        text = await _(message.chat.id, "bans.kicked", name=mention(user))
        if reason:
            text += await _(message.chat.id, "bans.reason", reason=reason)
        await message.reply(text)
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))


@Client.on_message(filters.command("kickme") & ~filters.private)
async def cmd_kickme(client: Client, message: Message):
    try:
        await do_kick(client, message.chat.id, message.from_user.id)
    except Exception as e:
        await message.reply(await _(message.chat.id, "bans.fail", error=str(e)))
