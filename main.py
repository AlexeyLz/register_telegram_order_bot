import asyncio
import logging
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import PreCheckoutQuery, ContentType
from dotenv import load_dotenv

from keyboards import get_menu_keyboard, get_direction_keyboard, get_platform_keyboard, get_purchase_keyboard, \
    get_admin_menu_keyboard
from states import OrderState, AdminMessageState
from database import connection

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

registration_data = {}
admin_ids = [716775112]


def reg_user(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()
    if len(data) > 0:
        cursor.close()
        return
    cursor.execute('INSERT INTO users (user_id, balance) VALUES(%s, %s)', (user_id, 0))
    connection.commit()
    cursor.close()


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    if message.from_user.id in admin_ids:
        await message.answer("Выберите нужный пункт", reply_markup=get_admin_menu_keyboard())
    else:
        await message.answer("Выберите нужный пункт", reply_markup=get_menu_keyboard())
    reg_user(message.from_user.id)


@dp.message_handler(Text('Отправить сообщение пользователям'))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in admin_ids:
        return
    await message.answer("Введите сообщение, которое хотите всем отправить?")
    await AdminMessageState.message.set()


@dp.message_handler(state=AdminMessageState.message)
async def get_admin_message(message: types.Message, state: FSMContext):
    message_to_send = message.text
    await state.finish()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM users")
    data = cursor.fetchall()
    cursor.close()
    for user_data in data:
        user_id = user_data[0]
        try:
            await bot.send_message(user_id, message_to_send)
        except:
            print(f'Сообщение id = {user_id} не отправлено')


@dp.message_handler(Text('Мой баланс'))
async def cmd_balance(message: types.Message):
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (message.from_user.id,))
    balance = cursor.fetchall()[0][0]
    cursor.close()
    await message.answer(f'У вас {balance} условных единиц')


@dp.message_handler(Text('Оставить заявку'))
async def cmd_application(message: types.Message):
    await message.answer("Какое направление вашего бизнеса", reply_markup=get_direction_keyboard())
    registration_data[message.from_user.id] = asyncio.get_event_loop().time()
    await OrderState.direction.set()


@dp.message_handler(state=OrderState.direction)
async def get_direction(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await message.answer("На какой платформе вы хотите разработать чат-бот?", reply_markup=get_platform_keyboard())
    registration_data[message.from_user.id] = asyncio.get_event_loop().time()
    await OrderState.next()


@dp.message_handler(state=OrderState.platform)
async def get_platform(message: types.Message, state: FSMContext):
    await state.update_data(platform=message.text)
    await message.answer("Какой у вас бюджет? Введите от и до")
    registration_data[message.from_user.id] = asyncio.get_event_loop().time()
    await OrderState.next()


@dp.message_handler(state=OrderState.budget)
async def get_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Введите свой номер телефона")
    registration_data[message.from_user.id] = asyncio.get_event_loop().time()
    await OrderState.next()


@dp.message_handler(state=OrderState.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    del registration_data[message.from_user.id]
    data = await state.get_data()
    await state.finish()
    for i in admin_ids:
        try:
            await bot.send_message(i, f"Новая заявка:\nНаправление:{data['direction']}\nПлатформа:{data['platform']}\n"
                                      f"Бюджет:{data['budget']}\nНомер телефона:{data['phone_number']}")
        except:
            pass
    await cmd_start(message)


@dp.message_handler(Text('Купить товар'))
async def cmd_purchase(message: types.Message):
    await message.answer("Сколько раз хотите купить?", reply_markup=get_purchase_keyboard())


@dp.callback_query_handler()
async def callbacks_num_start(call: types.CallbackQuery):
    action = call.data.split("_")[1]
    if action == "1":
        await bot.send_invoice(chat_id=call.from_user.id, title='Покупка 1', description='Купить 1 раз', payload='sub1',
                               provider_token='381764678:TEST:60122', currency='RUB', start_parameter='test',
                               prices=[{'label': "Руб", "amount": 10000}])
    elif action == "2":
        await bot.send_invoice(chat_id=call.from_user.id, title='Покупка 2', description='Купить 2 раза',
                               payload='sub2',
                               provider_token='381764678:TEST:60122', currency='RUB', start_parameter='test',
                               prices=[{'label': "Руб", "amount": 20000}])


@dp.pre_checkout_query_handler()
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


def add_balance(user_id, count):
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    balance = cursor.fetchall()[0][0]
    cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (int(balance) + int(count), user_id))
    connection.commit()
    cursor.close()


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def payment(message: types.Message):
    if message.successful_payment.invoice_payload == 'sub1':
        add_balance(message.from_user.id, 1)
    elif message.successful_payment.invoice_payload == 'sub2':
        add_balance(message.from_user.id, 2)


async def remind_inactive_users():
    remind_time = 600  # in seconds
    while True:
        await asyncio.sleep(remind_time)
        current_time = asyncio.get_event_loop().time()
        inactive_users = [
            user_id for user_id, registration_time in registration_data.items()
            if current_time - registration_time > remind_time
        ]
        for user_id in inactive_users:
            await bot.send_message(user_id, "Ты забыл заполнить заявку!")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('Я тебя на понимаю. Пропиши /start')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(remind_inactive_users())
    executor.start_polling(dp, skip_updates=True)
