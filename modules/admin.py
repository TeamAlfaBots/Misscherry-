# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Admin Module          ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.filters import admin_filter, can_promote_filter
from core.translator import _
from core.database import get_chat_settings, set_chat_setting
from utils.helpers import get_target_user, mention


# Permission bit order — each bit position maps to a ChatPrivileges field.
PROMOTE_PERMS = [
    ("info",    "can_change_info",       "✏️ Change Info"),
    ("delete",  "can_delete_messages",   "🗑 Delete Messages"),
    ("video",   "can_manage_video_chats","🎥 Manage Video Chats"),
    ("restrict","can_restrict_members",  "🔨 Ban Users"),
    ("invite",  "can_invite_users",      "🔗 Invite via Link"),
    ("pin",     "can_pin_messages",      "📌 Pin Messages"),
    ("promote", "can_promote_members",   "👑 Add New Admins"),
]


def _encode_bits(enabled_keys: set) -> str:
    return "".join("1" if key in enabled_keys else "0" for key, _f, _l in PROMOTE_PERMS)


def _decode_bits(bits: str) -> set:
    return {key for (key, _f, _l), bit in zip(PROMOTE_PERMS, bits) if bit == "1"}


def _promote_kb(user_id: int, bits: str) -> InlineKeyboardMarkup:
    enabled = _decode_bits(bits)
    rows = []
    for key, _field, label in PROMOTE_PERMS:
        mark = "✅" if key in enabled else "❌"
        rows.append([
            InlineKeyboardButton(
                f"{mark} {label}",
                callback_data=f"promote_toggle:{user_id}:{key}:{bits}"
            )
        ])
    rows.append([
        InlineKeyboardButton("✅ Confirm & Promote", callback_data=f"promote_confirm:{user_id}:{bits}"),
        InlineKeyboardButton("✖️ Cancel", callback_data=f"promote_cancel:{user_id}"),
    ])
    return InlineKeyboardMarkup(rows)


@Client.on_message(filters.command("promote") & ~filters.private & can_promote_filter)
async def cmd_promote(client: Client, message: Message):
    user, reason = await get_target_user(client, message)
    if not user:
        return await message.reply(await _(message.chat.id, "general.no_user"))

    # Sensible defaults — everything except granting further admins.
    default_bits = _encode_bits({"info", "delete", "video", "restrict", "invite", "pin"})
    await message.reply(
        f"👑 Choose permissions for {mention(user)}:",
        reply_markup=_promote_kb(user.id, default_bits)
    )


@Client.on_callback_query(filters.regex(r"^promote_toggle:(-?\d+):(\w+):([01]+)$"))
async def cb_promote_toggle(client: Client, query: CallbackQuery):
    _prefix, user_id, key, bits = query.data.split(":")
    user_id = int(user_id)

    # Re-check the permission live, in case the admin's own rights changed.
    member = await client.get_chat_member(query.message.chat.id, query.from_user.id)
    is_creator = member.status == "creator"
    can_promote = is_creator or (member.privileges and member.privileges.can_promote_members)
    if not can_promote:
        return await query.answer(await _(query.message.chat.id, "general.not_admin"), show_alert=True)

    enabled = _decode_bits(bits)
    if key in enabled:
        enabled.discard(key)
    else:
        enabled.add(key)
    new_bits = _encode_bits(enabled)

    await query.message.edit_reply_markup(_promote_kb(user_id, new_bits))
    await query.answer()


@Client.on_callback_query(filters.regex(r"^promote_confirm:(-?\d+):([01]+)$"))
async def cb_promote_confirm(client: Client, query: CallbackQuery):
    _prefix, user_id, bits = query.data.split(":")
    user_id = int(user_id)

    member = await client.get_chat_member(query.message.chat.id, query.from_user.id)
    is_creator = member.status == "creator"
    can_promote = is_creator or (member.privileges and member.privileges.can_promote_members)
    if not can_promote:
        return await query.answer(await _(query.message.chat.id, "general.not_admin"), show_alert=True)

    enabled = _decode_bits(bits)
    perm_kwargs = {field: (key in enabled) for key, field, _label in PROMOTE_PERMS}
    perm_kwargs["can_manage_chat"] = True  # base right, required to be an admin at all

    try:
        target = await client.get_users(user_id)
        await client.promote_chat_member(
            query.message.chat.id, user_id,
            privileges=ChatPrivileges(**perm_kwargs)
        )
        await query.message.edit_text(
            await _(query.message.chat.id, "admin.promoted", name=mention(target))
        )
    except Exception as e:
        await query.message.edit_text(
            await _(query.message.chat.id, "bans.fail", error=str(e))
        )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^promote_cancel:(-?\d+)$"))
async def cb_promote_cancel(client: Client, query: CallbackQuery):
    await query.message.edit_text("❌ Promotion cancelled.")
    await query.answer()


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
