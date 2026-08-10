# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Admin Module          ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
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
        is_on = key in enabled
        mark = "✅" if is_on else "❌"
        rows.append([
            InlineKeyboardButton(
                f"{mark} {label}",
                callback_data=f"promote_toggle:{user_id}:{key}:{bits}",
                style=ButtonStyle.SUCCESS if is_on else ButtonStyle.DANGER
            )
        ])
    rows.append([
        InlineKeyboardButton(
            "✅ Confirm & Promote",
            callback_data=f"promote_confirm:{user_id}:{bits}",
            style=ButtonStyle.SUCCESS
        ),
        InlineKeyboardButton(
            "✖️ Cancel",
            callback_data=f"promote_cancel:{user_id}",
            style=ButtonStyle.DANGER
        ),
    ])
    return InlineKeyboardMarkup(rows)
