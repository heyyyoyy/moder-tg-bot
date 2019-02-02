from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re

from callback_factory import spam, admin_menu


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


async def search_link(message):
    result = re.search(PATTERN_URL, message)
    if result is not None:
        domain = result.groups()[2]
        # if domain not in link list => return true
        return True
    return False


async def admin_panel():
    mode = 't'
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        *(InlineKeyboardButton(
            f'{"✅" if mode == "t" else "☑️"} Join',
            callback_data=admin_menu.new(mode='t', action='join')),
          InlineKeyboardButton(
              f'{"✅" if mode == "t" else "☑️"} Check user',
              callback_data=admin_menu.new(mode='t', action='check')),
          InlineKeyboardButton(
              f'{"✅" if mode == "t" else "☑️"} Left',
              callback_data=admin_menu.new(mode='t', action='left')),
          InlineKeyboardButton(
              'Links',
              callback_data=admin_menu.new(mode='t', action='links')),
          InlineKeyboardButton(
              f'{"✅" if mode == "t" else "☑️"} Media',
              callback_data=admin_menu.new(mode='t', action='media')),
          InlineKeyboardButton(
              'Download',
              callback_data=admin_menu.new(mode='t', action='download')))
    )
    return (
        'Добро пожаловать в управление ботом! Выберите интересующий вас пункт',
        markup
    )
