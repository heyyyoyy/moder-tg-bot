import os
import aioredis
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.redis import RedisStorage2
import logging
import asyncio

load_dotenv()

loop = asyncio.get_event_loop()

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ['TOKEN']

PROXY = os.getenv('PROXY')
bot = Bot(TOKEN, parse_mode=ParseMode.HTML, proxy=PROXY)
storage = RedisStorage2(host=os.environ['REDIS'])
dp = Dispatcher(bot, storage=storage)


async def get_bot_id():
    bot_ = await bot.get_me()
    return bot_.id

BOT_ID = loop.run_until_complete(get_bot_id())
ADMIN = int(os.environ['ADMIN'])

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']


async def init_redis_pool():
    pool = await aioredis.create_redis_pool(
        f'redis://{os.environ["REDIS"]}',
        minsize=int(os.environ['REDIS_MIN_CON']),
        maxsize=int(os.environ['REDIS_MAX_CON'])

    )
    return pool


redis = loop.run_until_complete(init_redis_pool())


WEBHOOK_HOST = os.environ['WEBHOOK_HOST']
WEBHOOK_PATH = os.environ['WEBHOOK_PATH']

WEBAPP_HOST = os.environ['WEBAPP_HOST']
WEBAPP_PORT = os.environ['WEBAPP_PORT']
