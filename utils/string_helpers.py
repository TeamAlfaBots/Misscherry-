# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - String Helpers       ║
# ╚══════════════════════════════════════════╝

import re
from html import escape


def fill_placeholders(text: str, user, chat) -> str:
    """Fill greeting/rule placeholders with actual user & chat info."""
    mention_name = escape(user.first_name or "User")
    return (
        text
        .replace("{first}",    user.first_name or "")
        .replace("{last}",     user.last_name or "")
        .replace("{fullname}", f"{user.first_name or ''} {user.last_name or ''}".strip())
        .replace("{username}", f"@{user.username}" if user.username else user.first_name or "User")
        .replace("{mention}",  f'<a href="tg://user?id={user.id}">{mention_name}</a>')
        .replace("{id}",       str(user.id))
        .replace("{chatname}", chat.title or "")
        .replace("{chatid}",   str(chat.id))
    )


def bl_pattern_to_regex(pattern: str) -> str:
    """Convert blocklist pattern to regex. Supports ?, *, **"""
    p = re.escape(pattern)
    p = p.replace(r"\*\*", r"[\s\S]*")
    p = p.replace(r"\*",   r"\S*")
    p = p.replace(r"\?",   r"\S")
    return p
