from aiogram.types import ContentType
from aiogram.utils.exceptions import MessageCantBeDeleted
import logging

from settings import bot, dp, BOT_ID


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


@dp.message_handler(content_types=ContentType.NEW_CHAT_MEMBERS)
async def new_chat_members_handler(message):
    for member in message.new_chat_members:
        if member.id == BOT_ID:
            # Bot added in the group
            # Save group in the db
            # or check mark that the group is deleted (deleted=False)
            pass
        else:
            # User added in the group
            # Use restrictChatMember
            # Send message with button
            # and try delete service message
            # Save user in the db (group - user)
            # or check mark that user is deleted (deleted=False)
            pass


@dp.message_handler(content_types=ContentType.LEFT_CHAT_MEMBER)
async def left_user_handler(message):
    if message.left_chat_member.id == BOT_ID:
        # Bot was removed from the group
        # Mark in the db that the group is deleted
        pass
    else:
        # User left from the group
        # Try delete service message
        # Mark in the db that user is deleted
        pass


@dp.message_handler(lambda msg: msg.chat.type in ['group', 'supergroup'])
async def all(message):
    # Check messages in the group (link, media, stickers)
    pass
