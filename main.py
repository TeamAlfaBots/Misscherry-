# ╔══════════════════════════════════════════╗
# ║         Miss Cherry 🍒 Bot               ║
# ║         Made by AlfaBots                 ║
# ╚══════════════════════════════════════════╝

import asyncio

from pyrogram import Client, idle

from core.config import cfg
from core.logger import logger
from core.database import db
from core.translator import load_locales

plugins = dict(root="modules")

app: Client = None


async def main():
    global app

    app = Client(
        "MissCherry",
        api_id=cfg.API_ID,
        api_hash=cfg.API_HASH,
        bot_token=cfg.BOT_TOKEN,
        plugins=plugins,
        in_memory=True
    )

    await db.connect()
    logger.info("✅ Database connected")

    load_locales()
    logger.info("✅ Locales loaded")

    await app.start()
    me = await app.get_me()
    logger.info(f"✅ Bot started as @{me.username}")

    await idle()

    await app.stop()
    await db.close()
    logger.info("Bot stopped.")


if __name__ == "__main__":
    print("╔══════════════════════════════════╗")
    print("║   Miss Cherry 🍒 Bot Starting... ║")
    print("║         By AlfaBots              ║")
    print("╚══════════════════════════════════╝")

    asyncio.run(main())
    
