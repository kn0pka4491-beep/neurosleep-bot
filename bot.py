import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class SleepTest(StatesGroup):
    q1 = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    channel_button = types.InlineKeyboardButton(
        text="📘 Перейти в канал",
        url="https://t.me/neuro_sleep_science"
    )

    test_button = types.InlineKeyboardButton(
        text="🧠 Пройти тест сна",
        callback_data="start_test"
    )

    keyboard.add(channel_button, test_button)

    await message.answer(
        "Привет 🌙\n"
        "Я — бот канала Neuro Sleep Science.\n\n"
        "Я помогу тебе:\n"
        "• лучше понять свой сон\n"
        "• увидеть возможные причины усталости\n"
        "• получить первые ориентиры для улучшения сна\n\n"
        "🔹 В канале — наука, исследования и разборы\n"
        "🔹 Здесь — персональный мини-тест\n\n"
        "С чего начнём? 👇",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data == "start_test")
async def start_test_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await SleepTest.q1.set()

    await callback_query.message.answer(
        "🧠 Тест сна начинается.\n\n"
        "❓ Вопрос 1:\n"
        "Во сколько ты обычно ложишься спать?"
    )


@dp.message_handler(state=SleepTest.q1)
async def process_q1(message: types.Message, state: FSMContext):
    await state.update_data(bedtime=message.text)

    await message.answer(
        "Спасибо 🌙\n"
        "Твой ответ сохранён.\n\n"
        "Дальше будет следующий вопрос."
    )

    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
