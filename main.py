import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from aiogram.utils.markdown import hbold
from config import BOT_TOKEN

TOKEN = BOT_TOKEN
TEXT_PREV_REQUEST = '''Отлично, укажите свой вес (кг) и рост (см) 
                    через пробел, например 55 165:'''
TEXT_IF_VALUE_ERROR = "нужно указать 2 числа через пробел, например: 55 165"


dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
button_yes = InlineKeyboardButton(text='ДА', callback_data='button_yes')
button_no = InlineKeyboardButton(text='НЕТ', callback_data='button_no')

kb_yes_no = InlineKeyboardMarkup(inline_keyboard=[[button_yes, button_no]])


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    await message.answer(f"Привет, {hbold(message.from_user.first_name)}!\n"
                         f"Вычислить индекс массы тела?",
                         reply_markup=kb_yes_no)


@dp.callback_query(F.data == 'button_yes')
async def yes_handler(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=TEXT_PREV_REQUEST)


@dp.callback_query(F.data == 'button_no')
async def yes_handler(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text='''Жаль, напишите /start как надумаете...''')


@dp.message(F.text.regexp(r'\d+'))
async def get_params(message: Message):
    try:
        _weight, _height = map(float, message.text.strip().split())
        _height /= 100
        _bmi = calculate_bmi(_weight, _height)

        if _bmi < 18.5:
            text_res = '[до 18.5] - Недостаточная масса тела'
        elif 18.5 <= _bmi < 24.9:
            text_res = '[18.5 - 24.9] - Нормальная масса тела'
        elif 24.9 <= _bmi < 29.9:
            text_res = '[24.9 - 29.9] - Избыточная масса тела (предожирение)'
        else:
            text_res = '[более 29.9] - Ожирение'
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Индекс вашего тела: {_bmi:.1f}\n'
                                    f'{text_res}')

    except ValueError:
        logging.basicConfig(filename='log.txt', level=logging.ERROR)
        await message.answer(f"{hbold(message.from_user.first_name)}!\n"
                             f"{TEXT_IF_VALUE_ERROR}")
    else:
        await message.answer(f"{hbold(message.from_user.first_name)}!\n"
                             f"Вычислить еще раз индекс массы?",
                             reply_markup=kb_yes_no)


@dp.message(F.text.regexp(r'\D+'))
async def get_incorrect_data(message: Message):
    logging.basicConfig(filename='log.txt', level=logging.ERROR)
    await message.answer(f"{hbold(message.from_user.first_name)},\n"
                         f"{TEXT_IF_VALUE_ERROR}")


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
