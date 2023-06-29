from aiogram.dispatcher.filters.state import StatesGroup, State


class OrderState(StatesGroup):
    direction = State()
    platform = State()
    budget = State()
    phone_number = State()


class AdminMessageState(StatesGroup):
    message = State()