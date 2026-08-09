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
    target_clean = target.lstrip("@")

    # Try resolving via the chat member list first when we have a chat
    # context — this can resolve users (and their access_hash) that a
    # bare get_users() call cannot, since the bot may never have
    # interacted with that user directly.
    try:
        member = await client.get_chat_member(message.chat.id, target_clean)
        return member.user, reason
    except Exception:
        pass

    try:
        user = await client.get_users(
            int(target) if target.lstrip("-").isdigit() else target
        )
        return user, reason
    except Exception:
        return None, reason
