from traceback import format_exc
from aioredis import Redis
from decouple import config
from telethon import TelegramClient
import asyncio

try:
    BOT_TOKEN = config("BOT_TOKEN")
    REDISPASSWORD = config("REDISPASSWORD", default=None)
    REDISHOST = config("REDISHOST", default=None)
    REDISPORT = config("REDISPORT", default=None)
    REDISUSER = config("REDISUSER", default=None)
    ADMINS = [int(i) for i in config("ADMINS").split()]
except BaseException:
    print(format_exc())
    exit()

db = Redis(
    username=REDISUSER,
    host=REDISHOST,
    port=REDISPORT,
    password=REDISPASSWORD,
    decode_responses=True,
)

# connecting the client
client = TelegramClient(None, 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e")