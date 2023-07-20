import asyncio
import re
import pandas as pd
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from decouple import config

from database import db_connect

API_TOKEN = config('BOT_TOKEN')
db = db_connect()

bot = Bot(token=API_TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class MyForm(StatesGroup):
    waiting_for_input = State()


class ErrorExistsUser(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


def check_auth(user_id):
    user_id = db['tg_bot_users'].find_one({'user_id': user_id})
    if not user_id:
        return False
    return True


@dp.message_handler(commands=['start', 'help'])
async def auth(message: types.Message):
    if not check_auth(message.from_user.id):
        await message.reply(
            "Для авторизации введите имя пользователя и код доступа через пробел в формате: `username 0000`")
        await MyForm.waiting_for_input.set()
    else:
        await message.reply("Вы уже авторизованы")


@dp.message_handler(state=MyForm.waiting_for_input)
async def process_input(message: types.Message, state: FSMContext):
    input_value = message.text
    try:
        username = input_value.split(' ')[0]
        code = input_value.split(' ')[1]

        user = db['tg_bot_users'].find_one({'username': username, 'code': code})
        if not user:
            raise IndexError

        if user.get('user_id'):
            raise ErrorExistsUser

        db['tg_bot_users'].find_one_and_update({'username': username},
                                               {'$set': {'user_id': message.from_user.id,
                                                         'send_allow': True}},
                                               upsert=True)
        await message.reply("Вы успешно авторизовались.")
        await state.finish()
    except IndexError:
        await message.reply("Ошибка. Проверьте вводимые данные.")
    except ErrorExistsUser:
        await message.reply("Пользователь с такими данными уже привязан к другому аккаунту.")


@dp.message_handler(commands=['actives'])
async def auth(message: types.Message):
    if not check_auth(message.from_user.id):
        await message.reply('Вы не авторизованы. /start для авторизации.')
        return

    username = db['tg_bot_users'].find_one({'user_id': message.from_user.id})['username']

    collection_actives = db['users_actives']
    actives = list(collection_actives.find({'username': username}, {'_id': 0}))
    if not actives:
        return {'error': 'empty', 'error_type': '0'}
    fonds = [data['active'].upper() for data in actives if data['type_active'] == 'fonds']
    crypto = [data['active'].upper() for data in actives if data['type_active'] == 'crypto']

    fonds_msg = str(fonds).strip('[]').replace('\'', '') if fonds else 'отсутствуют'
    crypto_msg = str(crypto).strip('[]').replace('\'', '') if crypto else 'отсутствуют'

    await message.reply(f'<i>Активы, добавленные вами на сайте:</i>\n'
                        f'<b>Фондовый рынок:</b> {fonds_msg}\n'
                        f'<b>Криптовалютный рынок:</b> {crypto_msg}')


@dp.message_handler(commands=['notifon'])
async def notification_on(message: types.Message):
    if not check_auth(message.from_user.id):
        await message.reply('Вы не авторизованы. /start для авторизации.')
        return
    db['tg_bot_users'].find_one_and_update({'user_id': message.from_user.id},
                                           {'$set': {'send_allow': True}},
                                           upsert=True)
    await message.reply('Уведомления о сигналах включены.\n'
                        'Для отключения используйте /notifoff')


@dp.message_handler(commands=['notifoff'])
async def notification_off(message: types.Message):
    if not check_auth(message.from_user.id):
        await message.reply('Вы не авторизованы. /start для авторизации.')
        return
    db['tg_bot_users'].find_one_and_update({'user_id': message.from_user.id},
                                           {'$set': {'send_allow': False}},
                                           upsert=True)
    await message.reply('Уведомления о сигналах выключены.\n'
                        'Для включения используйте /notifon')


@dp.message_handler(commands=['logout'])
async def logout(message: types.Message):
    if not check_auth(message.from_user.id):
        await message.reply('Вы не авторизованы. /start для авторизации.')
        return
    db['tg_bot_users'].find_one_and_update({'user_id': message.from_user.id},
                                           {'$set': {'user_id': '',
                                                     'send_allow': True}},
                                           upsert=True)
    await message.reply('Вы больше не авторизованы.\n'
                        'Для авторизации используйте /start')


async def send_notifications_executor():
    while True:
        await asyncio.sleep(5)
        notifications = list(db['tg_notifications'].find({'is_send': False, 'user_id': {'$ne': None}}))
        if notifications:
            await send_notifications(notifications)


async def send_notifications(notifications):
    for notif in notifications:
        send_check = db['tg_bot_users'].find_one({'username': notif['username']})
        if send_check['send_allow'] and send_check['user_id']:
            type_active = 'фондовый рынок' if notif["type_active"] == 'fonds' else 'криптовалютный рынок'

            signals = []
            for signal in notif["signals"]:
                if signal == 'ma':
                    signals.append('Средняя скользящая (MA)')
                if signal == 'rsi':
                    signals.append('Индекс относительной силы (RSI)')
                if signal == 'bollinger':
                    signals.append('Линии Боллинджера')
                if signal == 'talib':
                    signals.append('Свечные индикаторы')
                if signal == 'triangle':
                    signals.append('Фигура треугольник')
            msg_signals = str(signals).strip('[]').replace('\'', '')

            await bot.send_message(notif['user_id'], (
                f'✅ <b>Новый сигнал</b> ({type_active})\n'
                f'<b>Актив:</b> {notif["active"]}\n'
                f'<b>Таймфрейм:</b> {notif["interval"]}\n'
                f'<b>Найденные индикаторы:</b> <i>{msg_signals}</i>'))

            await asyncio.sleep(3)

        db['tg_notifications'].find_one_and_update(
            {'username': notif['username'],
             'active': notif["active"],
             'interval': notif["interval"],
             'signals': notif["signals"]},
            {'$set': {'is_send': True}}, upsert=True)


async def bot_startup(dp):
    asyncio.create_task(send_notifications_executor())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=bot_startup)
