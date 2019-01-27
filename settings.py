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


bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def get_bot_id():
    bot_ = await bot.get_me()
    return bot_.id

BOT_ID = loop.run_until_complete(get_bot_id())
