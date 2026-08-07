# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Helpers              ║
# ╚══════════════════════════════════════════╝

from pyrogram.types import Message


def mention(user) -> str:
    name = user.first_name or "User"
    return f"[{name}](tg://user?id={user.id})"


async def get_target_user(client, message: Message):
    """
    Returns (user, reason) from reply / mention / user_id.
    """
    reason = ""

    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        parts = message.text.split(None, 1)
        reason = parts[1] if len(parts) > 1 else ""
        return user, reason

    args = message.text.split(None, 2)
    if len(args) < 2:
        return None, ""

    target = args[1]
    reason = args[2] if len(args) > 2 else ""

    try:
        user = await client.get_users(
            int(target) if target.lstrip("-").isdigit() else target
        )
        return user, reason
    except Exception:
        return None, reason
