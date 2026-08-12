# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Log Reporter          ║
# ╚══════════════════════════════════════════╝

from datetime import datetime
from pyrogram import Client
from pyrogram.types import Message
from core.config import cfg
from core.logger import logger


def _tag(user) -> str:
    """Build a clickable mention for the log message."""
    if not user:
        return "Unknown"
    name = user.first_name or "User"
    return f"[{name}](tg://user?id={user.id}) (`{user.id}`)"


async def send_log(client: Client, text: str):
    """
    Send a formatted report to LOG_GROUP_ID.
    Safe no-op if LOG_GROUP_ID isn't configured, and never raises
    (a failed log send should never break the actual bot action).
    """
    if not cfg.LOG_GROUP_ID:
        return
    try:
        await client.send_message(
            cfg.LOG_GROUP_ID,
            text,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.warning(f"Failed to send log to LOG_GROUP_ID: {e}")


async def log_bot_started(client: Client, message: Message):
    """Report when the bot is added/started in a group via /start."""
    chat = message.chat
    user = message.from_user
    text = (
        "🍒 **Bot Started in Group**\n\n"
        f"👤 **By:** {_tag(user)}\n"
        f"💬 **Chat:** {chat.title}\n"
        f"🆔 **Chat ID:** `{chat.id}`\n"
        f"🕒 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await send_log(client, text)


async def log_action(
    client: Client,
    message: Message,
    action: str,
    target,
    reason: str = "",
    duration: str = ""
):
    """
    Report an admin action (ban/mute/kick/unban/unmute/etc).

    action: e.g. "Banned", "Muted", "Kicked", "Unbanned", "Unmuted"
    target: the user the action was taken on
    """
    chat = message.chat
    admin = message.from_user

    emoji_map = {
        "Banned": "🔨", "Temp Banned": "⏳🔨",
        "Unbanned": "♻️", "Muted": "🔇",
        "Temp Muted": "⏳🔇", "Unmuted": "🔊",
        "Kicked": "👢",
    }
    emoji = emoji_map.get(action, "📋")

    text = (
        f"{emoji} **{action}**\n\n"
        f"👮 **Admin:** {_tag(admin)}\n"
        f"🎯 **User:** {_tag(target)}\n"
        f"💬 **Chat:** {chat.title}\n"
        f"🆔 **Chat ID:** `{chat.id}`"
    )
    if duration:
        text += f"\n⏱ **Duration:** {duration}"
    if reason:
        text += f"\n📝 **Reason:** {reason}"
    text += f"\n🕒 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    await send_log(client, text)
