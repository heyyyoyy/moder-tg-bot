from aiogram.utils.callback_data import CallbackData


spam = CallbackData('spam', 'id', 'action')
admin_menu = CallbackData('admin', 'id', 'mode', 'action')
group_cb = CallbackData('group', 'id', 'action')
back = CallbackData('back', 'action')
