# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Database             ║
# ╚══════════════════════════════════════════╝

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import cfg
from core.logger import logger


class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(cfg.DATABASE_URL)
        self.db = self.client[cfg.DATABASE_NAME]
        logger.info("MongoDB connected!")

    async def close(self):
        if self.client:
            self.client.close()

    def __getattr__(self, name):
        return self.db[name]


db = Database()


# ══════════════════════════════════════════════
#  SUDO
# ══════════════════════════════════════════════
async def add_sudo(user_id: int):
    await db.sudos.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

async def remove_sudo(user_id: int):
    await db.sudos.delete_one({"_id": user_id})

async def get_sudos() -> list:
    return [d["_id"] async for d in db.sudos.find()]


# ══════════════════════════════════════════════
#  CHATS & USERS
# ══════════════════════════════════════════════
async def save_chat(chat_id: int, title: str):
    await db.chats.update_one({"_id": chat_id}, {"$set": {"title": title}}, upsert=True)

async def save_user(user_id: int, username: str = None):
    await db.users.update_one({"_id": user_id}, {"$set": {"username": username}}, upsert=True)

async def get_all_chats() -> list:
    return [d async for d in db.chats.find()]

async def get_all_users() -> list:
    return [d async for d in db.users.find()]


# ══════════════════════════════════════════════
#  LANGUAGE
# ══════════════════════════════════════════════
async def set_language(chat_id: int, lang: str):
    await db.language.update_one({"_id": chat_id}, {"$set": {"lang": lang}}, upsert=True)

async def get_language(chat_id: int) -> str:
    doc = await db.language.find_one({"_id": chat_id})
    return doc["lang"] if doc else "en"


# ══════════════════════════════════════════════
#  ANTIFLOOD
# ══════════════════════════════════════════════
async def set_flood(chat_id: int, limit: int):
    await db.antiflood.update_one({"_id": chat_id}, {"$set": {"limit": limit}}, upsert=True)

async def get_flood(chat_id: int) -> dict:
    return await db.antiflood.find_one({"_id": chat_id}) or {}

async def set_flood_mode(chat_id: int, mode: str):
    await db.antiflood.update_one({"_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)

async def set_flood_timer(chat_id: int, count: int, duration: int):
    await db.antiflood.update_one({"_id": chat_id}, {"$set": {"timer_count": count, "timer_duration": duration}}, upsert=True)

async def set_clear_flood(chat_id: int, value: bool):
    await db.antiflood.update_one({"_id": chat_id}, {"$set": {"clear": value}}, upsert=True)


# ══════════════════════════════════════════════
#  ANTIRAID
# ══════════════════════════════════════════════
async def set_antiraid(chat_id: int, status: bool, duration: int = 21600):
    await db.antiraid.update_one({"_id": chat_id}, {"$set": {"enabled": status, "duration": duration}}, upsert=True)

async def get_antiraid(chat_id: int) -> dict:
    return await db.antiraid.find_one({"_id": chat_id}) or {}

async def set_raidtime(chat_id: int, seconds: int):
    await db.antiraid.update_one({"_id": chat_id}, {"$set": {"raidtime": seconds}}, upsert=True)

async def set_raidactiontime(chat_id: int, seconds: int):
    await db.antiraid.update_one({"_id": chat_id}, {"$set": {"actiontime": seconds}}, upsert=True)

async def set_autoantiraid(chat_id: int, joins: int):
    await db.antiraid.update_one({"_id": chat_id}, {"$set": {"auto_joins": joins}}, upsert=True)


# ══════════════════════════════════════════════
#  APPROVED
# ══════════════════════════════════════════════
async def approve_user(chat_id: int, user_id: int):
    await db.approved.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"chat_id": chat_id, "user_id": user_id}}, upsert=True)

async def unapprove_user(chat_id: int, user_id: int):
    await db.approved.delete_one({"chat_id": chat_id, "user_id": user_id})

async def is_approved(chat_id: int, user_id: int) -> bool:
    return bool(await db.approved.find_one({"chat_id": chat_id, "user_id": user_id}))

async def get_approved_users(chat_id: int) -> list:
    return [d["user_id"] async for d in db.approved.find({"chat_id": chat_id})]

async def unapprove_all(chat_id: int):
    await db.approved.delete_many({"chat_id": chat_id})


