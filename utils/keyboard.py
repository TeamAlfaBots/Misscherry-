# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Keyboards            ║
# ║       Bot API 9.4 Colored Buttons        ║
# ╚══════════════════════════════════════════╝

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from core.config import cfg


def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📨 Support", url=cfg.SUPPORT_LINK, style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📢 Updates", url=cfg.UPDATE_LINK, style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("❓ Help & Commands", callback_data="help_menu", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("🌐 Language", callback_data="lang_menu", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🪧 Info", callback_data="info_menu", style=ButtonStyle.DANGER),
        ],
    ])


def info_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "👑 Owner",
                url=f"https://t.me/{cfg.OWNER_USERNAME.lstrip('@')}",
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                "👨‍💻 Developer",
                url=f"https://t.me/{cfg.DEVELOPER_USERNAME.lstrip('@')}",
                style=ButtonStyle.PRIMARY
            ),
        ],
        [
            InlineKeyboardButton("📂 Source", url=cfg.SOURCE_LINK, style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="start_menu", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
        ],
    ])


def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👮 Admin", callback_data="help_admin", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🌊 Antiflood", callback_data="help_antiflood", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🛡 AntiRaid", callback_data="help_antiraid", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("✅ Approval", callback_data="help_approval", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🔨 Bans", callback_data="help_bans", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🚫 Blocklist", callback_data="help_blocklist", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("🔍 Filters", callback_data="help_filters", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("👋 Greetings", callback_data="help_greetings", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🌐 Language", callback_data="help_language", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("📌 Pin", callback_data="help_pin", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🗑 Purge", callback_data="help_purge", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🚨 Report", callback_data="help_report", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("📜 Rules", callback_data="help_rules", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⚠️ Warning", callback_data="help_warning", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🔑 Sudo", callback_data="help_sudo", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("🤖 Chatbot", callback_data="help_chatbot", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("📖 Miss Cherry Docs", url=cfg.DOCS_URL, style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="start_menu", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
        ],
    ])


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="setlang_hi", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("🇮🇳 Bhojpuri", callback_data="setlang_bh", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🇮🇳 தமிழ்", callback_data="setlang_ta", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang_ar", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="setlang_ru", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="start_menu", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
        ],
    ])


def back_close_kb(back_data: str = "help_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "◀️ Back",
                callback_data=back_data,
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                "✖️ Close",
                callback_data="close",
                style=ButtonStyle.DANGER
            ),
        ]
    ])


def back_kb(back_data: str = "help_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "◀️ Back",
                callback_data=back_data,
                style=ButtonStyle.PRIMARY
            ),
        ]
    ])
