# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Translator           ║
# ╚══════════════════════════════════════════╝

import json
import os
from core.database import get_language
from core.logger import logger

LOCALES: dict = {}
LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")


def load_locales():
    global LOCALES
    for file in os.listdir(LOCALES_DIR):
        if file.endswith(".json"):
            lang = file.replace(".json", "").lower()
            try:
                with open(os.path.join(LOCALES_DIR, file), encoding="utf-8") as f:
                    LOCALES[lang] = json.load(f)
                logger.info(f"Loaded locale: {lang}")
            except Exception as e:
                logger.error(f"Failed to load locale {file}: {e}")


async def _(chat_id: int, key: str, **kwargs) -> str:
    """
    Get translated string for a chat.

    Usage:
        await _( chat_id, "bans.banned", name="John")
        await _( chat_id, "admin.not_admin")
    """
    lang = (await get_language(chat_id)).lower().replace("-", "_")

    # Try requested language, fallback to English
    strings = LOCALES.get(lang) or LOCALES.get("en", {})

    # Navigate nested key: "bans.banned" → strings["bans"]["banned"]
    text = strings
    for k in key.split("."):
        if isinstance(text, dict):
            text = text.get(k)
        else:
            text = None
            break

    # Fallback to English if key missing
    if not text:
        text = LOCALES.get("en", {})
        for k in key.split("."):
            if isinstance(text, dict):
                text = text.get(k)
            else:
                text = None
                break

    if not text:
        return f"[{key}]"

    # Fill placeholders
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text
