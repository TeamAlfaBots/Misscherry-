# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Config               ║
# ╚══════════════════════════════════════════╝

import os
from dotenv import load_dotenv

load_dotenv("config.env")


class Config:
    # ── Bot Credentials ──────────────────────
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    API_ID: int    = int(os.getenv("API_ID", 0))
    API_HASH: str  = os.getenv("API_HASH", "")

    # ── Owners ───────────────────────────────
    OWNER_ID: list = list(map(int, os.getenv("OWNER_ID", "").split()))

    # ── Log Group ─────────────────────────────
    LOG_GROUP_ID: int = int(os.getenv("LOG_GROUP_ID", 0) or 0)

    # ── Database ─────────────────────────────
    DATABASE_URL: str  = os.getenv("DATABASE_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "MissCherryDB")

    # ── DeepSeek AI ──────────────────────────
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL: str   = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # ── Bot Info ─────────────────────────────
    BOT_NAME: str  = os.getenv("BOT_NAME", "Miss Cherry 🍒")
    START_IMG: str = os.getenv("START_IMG", "")

    # ── Links ────────────────────────────────
    SUPPORT_LINK:       str = os.getenv("SUPPORT_LINK", "https://t.me/")
    UPDATE_LINK:        str = os.getenv("UPDATE_LINK", "https://t.me/")
    SOURCE_LINK:        str = os.getenv("SOURCE_LINK", "https://github.com/")
    DOCS_URL:           str = os.getenv("DOCS_URL", "https://")
    OWNER_USERNAME:     str = os.getenv("OWNER_USERNAME", "")
    DEVELOPER_USERNAME: str = os.getenv("DEVELOPER_USERNAME", "")


cfg = Config()
