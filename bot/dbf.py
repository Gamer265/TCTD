from . import *


async def add_user(id):
    board = eval((await db.get("BOARDCAST_USERS")) or "[]")
    if id not in board:
        board.append(id)
        await db.set("BOARDCAST_USERS", str(board).replace(" ", ""))


async def rem_user(id):
    board = eval((await db.get("BOARDCAST_USERS")) or "[]")
    if id in board:
        board.remove(id)
        await db.set("BOARDCAST_USERS", str(board).replace(" ", ""))


async def get_users():
    return eval((await db.get("BOARDCAST_USERS")) or "[]")

async def get_start_msg(client: TelegramClient):
    id_ = await db.get("START_MSG")
    if id_:
        try:
            msg = await client.get_messages(DATABASE_CHANNEL, ids=eval(id_))
            if msg:
                return msg
        except:
            return "Hi"
    return "Hi"


async def get_wlcm_msg(client):
    id_ = await db.get("WELCOME_MSG")
    if id_:
        try:
            msg = await client.get_messages(DATABASE_CHANNEL, ids=eval(id_))
            if msg:
                return msg
        except:
            return "Welcome"
    return "Welcome"


async def get_chat_list():
    return ((await db.get("CHAT_LIST")) or "").split() or []


async def set_start_msg(id):
    await db.set("START_MSG", str(id))


async def set_wlcm_msg(id):
    await db.set("WELCOME_MSG", str(id))


async def set_chat_list(chat):
    chats = await get_chat_list()
    if chat not in chats:
        chats.append(chat)
        await db.set("CHAT_LIST", " ".join(chats))
        return True
    return False


async def rem_chat_list(chat):
    chats = await get_chat_list()
    if chat in chats:
        chats.remove(chat)
        await db.set("CHAT_LIST", " ".join(chats))
        return True
    return False