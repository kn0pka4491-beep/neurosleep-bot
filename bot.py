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

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Сон — это результат работы биологических механизмов.\n\n"
        "Ответь на 10 вопросов и получи предварительную оценку факторов сна.\n\n"
        "Нажми /test чтобы начать."
    )

@dp.message_handler(commands=["test"])
async def test(message: types.Message):
    await message.answer("Тест запускается. Следующий шаг — добавим вопросы.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
