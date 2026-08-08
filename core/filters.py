# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Custom Filters       ║
# ╚══════════════════════════════════════════╝

from pyrogram import filters
from pyrogram.types import Message
from core.config import cfg
from core.database import get_sudos


async def _owner_check(_, __, message: Message) -> bool:
    return message.from_user and message.from_user.id in cfg.OWNER_ID


async def _sudo_check(_, __, message: Message) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id in cfg.OWNER_ID:
        return True
    sudos = await get_sudos()
    return message.from_user.id in sudos


async def _admin_check(_, client, message: Message) -> bool:
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


owner_filter = filters.create(_owner_check, "OwnerFilter")
sudo_filter  = filters.create(_sudo_check,  "SudoFilter")
admin_filter = filters.create(_admin_check, "AdminFilter")
