# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Warnings Module       ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from core.database import (
    add_warn, get_warns, remove_last_warn,
    reset_warns, reset_all_warns,
    set_chat_setting, get_warn_settings
)
from utils.helpers import get_target_user, mention
from utils.chat_helpers import apply_action
from utils.time_parser import parse_time


async def apply_warn_action(client, message, user, count: int, settings: dict):
    limit = settings.get("limit", 3)
    mode  = settings.get("mode", "ban")
    wtime = settings.get("time")
    reason_text = ""

    text = await _(message.chat.id, "warning.warned",
                   name=mention(user), count=count,
                   limit=limit, reason="—")

    if count >= limit:
        text += "\n" + await _(message.chat.id, "warning.limit_reached", action=mode)
        try:
            await apply_action(client, message.chat.id, user.id, mode, wtime)
        except Exception as e:
            text += f"\n❌ {e}"
        await reset_warns(message.chat.id, user.id)

    await message.reply(text)


@Client.on_message(filters.command(["warn", "dwarn", "swarn"]) & ~filters.private & admin_filter)
async def cmd_warn(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    try:
        m = await client.get_chat_member(message.chat.id, user.id)
        if m.status in ("administrator", "creator"):
            return await message.reply(await _(message.chat.id, "warning.cant_warn_admin"))
    except Exception:
        pass
    cmd = message.command[0]
    if cmd == "dwarn" and message.reply_to_message:
        await message.reply_to_message.delete()
    if cmd == "swarn":
        await message.delete()
    settings = await get_warn_settings(message.chat.id)
    count = await add_warn(message.chat.id, user.id, reason or "No reason")
    await apply_warn_action(client, message, user, count, settings)


@Client.on_message(filters.command("warns") & ~filters.private)
async def cmd_warns(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        user = message.from_user
    warns = await get_warns(message.chat.id, user.id)
    settings = await get_warn_settings(message.chat.id)
    if not warns:
        return await message.reply(await _(message.chat.id, "warning.no_warns", name=mention(user)))
    lines = [f"{i+1}. {w}" for i, w in enumerate(warns)]
    await message.reply(await _(message.chat.id, "warning.warns_list",
                                name=mention(user), count=len(warns),
                                limit=settings["limit"], list="\n".join(lines)))


@Client.on_message(filters.command("rmwarn") & ~filters.private & admin_filter)
async def cmd_rmwarn(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    await remove_last_warn(message.chat.id, user.id)
    await message.reply(await _(message.chat.id, "warning.removed", name=mention(user)))


@Client.on_message(filters.command("resetwarn") & ~filters.private & admin_filter)
async def cmd_resetwarn(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))
    await reset_warns(message.chat.id, user.id)
    await message.reply(await _(message.chat.id, "warning.reset", name=mention(user)))


@Client.on_message(filters.command("resetallwarns") & ~filters.private & admin_filter)
async def cmd_resetallwarns(client: Client, message: Message):
    await reset_all_warns(message.chat.id)
    await message.reply(await _(message.chat.id, "warning.reset_all"))


@Client.on_message(filters.command("warnings") & ~filters.private)
async def cmd_warn_settings(client: Client, message: Message):
    s = await get_warn_settings(message.chat.id)
    await message.reply(await _(message.chat.id, "warning.settings",
                                limit=s["limit"], mode=s["mode"],
                                time=s["time"] or "Never"))


@Client.on_message(filters.command("warnmode") & ~filters.private & admin_filter)
async def cmd_warnmode(client: Client, message: Message):
    valid = ("ban", "mute", "kick", "tban", "tmute")
    args = message.text.split(None, 1)
    if len(args) < 2:
        s = await get_warn_settings(message.chat.id)
        return await message.reply(f"Current: **{s['mode']}**")
    if args[1].lower() not in valid:
        return await message.reply(f"Options: `{'` | `'.join(valid)}`")
    await set_chat_setting(message.chat.id, "warn_mode", args[1].lower())
    await message.reply(await _(message.chat.id, "warning.mode_set", mode=args[1].lower()))


@Client.on_message(filters.command("warnlimit") & ~filters.private & admin_filter)
async def cmd_warnlimit(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        s = await get_warn_settings(message.chat.id)
        return await message.reply(f"Current limit: **{s['limit']}**")
    if not args[1].isdigit():
        return await message.reply("❌ Provide a valid number.")
    await set_chat_setting(message.chat.id, "warn_limit", int(args[1]))
    await message.reply(await _(message.chat.id, "warning.limit_set", limit=args[1]))


@Client.on_message(filters.command("warntime") & ~filters.private & admin_filter)
async def cmd_warntime(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        s = await get_warn_settings(message.chat.id)
        return await message.reply(f"Current expiry: **{s['time'] or 'Never'}**")
    val = args[1].lower()
    if val in ("off", "no"):
        await set_chat_setting(message.chat.id, "warn_time", None)
        return await message.reply(await _(message.chat.id, "warning.time_off"))
    if not parse_time(val):
        return await message.reply("❌ Invalid time. Example: `4w` `3d` `1h`")
    await set_chat_setting(message.chat.id, "warn_time", val)
    await message.reply(await _(message.chat.id, "warning.time_set", time=val))
