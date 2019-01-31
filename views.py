from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

spam = CallbackData('spam', 'id', 'action')


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
