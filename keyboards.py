from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_keyboard():
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_keyboard.add(KeyboardButton('Оставить заявку'))
    menu_keyboard.add(KeyboardButton('Купить товар'))
    menu_keyboard.add(KeyboardButton('Мой баланс'))
    return menu_keyboard


def get_admin_menu_keyboard():
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_keyboard.add(KeyboardButton('Отправить сообщение пользователям'))
    menu_keyboard.add(KeyboardButton('Оставить заявку'))
    menu_keyboard.add(KeyboardButton('Купить товар'))
    menu_keyboard.add(KeyboardButton('Мой баланс'))
    return menu_keyboard


def get_direction_keyboard():
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    menu_keyboard.add(KeyboardButton('Продажа'))
    menu_keyboard.add(KeyboardButton('Производство'))
    menu_keyboard.add(KeyboardButton('Оказание услуг'))
    return menu_keyboard


def get_platform_keyboard():
    menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu_keyboard.add(KeyboardButton('Телеграмм'))
    menu_keyboard.add(KeyboardButton('Ватсап'))
    menu_keyboard.add(KeyboardButton('Вайбер'))
    return menu_keyboard


def get_purchase_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Купить 1 раз", callback_data="buy_1"))
    keyboard.add(InlineKeyboardButton(text="Купить 2 раза", callback_data="buy_2"))
    return keyboard
