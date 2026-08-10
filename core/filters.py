# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Custom Filters       ║
# ╚══════════════════════════════════════════╝

from pyrogram import filters
from pyrogram.types import Message
from core.config import cfg
from core.database import get_sudos, get_chat_settings


async def _owner_check(_, __, message: Message) -> bool:
    return message.from_user and message.from_user.id in cfg.OWNER_ID


async def _sudo_check(_, __, message: Message) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id in cfg.OWNER_ID:
        return True
    sudos = await get_sudos()
    return message.from_user.id in sudos


async def _is_admin(client, message: Message) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id in cfg.OWNER_ID:
        return True
    sudos = await get_sudos()
    if message.from_user.id in sudos:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


async def _admin_check(_, client, message: Message) -> bool:
    is_admin = await _is_admin(client, message)
    if is_admin:
        return True

    # Not an admin — if this chat has "adminerror" replies enabled,
    # let the user know why the command was rejected.
    if message.chat and message.chat.id:
        try:
            settings = await get_chat_settings(message.chat.id)
            if settings.get("adminerror", False):
                from core.translator import _ as translate
                text = await translate(message.chat.id, "general.not_admin")
                await message.reply(text)
        except Exception:
            pass

    return False


async def _can_promote_check(_, client, message: Message) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id in cfg.OWNER_ID:
        return True
    sudos = await get_sudos()
    if message.from_user.id in sudos:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status == "creator":
            return True
        if member.status == "administrator" and member.privileges:
            return bool(member.privileges.can_promote_members)
        return False
    except Exception:
        return False


owner_filter = filters.create(_owner_check, "OwnerFilter")
sudo_filter  = filters.create(_sudo_check,  "SudoFilter")
admin_filter = filters.create(_admin_check, "AdminFilter")
can_promote_filter = filters.create(_can_promote_check, "CanPromoteFilter")
