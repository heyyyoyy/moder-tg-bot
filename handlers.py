from aiogram.types import ContentType
from aiogram.utils.exceptions import MessageCantBeDeleted
import logging

from settings import bot, dp, BOT_ID

from models import manager, UserToGroup, Group


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
            await Group.save_group(message.chat, readded=True)
            # Save group in the db
            # or check mark that the group is deleted (deleted=False)
            pass
        else:
            # User added in the group
            await UserToGroup.save_user_to_group(
                member,
                message.chat
            )
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
        await Group.delete_group(message.chat.id)
        # Mark in the db that the group is deleted
        pass
    else:
        # User left from the group
        await UserToGroup.delete_user_from_group(
            message.left_chat_member,
            message.chat.id
        )
        # Try delete service message
        # Mark in the db that user is deleted
        pass


@dp.message_handler(lambda msg: msg.chat.type in ['group', 'supergroup'])
async def all(message):
    # Check messages in the group (link, media, stickers)
    pass
