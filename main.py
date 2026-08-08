# ╔══════════════════════════════════════════╗
# ║         Miss Cherry 🍒 Bot               ║
# ║         Made by AlfaBots                 ║
# ╚══════════════════════════════════════════╝

import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from pyrogram import Client, idle, filters
from pyrogram.types import Message

from core.config import cfg
from core.logger import logger
from core.database import db
from core.translator import load_locales

plugins = dict(root="modules")

app: Client = None


# HTTP Server for Render health checks
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Miss Cherry is running')

    def log_message(self, format, *args):
        pass  # Suppress logs


def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"✅ HTTP health check server started on port {port}")
    server.serve_forever()


async def main():
    global app

    # Start HTTP server in background thread (keeps Render alive)
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    logger.info("HTTP server thread started for Render health checks")

    app = Client(
        "MissCherry",
        api_id=cfg.API_ID,
        api_hash=cfg.API_HASH,
        bot_token=cfg.BOT_TOKEN,
        plugins=plugins,
        in_memory=True
    )

    # DEBUG: raw catch-all handler, no filters, separate dispatch group (-1)
    # so it always runs first and independently of every other handler.
    @app.on_message(filters.all, group=-1)
    async def debug_catch_all(client: Client, message: Message):
        logger.info(
            f"🐞DEBUG_RAW_UPDATE🐞 chat_id={message.chat.id} "
            f"chat_type={message.chat.type} text={message.text!r}"
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

