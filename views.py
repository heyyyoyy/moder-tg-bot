from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
import re


spam = CallbackData('spam', 'id', 'action')
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
