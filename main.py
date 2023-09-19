import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram.utils.markdown import hbold
from config import BOT_TOKEN

TOKEN = BOT_TOKEN

dp = Dispatcher()
myrouter = Router()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
button_yes = InlineKeyboardButton(text='ДА', callback_data='button_yes')
button_no = InlineKeyboardButton(text='НЕТ', callback_data='button_no')

kb_yes_no = InlineKeyboardMarkup(inline_keyboard=[[button_yes, button_no]])


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!\n"
                         f"Вычислить индекс массы?",
                         reply_markup=kb_yes_no)


@dp.callback_query(F.data == 'button_yes')
async def yes_handler(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text='''Отлично, укажите свой вес (кг) и рост (см) 
                           через пробел, например 55 165:''')


@dp.callback_query(F.data == 'button_no')
async def yes_handler(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text='''Жаль, напишите /start как надумаете...''')


@dp.message(F.text.regexp(r'\d+'))
async def get_params(message: Message):

    _weight, _height = map(float, message.text.split())
    _height /= 100
    _bmi = calculate_bmi(_weight, _height)

    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Индекс вашего тела:{_bmi:.1f}')

    if _bmi < 18.5:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Недостаточная масса тела [до 18.5]')
    elif 18.5 <= _bmi < 24.9:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Нормальная масса тела [18.5 - 24.9]')
    elif 24.9 <= _bmi < 29.9:
        await bot.send_message(chat_id=message.from_user.id,
                               text='''Избыточная масса тела (предожирение)
                                [24.9 - 29.9]''')
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Ожирение [более 29.9]')

    await message.answer(f"{hbold(message.from_user.full_name)}!\n"
                         f"Вычислить еще раз индекс массы?",
                         reply_markup=kb_yes_no)


@dp.message(F.text.regexp(r'\w+'))
async def get_params(message: Message):
    await message.answer(f"{hbold(message.from_user.full_name)}!\n"
                         f"нужно указать 2 числа через пробел, например 55 165")


def calculate_bmi(_weight, _height):
    """
    Рассчитать индекс массы тела (BMI).
    :param _weight: Вес в кг.
    :param _height: Рост в метрах (например: 1.75).
    :return: Index of mass.
    """
    return _weight / (_height ** 2)


async def main() -> None:
    # bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


