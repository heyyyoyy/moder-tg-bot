from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove)
import re

from .settings import redis
from .callback_factory import spam, admin_menu, group_cb
from .models import Link, Group, manager


PATTERN_URL = re.compile(r'(https?:\/\/)?(\w+\.)?([-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b)([-a-zA-Z0-9@:%_\+.~#?&//=]*)')


async def check_user(member):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            'Подтвердить',
            callback_data=spam.new(id=str(member.id), action='filter'))
    )
    return (
        'Привет <a href="tg://user?id={0}">{1}</a>! '
        'Чтобы убедиться, что вы не '
        'спамер нажмите на кнопку Подтвердить и '
        'тогда вам будет разрешено писать в чат'.format(
            member.id, member.first_name),
        markup
    )


async def check_admin(bot, message):
    admins = await redis.lrange(
        message.chat.id, 0, await redis.llen(message.chat.id))
    if not admins:
        chat_members = await bot.get_chat_administrators(
            message.chat.id
        )
        chat_members = [member.user.id for member in chat_members]
        for member in chat_members:
            await redis.lpush(
                message.chat.id,
                member
            )
        await redis.expire(
            message.chat.id,
            60*60
        )
        if message.from_user.id in chat_members:
            return True

    admins = map(int, admins)
    if message.from_user.id in admins:
        return True


async def search_link(message):
    result = re.search(PATTERN_URL, message)
    if result is not None:
        domain = result.groups()[2]
        # if domain not in link list => return true
        links = await manager.execute(Link.select().where(Link.url == domain))
        if not links:
            return True
    return False


async def get_settings():
    pipe = redis.pipeline()
    pipe.get('join')
    pipe.get('check_user')
    pipe.get('left')
    pipe.get('media')
    result = await pipe.execute()
    return (m.decode() for m in result)


async def admin_panel():
    join_mode, check_user_mode, left_mode, media_mode = await get_settings()
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *(InlineKeyboardButton(
            f'{"✅" if join_mode == "t" else "☑️"} Присоединился',
            callback_data=admin_menu.new(mode=join_mode, action='join')),
          InlineKeyboardButton(
              f'{"✅" if check_user_mode == "t" else "☑️"} Проверка пользователя',
              callback_data=admin_menu.new(mode=check_user_mode, action='check_user')),
          InlineKeyboardButton(
              f'{"✅" if left_mode == "t" else "☑️"} Покинул',
              callback_data=admin_menu.new(mode=left_mode, action='left')),
          InlineKeyboardButton(
              'Ссылки',
              callback_data=admin_menu.new(mode='t', action='links')),
          InlineKeyboardButton(
              f'{"✅" if media_mode == "t" else "☑️"} Вложения',
              callback_data=admin_menu.new(mode=media_mode, action='media')),
          InlineKeyboardButton(
              'Скачать',
              callback_data=admin_menu.new(mode='t', action='download')))
    )
    return (
        'Добро пожаловать в управление ботом! Выберите интересующий вас пункт',
        markup
    )


async def get_link_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Отмена'))
    return (
        'Введите название сайта, например '
        '<code>vk.com</code> и я не буду удалять '
        'все ссылки связанные с ним. Если хотите '
        'выйти нажмите Отмена',
        markup
    )


async def save_link(link):
    url = re.search(PATTERN_URL, link)
    if url is not None:
        domain = url.groups()[2]
        await manager.get_or_create(Link, url=domain)
        return ('Ссылка добавлена', True, ReplyKeyboardRemove()), await admin_panel()

    return ('Вы ввели неправильную ссылку', False, None), None


async def create_grouplist():
    groups = await manager.execute(Group.select())
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *(
            InlineKeyboardButton(
                group.title,
                callback_data=group_cb.new(id=str(group.id), action='load'))
            for group in groups
        )
    )
    return (
        'Выберите группу из которой хотите скачать базу',
        markup
    )
