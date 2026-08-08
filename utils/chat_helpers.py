# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Chat Helpers         ║
# ╚══════════════════════════════════════════╝

from pyrogram import Client
from pyrogram.types import Message, ChatPermissions
from core.database import save_chat, save_user
from utils.time_parser import parse_time
import datetime


async def track_chat_user(message: Message):
    """Save chat and user to DB on every message."""
    if message.chat and message.chat.title:
        await save_chat(message.chat.id, message.chat.title)
    if message.from_user:
        await save_user(message.from_user.id, message.from_user.username)


async def do_ban(client: Client, chat_id: int, user_id: int, until=None):
    await client.ban_chat_member(chat_id, user_id, until_date=until)


async def do_unban(client: Client, chat_id: int, user_id: int):
    await client.unban_chat_member(chat_id, user_id)


async def do_kick(client: Client, chat_id: int, user_id: int):
    await client.ban_chat_member(chat_id, user_id)
    await client.unban_chat_member(chat_id, user_id)


async def do_mute(client: Client, chat_id: int, user_id: int, until=None):
    await client.restrict_chat_member(
        chat_id, user_id,
        ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        ),
        until_date=until
    )


async def do_unmute(client: Client, chat_id: int, user_id: int):
    await client.restrict_chat_member(
        chat_id, user_id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
    )


async def tban_until(time_str: str) -> datetime.datetime:
    secs = parse_time(time_str)
    if not secs:
        secs = 3600
    return datetime.datetime.now() + datetime.timedelta(seconds=secs)


async def apply_action(client: Client, chat_id: int, user_id: int, mode: str, time_str: str = None):
    """Apply ban action based on mode string."""
    if mode == "ban":
        await do_ban(client, chat_id, user_id)
    elif mode == "kick":
        await do_kick(client, chat_id, user_id)
    elif mode == "mute":
        await do_mute(client, chat_id, user_id)
    elif mode == "tban":
        until = await tban_until(time_str or "1h")
        await do_ban(client, chat_id, user_id, until)
    elif mode == "tmute":
        until = await tban_until(time_str or "1h")
        await do_mute(client, chat_id, user_id, until)
