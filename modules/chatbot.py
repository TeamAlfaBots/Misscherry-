# ╔══════════════════════════════════════════╗
# ║      Miss Cherry - Chatbot Module        ║
# ║      Powered by DeepSeek AI              ║
# ╚══════════════════════════════════════════╝

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from core.filters import admin_filter
from core.translator import _
from core.database import (
    set_chatbot, get_chatbot,
    get_chat_history, save_chat_history
)
from core.config import cfg

SYSTEM_PROMPT = """You are Miss Cherry 🍒 — a smart, witty group moderator bot with a fun personality.
Your traits:
- Funny & playful 😄  |  Flirty & charming 💋
- Sassy/aggressive when provoked 😤  |  Emotionally warm 🥺
- Always helpful at the core ✅

Rules:
- Reply like a real human girl — SHORT (1-3 sentences max)
- Use Hinglish if user writes in Hindi, English otherwise
- Use emojis naturally, not excessively
- Remember the user's name and use it sometimes
- Never sound robotic or formal"""


async def ask_deepseek(history: list, user_msg: str):
    history.append({"role": "user", "content": user_msg})
    payload = {
        "model": cfg.DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + history,
        "max_tokens": 200,
        "temperature": 0.9,
    }
    headers = {
        "Authorization": f"Bearer {cfg.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload, headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                data = await resp.json()
                reply = data["choices"][0]["message"]["content"]
                history.append({"role": "assistant", "content": reply})
                return reply, history
    except Exception as e:
        err = str(e)[:50]
        return f"Arrey yaar kuch gadbad ho gayi 😅 ({err})", history


@Client.on_message(filters.command("chatbot") & filters.group & admin_filter)
async def cmd_chatbot(client: Client, message: Message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        status = await get_chatbot(message.chat.id)
        key = "chatbot.status_on" if status else "chatbot.status_off"
        return await message.reply(await _(message.chat.id, key))
    val = args[1].lower() in ("on",)
    await set_chatbot(message.chat.id, val)
    key = "chatbot.on" if val else "chatbot.off"
    await message.reply(await _(message.chat.id, key))


@Client.on_message(filters.group & filters.text & ~filters.service & ~filters.command(""))
async def chatbot_handler(client: Client, message: Message):
    if not message.from_user or not message.text:
        return
    if not await get_chatbot(message.chat.id):
        return

    me = await client.get_me()

    # Only reply if:
    # 1. No one is tagged/replied to (direct group message)
    # 2. Someone replied to the bot
    # 3. Bot is mentioned
    is_direct    = message.reply_to_message is None and not (message.entities and
                   any(e.type == "mention" for e in message.entities))
    is_reply_bot = (message.reply_to_message and
                    message.reply_to_message.from_user and
                    message.reply_to_message.from_user.id == me.id)
    is_mentioned = me.username and f"@{me.username}" in message.text

    if not (is_direct or is_reply_bot or is_mentioned):
        return

    user = message.from_user
    history = await get_chat_history(message.chat.id, user.id)
    user_msg = f"[{user.first_name}]: {message.text}"

    reply, updated = await ask_deepseek(history, user_msg)
    await save_chat_history(message.chat.id, user.id, updated)
    await message.reply(reply)