# ══════════════════════════════════════════════
#  BLOCKLIST
# ══════════════════════════════════════════════
async def add_blocklist(chat_id: int, trigger: str, reason: str = ""):
    await db.blocklist.update_one({"chat_id": chat_id, "trigger": trigger}, {"$set": {"reason": reason}}, upsert=True)

async def remove_blocklist(chat_id: int, trigger: str):
    await db.blocklist.delete_one({"chat_id": chat_id, "trigger": trigger})

async def get_blocklist(chat_id: int) -> list:
    return [d async for d in db.blocklist.find({"chat_id": chat_id})]

async def clear_blocklist(chat_id: int):
    await db.blocklist.delete_many({"chat_id": chat_id})

async def get_chat_settings(chat_id: int) -> dict:
    return await db.chats.find_one({"_id": chat_id}) or {}

async def set_chat_setting(chat_id: int, key: str, value):
    await db.chats.update_one({"_id": chat_id}, {"$set": {key: value}}, upsert=True)


# ══════════════════════════════════════════════
#  FILTERS
# ══════════════════════════════════════════════
async def add_filter(chat_id: int, trigger: str, reply: str):
    await db.filters.update_one({"chat_id": chat_id, "trigger": trigger}, {"$set": {"reply": reply}}, upsert=True)

async def remove_filter(chat_id: int, trigger: str):
    await db.filters.delete_one({"chat_id": chat_id, "trigger": trigger})

async def get_filters(chat_id: int) -> list:
    return [d async for d in db.filters.find({"chat_id": chat_id})]

async def clear_filters(chat_id: int):
    await db.filters.delete_many({"chat_id": chat_id})


# ══════════════════════════════════════════════
#  GREETINGS
# ══════════════════════════════════════════════
async def set_greeting(chat_id: int, key: str, value):
    await db.greetings.update_one({"_id": chat_id}, {"$set": {key: value}}, upsert=True)

async def get_greeting(chat_id: int) -> dict:
    return await db.greetings.find_one({"_id": chat_id}) or {}


# ══════════════════════════════════════════════
#  RULES
# ══════════════════════════════════════════════
async def set_rules(chat_id: int, text: str):
    await db.rules.update_one({"_id": chat_id}, {"$set": {"text": text}}, upsert=True)

async def get_rules(chat_id: int) -> dict:
    return await db.rules.find_one({"_id": chat_id}) or {}

async def reset_rules(chat_id: int):
    await db.rules.delete_one({"_id": chat_id})


# ══════════════════════════════════════════════
#  WARNINGS
# ══════════════════════════════════════════════
async def add_warn(chat_id: int, user_id: int, reason: str) -> int:
    doc = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    warns = doc.get("warns", []) if doc else []
    warns.append(reason)
    await db.warns.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"warns": warns}}, upsert=True)
    return len(warns)

async def get_warns(chat_id: int, user_id: int) -> list:
    doc = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc.get("warns", []) if doc else []

async def remove_last_warn(chat_id: int, user_id: int):
    doc = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    if doc and doc.get("warns"):
        doc["warns"].pop()
        await db.warns.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"warns": doc["warns"]}})

async def reset_warns(chat_id: int, user_id: int):
    await db.warns.delete_one({"chat_id": chat_id, "user_id": user_id})

async def reset_all_warns(chat_id: int):
    await db.warns.delete_many({"chat_id": chat_id})

async def get_warn_settings(chat_id: int) -> dict:
    doc = await get_chat_settings(chat_id)
    return {
        "limit": doc.get("warn_limit", 3),
        "mode":  doc.get("warn_mode", "ban"),
        "time":  doc.get("warn_time", None)
    }


# ══════════════════════════════════════════════
#  CHATBOT
# ══════════════════════════════════════════════
async def set_chatbot(chat_id: int, status: bool):
    await db.chatbot.update_one({"_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_chatbot(chat_id: int) -> bool:
    doc = await db.chatbot.find_one({"_id": chat_id})
    return doc.get("enabled", False) if doc else False

async def get_chat_history(chat_id: int, user_id: int) -> list:
    doc = await db.chatbot_history.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc.get("history", []) if doc else []

async def save_chat_history(chat_id: int, user_id: int, history: list):
    history = history[-20:]
    await db.chatbot_history.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"history": history}},
        upsert=True
    )
