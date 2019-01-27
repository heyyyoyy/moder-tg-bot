from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

from settings import TOKEN


logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.errors_handler()
async def error(update, error):
    logging.exception(f'Update - {update} with error')
    return True


@dp.message_handler(commands='start')
async def welcome(message):
    await bot.send_message(
        message.from_user.id,
        'hello'
    )
