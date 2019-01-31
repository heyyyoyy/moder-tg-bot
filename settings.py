import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
import asyncio

load_dotenv()

loop = asyncio.get_event_loop()

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ['TOKEN']

PROXY = os.getenv('PROXY')
bot = Bot(TOKEN, parse_mode=ParseMode.HTML, proxy=PROXY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def get_bot_id():
    bot_ = await bot.get_me()
    return bot_.id

BOT_ID = loop.run_until_complete(get_bot_id())
ADMIN = int(os.environ['ADMIN'])

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
