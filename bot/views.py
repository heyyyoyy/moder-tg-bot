from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove)
import re

from .settings import redis, _i18n
from .callback_factory import spam, admin_menu, group_cb, back
from .models import Link, Group, manager


PATTERN_URL = re.compile(r'(https?:\/\/)?(\w+\.)?([-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b)([-a-zA-Z0-9@:%_\+.~#?&//=]*)')


async def check_user(member):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            _i18n('Confirm'),
            callback_data=spam.new(id=str(member.id), action='filter'))
    )
    link = '<a href="tg://user?id={0}">{1}</a>'.format(
            member.id, member.first_name)
    return (
        _i18n('Hello {link}! Click the button below '
              'and confirm that you are a live user!').format(
            link=link
        ),
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


async def search_link(message, group_id):
    result = re.search(PATTERN_URL, message)
    if result is not None:
        domain = result.groups()[2]
        # if domain not in link list => return true
        links = await manager.execute(Link.select().where(
            (Link.group == group_id) & (Link.url == domain)))
        if not links:
            return True
    return False


async def get_settings(group_id):
    pipe = redis.pipeline()
    pipe.get(f'{group_id}:join')
    pipe.get(f'{group_id}:check_user')
    pipe.get(f'{group_id}:left')
    pipe.get(f'{group_id}:media')
    result = await pipe.execute()
    return (m.decode() for m in result)


async def save_settings(group_id):
    pipe = redis.pipeline()
    pipe.set(f'{group_id}:join', 't')
    pipe.set(f'{group_id}:check_user', 't')
    pipe.set(f'{group_id}:left', 't')
    pipe.set(f'{group_id}:media', 't')
    await pipe.execute()


async def main_menu():
    groups = await manager.execute(
        Group.select().where(~Group.deleted)
    )
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *(
            InlineKeyboardButton(
                group.title,
                callback_data=group_cb.new(
                    id=str(group.id), action='main'
                )
            )
            for group in groups
        )
    )
    return (
        'Добро пожаловать в управление ботом! '
        'Выберите интересующую вас группу',
        markup
    )


async def admin_panel(group_id):
    join_mode, check_user_mode, left_mode, media_mode = await get_settings(group_id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *(InlineKeyboardButton(
            f'{"✅" if join_mode == "t" else "☑️"} Присоединился',
            callback_data=admin_menu.new(
                id=group_id, mode=join_mode, action='join')),
          InlineKeyboardButton(
              f'{"✅" if check_user_mode == "t" else "☑️"} Проверка пользователя',
              callback_data=admin_menu.new(
                  id=group_id, mode=check_user_mode, action='check_user')),
          InlineKeyboardButton(
              f'{"✅" if left_mode == "t" else "☑️"} Покинул',
              callback_data=admin_menu.new(
                  id=group_id, mode=left_mode, action='left')),
          InlineKeyboardButton(
              'Ссылки',
              callback_data=admin_menu.new(
                  id=group_id, mode='t', action='links')),
          InlineKeyboardButton(
              f'{"✅" if media_mode == "t" else "☑️"} Вложения',
              callback_data=admin_menu.new(
                  id=group_id, mode=media_mode, action='media')),
          InlineKeyboardButton(
              'Скачать',
              callback_data=admin_menu.new(
                  id=group_id, mode='t', action='download')))
    )
    markup.add(
        InlineKeyboardButton(
            'Назад', callback_data=back.new(action='back')
            )
    )
    return (
        'Выберите интересующий вас пункт',
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


async def save_link(link, group_id):
    url = re.search(PATTERN_URL, link)
    if url is not None:
        domain = url.groups()[2]
        await manager.get_or_create(Link, group=group_id, url=domain)
        return ('Ссылка добавлена', True, ReplyKeyboardRemove()), await admin_panel(group_id)

    return ('Вы ввели неправильную ссылку', False, None), None
