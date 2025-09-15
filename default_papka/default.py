from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def menu_button(podpiska: bool):
    if podpiska:
        keyboard = [
            [KeyboardButton(text='Отписаться')],
            [KeyboardButton(text='Изменить дату')]
        ]
    else:
        keyboard = [
            [KeyboardButton(text='Подписаться')],
            [KeyboardButton(text='Изменить дату')]
        ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)