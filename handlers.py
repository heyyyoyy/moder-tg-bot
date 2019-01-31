from aiogram.types import ContentType
import logging

from settings import bot, dp, BOT_ID, ADMIN

from models import UserToGroup, Group
from views import check_user, spam, search_link


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
    # try delete service message
    await bot.delete_message(
        message.chat.id,
        message.message_id
    )
    for member in message.new_chat_members:
        if member.id == BOT_ID:
            if message.chat.type == 'group':
                await bot.leave_chat(message.chat.id)
                await bot.send_message(
                            message.from_user.id,
                            'Чтобы я мог давать ограничения, '
                            'преобразуй группу в супергруппу и '
                            'добавь меня снова'
                        )
            # Bot added in the group
            # if it is not added by admin, use leave_chat
            elif ADMIN != message.from_user.id:
                await bot.leave_chat(message.chat.id)
            else:
                # Save group in the db
                # or check mark that the group is deleted (deleted=False)
                await Group.save_group(message.chat, readded=True)
        else:
            # User added in the group
            # Save user in the db (group - user)
            # or check mark that user is deleted (deleted=False)
            await UserToGroup.save_user_to_group(
                member,
                message.chat
            )
            # Use restrictChatMember
            await bot.restrict_chat_member(
                message.chat.id,
                member.id,
                until_date=0,
                can_send_messages=False,
                )
            text, kb = await check_user(member)
            # Send message with button
            await bot.send_message(
                message.chat.id,
                text,
                reply_markup=kb
            )


@dp.callback_query_handler(spam.filter(action='filter'))
async def handle_click(call, callback_data):
    user_id = int(callback_data['id'])
    if call.from_user.id == user_id:
        await bot.restrict_chat_member(
            call.message.chat.id,
            user_id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    else:
        await bot.answer_callback_query(call.id)


@dp.message_handler(content_types=ContentType.LEFT_CHAT_MEMBER)
async def left_user_handler(message):
    # try delete service message
    await bot.delete_message(
        message.chat.id,
        message.message_id
    )
    if message.left_chat_member.id == BOT_ID:
        # Bot was removed from the group
        # Mark in the db that the group is deleted
        await Group.delete_group(message.chat.id)
    else:
        # User left from the group
        # Mark in the db that user is deleted
        await UserToGroup.delete_user_from_group(
            message.left_chat_member,
            message.chat.id
        )


@dp.message_handler(
    lambda msg: msg.chat.type == 'supergroup',
    content_types=[ContentType.AUDIO, ContentType.VIDEO,
                   ContentType.VIDEO_NOTE, ContentType.VOICE,
                   ContentType.PHOTO, ContentType.DOCUMENT])
async def media_handler(message):
    # if media off - delete message
    await bot.delete_message(
        message.chat.id,
        message.message_id
    )


@dp.message_handler(
    lambda msg: msg.chat.type == 'supergroup',
    content_types=[ContentType.STICKER])
async def handle_stickers(message):
    # if user days > 7 days => can send stickers
    if await UserToGroup.can_send_sticker(message.from_user, message.chat):
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )


@dp.message_handler(lambda msg: msg.chat.type == 'supergroup')
async def all(message):
    # Check messages in the group (link)
    if await search_link(message.text):
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
