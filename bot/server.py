import logging

from aiogram.utils.executor import start_webhook
from .settings import WEBHOOK_HOST, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from .handlers import bot, dp


WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)


async def on_startup(dp):
    await bot.set_webhook(
        WEBHOOK_URL,
        certificate=open('./bot/webhook_cert.pem', 'r')
        )


async def on_shutdown(dp):
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH,
                  on_startup=on_startup, on_shutdown=on_shutdown,
                  host=WEBAPP_HOST, port=WEBAPP_PORT)
