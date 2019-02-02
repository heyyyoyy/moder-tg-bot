from aiogram.dispatcher.filters import BoundFilter

from settings import ADMIN


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message):
        return ADMIN == message.from_user.id
