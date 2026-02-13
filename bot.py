import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

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

    await callback_query.message.answer(
        "🧠 Тест сна начинается.\n\n"
        "Сейчас задам первый вопрос."
    )
