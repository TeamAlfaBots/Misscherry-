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
            InlineKeyboardButton("👑 Owner", url=f"https://t.me/{cfg.OWNER_USERNAME.lstrip('@')}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{cfg.DEVELOPER_USERNAME.lstrip('@')}", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("📂 Source", url=cfg.SOURCE_LINK, style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="start_menu"),
            InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
        ],
    ])


def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👮 Admin",     callback_data="help_admin"),
            InlineKeyboardButton("🌊 Antiflood", callback_data="help_antiflood"),
            InlineKeyboardButton("🛡 AntiRaid",  callback_data="help_antiraid"),
        ],
        [
            InlineKeyboardButton("✅ Approval",  callback_data="help_approval", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🔨 Bans",      callback_data="help_bans", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🚫 Blocklist", callback_data="help_blocklist", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("🔍 Filters",   callback_data="help_filters"),
            InlineKeyboardButton("👋 Greetings", callback_data="help_greetings", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("🌐 Language",  callback_data="help_language"),
        ],
        [
            InlineKeyboardButton("📌 Pin",       callback_data="help_pin"),
            InlineKeyboardButton("🗑 Purge",     callback_data="help_purge", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🚨 Report",    callback_data="help_report", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("📜 Rules",     callback_data="help_rules"),
            InlineKeyboardButton("⚠️ Warning",   callback_data="help_warning", style=ButtonStyle.DANGER),
            InlineKeyboardButton("🔑 Sudo",      callback_data="help_sudo", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("🤖 Chatbot",   callback_data="help_chatbot", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("📖 Miss Cherry Docs", url=cfg.DOCS_URL, style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="start_menu"),
            InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
        ],
    ])


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English",   callback_data="setlang_en"),
            InlineKeyboardButton("🇮🇳 हिन्दी",     callback_data="setlang_hi"),
        ],
        [
            InlineKeyboardButton("🇮🇳 Bhojpuri",  callback_data="setlang_bh"),
            InlineKeyboardButton("🇮🇳 தமிழ்",      callback_data="setlang_ta"),
        ],
        [
            InlineKeyboardButton("🇸🇦 العربية",    callback_data="setlang_ar"),
            InlineKeyboardButton("🇷🇺 Русский",    callback_data="setlang_ru"),
        ],
        [
            InlineKeyboardButton("◀️ Back", callback_data="start_menu"),
            InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
        ],
    ])


def back_close_kb(back_data: str = "help_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Back", callback_data=back_data),
        InlineKeyboardButton("✖️ Close", callback_data="close", style=ButtonStyle.DANGER),
    ]])


def back_kb(back_data: str = "help_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Back", callback_data=back_data),
    ]])
