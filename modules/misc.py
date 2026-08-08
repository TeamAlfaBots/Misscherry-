# ╔══════════════════════════════════════════╗
# ║   Miss Cherry - Rules/Pin/Purge/         ║
# ║   Report/Language/Getlink Modules        ║
# ╚══════════════════════════════════════════╝

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter, sudo_filter
from core.translator import _
from core.database import (
    set_rules, get_rules, reset_rules,
    set_language, get_language,
    set_greeting, get_greeting,
    set_chat_setting, get_all_chats
)

purge_markers: dict = {}


# ══════════════════════════════════════════════
#  RULES
# ══════════════════════════════════════════════

@Client.on_message(filters.command("rules") & filters.group)
async def cmd_rules(client: Client, message: Message):
    doc = await get_rules(message.chat.id)
    text = doc.get("text", "")
    if not text:
        return await message.reply(await _(message.chat.id, "rules.none"))
    private = doc.get("private", False)
    full = await _(message.chat.id, "rules.title",
                   chatname=message.chat.title, rules=text)
    if private:
        try:
            await client.send_message(message.from_user.id, full)
            await message.reply(await _(message.chat.id, "rules.sent_private"))
        except Exception:
            await message.reply(full)
    else:
        await message.reply(full)


@Client.on_message(filters.command("setrules") & filters.group & admin_filter)
async def cmd_setrules(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage: `/setrules <text>`")
    await set_rules(message.chat.id, args[1])
    await message.reply(await _(message.chat.id, "rules.set"))


@Client.on_message(filters.command("resetrules") & filters.group & admin_filter)
async def cmd_resetrules(client: Client, message: Message):
    await reset_rules(message.chat.id)
    await message.reply(await _(message.chat.id, "rules.reset"))


@Client.on_message(filters.command("privaterules") & filters.group & admin_filter)
async def cmd_privaterules(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_chat_setting(message.chat.id, "rules_private", val)
    key = "rules.private_on" if val else "rules.private_off"
    await message.reply(await _(message.chat.id, key))


# ══════════════════════════════════════════════
#  PIN
# ══════════════════════════════════════════════

@Client.on_message(filters.command("pinned") & filters.group)
async def cmd_pinned(client: Client, message: Message):
    chat = await client.get_chat(message.chat.id)
    if not chat.pinned_message:
        return await message.reply(await _(message.chat.id, "pin.no_pinned"))
    cid = str(message.chat.id).replace("-100", "")
    await message.reply(
        f"📌 [Jump to pinned message](https://t.me/c/{cid}/{chat.pinned_message.id})"
    )


@Client.on_message(filters.command("pin") & filters.group & admin_filter)
async def cmd_pin(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply(await _(message.chat.id, "pin.no_reply"))
    args = message.text.split(None, 1)
    notify = len(args) > 1 and args[1].lower() in ("loud", "notify")
    await client.pin_chat_message(
        message.chat.id,
        message.reply_to_message.id,
        disable_notification=not notify
    )
    await message.reply(await _(message.chat.id, "pin.pinned"))


@Client.on_message(filters.command("unpin") & filters.group & admin_filter)
async def cmd_unpin(client: Client, message: Message):
    if message.reply_to_message:
        await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
    else:
        await client.unpin_chat_message(message.chat.id)
    await message.reply(await _(message.chat.id, "pin.unpinned"))


@Client.on_message(filters.command("unpinall") & filters.group & admin_filter)
async def cmd_unpinall(client: Client, message: Message):
    await client.unpin_all_chat_messages(message.chat.id)
    await message.reply(await _(message.chat.id, "pin.unpinned_all"))


@Client.on_message(filters.command("antichannelpin") & filters.group & admin_filter)
async def cmd_antichannelpin(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_greeting(message.chat.id, "antichannelpin", val)
    key = "pin.antichannelpin_on" if val else "pin.antichannelpin_off"
    await message.reply(await _(message.chat.id, key))


@Client.on_message(filters.command("cleanlinked") & filters.group & admin_filter)
async def cmd_cleanlinked(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_greeting(message.chat.id, "cleanlinked", val)
    key = "pin.cleanlinked_on" if val else "pin.cleanlinked_off"
    await message.reply(await _(message.chat.id, key))


# ══════════════════════════════════════════════
#  PURGE
# ══════════════════════════════════════════════

@Client.on_message(filters.command(["purge", "spurge"]) & filters.group & admin_filter)
async def cmd_purge(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply(await _(message.chat.id, "purge.no_reply"))
    start_id = message.reply_to_message.id
    end_id = message.id
    args = message.text.split(None, 1)
    try:
        if len(args) > 1 and args[1].isdigit():
            ids = list(range(start_id, start_id + int(args[1]) + 1))
        else:
            ids = list(range(start_id, end_id + 1))
        deleted = 0
        for i in range(0, len(ids), 100):
            chunk = ids[i:i+100]
            await client.delete_messages(message.chat.id, chunk)
            deleted += len(chunk)
    except Exception as e:
        return await message.reply(await _(message.chat.id, "purge.fail", error=str(e)))
    if message.command[0] != "spurge":
        confirm = await message.reply(await _(message.chat.id, "purge.done", count=deleted))
        await asyncio.sleep(3)
        try:
            await confirm.delete()
        except Exception:
            pass


@Client.on_message(filters.command("del") & filters.group & admin_filter)
async def cmd_del(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a message to delete it.")
    await message.reply_to_message.delete()
    await message.delete()


@Client.on_message(filters.command("purgefrom") & filters.group & admin_filter)
async def cmd_purgefrom(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to the message to start purge from.")
    purge_markers[message.chat.id] = message.reply_to_message.id
    await message.reply(await _(message.chat.id, "purge.purgefrom_set"))


@Client.on_message(filters.command("purgeto") & filters.group & admin_filter)
async def cmd_purgeto(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to the message to purge to.")
    start_id = purge_markers.get(message.chat.id)
    if not start_id:
        return await message.reply(await _(message.chat.id, "purge.purgeto_no_from"))
    end_id = message.reply_to_message.id
    ids = list(range(min(start_id, end_id), max(start_id, end_id) + 1))
    for i in range(0, len(ids), 100):
        await client.delete_messages(message.chat.id, ids[i:i+100])
    purge_markers.pop(message.chat.id, None)
    confirm = await message.reply(await _(message.chat.id, "purge.done", count=len(ids)))
    await asyncio.sleep(3)
    try:
        await confirm.delete()
    except Exception:
        pass


# ══════════════════════════════════════════════
#  REPORT
# ══════════════════════════════════════════════

@Client.on_message(filters.command("reports") & filters.group & admin_filter)
async def cmd_reports_setting(client: Client, message: Message):
    args = message.text.split(None, 1)
    val = args[1].lower() in ("yes", "on") if len(args) > 1 else True
    await set_greeting(message.chat.id, "reports_enabled", val)
    key = "report.reports_on" if val else "report.reports_off"
    await message.reply(await _(message.chat.id, key))


@Client.on_message((filters.command("report") | filters.regex(r"^@admin$")) & filters.group)
async def cmd_report(client: Client, message: Message):
    data = await get_greeting(message.chat.id)
    if not data.get("reports_enabled", True):
        return await message.reply(await _(message.chat.id, "report.disabled"))
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return await message.reply(await _(message.chat.id, "report.admin_cant_report"))
    except Exception:
        pass
    if not message.reply_to_message:
        return await message.reply(await _(message.chat.id, "report.not_reply"))
    reported = message.reply_to_message.from_user
    if reported:
        try:
            rm = await client.get_chat_member(message.chat.id, reported.id)
            if rm.status in ("administrator", "creator"):
                return await message.reply(await _(message.chat.id, "report.cant_report_admin"))
        except Exception:
            pass
    admins = []
    async for m in client.get_chat_members(message.chat.id, filter="administrators"):
        if not m.user.is_bot:
            admins.append(f"[{m.user.first_name}](tg://user?id={m.user.id})")
    await message.reply(
        await _(message.chat.id, "report.reported",
                user=message.from_user.mention,
                admins=" ".join(admins))
    )


# ══════════════════════════════════════════════
#  LANGUAGE
# ══════════════════════════════════════════════

@Client.on_message(filters.command("setlang") & filters.group & admin_filter)
async def cmd_setlang(client: Client, message: Message):
    valid = ("en", "hi", "bh", "ta", "ar", "ru")
    args = message.text.split(None, 1)
    if len(args) < 2:
        lang = await get_language(message.chat.id)
        return await message.reply(await _(message.chat.id, "language.current", lang=lang.upper()))
    lang = args[1].lower()
    if lang not in valid:
        return await message.reply(await _(message.chat.id, "language.invalid"))
    await set_language(message.chat.id, lang)
    await message.reply(await _(message.chat.id, "language.set", lang=lang.upper()))


# ══════════════════════════════════════════════
#  GETLINK
# ══════════════════════════════════════════════

@Client.on_message(filters.command("getlink") & sudo_filter)
async def cmd_getlink(client: Client, message: Message):
    chats = await get_all_chats()
    if not chats:
        return await message.reply(await _(message.chat.id, "getlink.no_chats"))
    lines = []
    count = 0
    for chat in chats:
        try:
            chat_obj = await client.get_chat(chat["_id"])
            try:
                link = await client.export_chat_invite_link(chat["_id"])
            except Exception:
                link = await _(0, "getlink.no_permission")
            count += 1
            lines.append(
                f"**{count}.**\n"
                f"Chat: `{chat_obj.title}`\n"
                f"ID: `{chat_obj.id}`\n"
                f"Link: {link}\n"
            )
        except Exception:
            continue
    if not lines:
        return await message.reply(await _(message.chat.id, "getlink.fail"))
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > 4000:
            await message.reply(chunk)
            chunk = line
        else:
            chunk += "\n" + line
    if chunk:
        await message.reply(chunk)
