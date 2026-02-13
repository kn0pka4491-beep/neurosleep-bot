import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# --------------------
# НАСТРОЙКИ
# --------------------
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --------------------
# FSM
# --------------------
class SleepTest(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()

# --------------------
# /start
# --------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup(row_width=1)

    kb.add(
        types.InlineKeyboardButton(
            text="📘 Перейти в канал",
            url="https://t.me/neuro_sleep_science"
        ),
        types.InlineKeyboardButton(
            text="🧠 Пройти тест сна",
            callback_data="start_test"
        )
    )

    await message.answer(
        "Привет 🌙\n"
        "Я — бот канала Neuro Sleep Science.\n\n"
        "Я помогу тебе:\n"
        "• лучше понять свой сон\n"
        "• увидеть возможные причины усталости\n"
        "• получить первые ориентиры для улучшения сна\n\n"
        "С чего начнём? 👇",
        reply_markup=kb
    )

# --------------------
# СТАРТ ТЕСТА
# --------------------
@dp.callback_query_handler(lambda c: c.data == "start_test")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(score=0)
    await SleepTest.q1.set()

    await send_question(
        callback.message,
        "Как быстро ты обычно засыпаешь?",
        "q1",
        [
            ("😴 До 15 минут", 0),
            ("🌙 15–30 минут", 1),
            ("⏳ 30–60 минут", 2),
            ("🧠 Больше часа", 3),
        ]
    )

# --------------------
# УНИВЕРСАЛЬНЫЙ ВОПРОС
# --------------------
async def send_question(message, text, q, options):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for label, value in options:
        kb.add(types.InlineKeyboardButton(
            text=label,
            callback_data=f"{q}_{value}"
        ))
    await message.answer(text, reply_markup=kb)

# --------------------
# ОБРАБОТЧИК ОТВЕТОВ
# --------------------
async def process_answer(callback, state, next_state, question_text, options):
    data = await state.get_data()
    score = data["score"]
    points = int(callback.data.split("_")[1])

    await state.update_data(score=score + points)
    await callback.answer()

    if next_state:
        await next_state.set()
        await send_question(callback.message, question_text, next_state.state, options)
    else:
        await finish_test(callback.message, state)

# --------------------
# ВОПРОСЫ
# --------------------
@dp.callback_query_handler(lambda c: c.data.startswith("q1_"), state=SleepTest.q1)
async def q1(callback, state):
    await process_answer(
        callback, state, SleepTest.q2,
        "Просыпаешься ли ты ночью?",
        [
            ("🌑 Нет", 0),
            ("🌒 1 раз", 1),
            ("🌗 2–3 раза", 2),
            ("🌕 4 и более", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q2_"), state=SleepTest.q2)
async def q2(callback, state):
    await process_answer(
        callback, state, SleepTest.q3,
        "Просыпаешься слишком рано и не можешь уснуть?",
        [
            ("🙏 Почти никогда", 0),
            ("😐 1–2 раза в неделю", 1),
            ("😣 3–4 раза", 2),
            ("😵 Почти каждый день", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q3_"), state=SleepTest.q3)
async def q3(callback, state):
    await process_answer(
        callback, state, SleepTest.q4,
        "Сколько часов ты обычно спишь?",
        [
            ("🛌 7,5–9", 0),
            ("🙂 6,5–7,5", 1),
            ("😕 5,5–6,5", 2),
            ("😴 < 5,5", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q4_"), state=SleepTest.q4)
async def q4(callback, state):
    await process_answer(
        callback, state, SleepTest.q5,
        "Как ты чувствуешь себя утром?",
        [
            ("✨ Отдохнув(а)", 0),
            ("🙂 Нормально", 1),
            ("😐 Уставший(ая)", 2),
            ("🧟 Очень разбит(а)", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q5_"), state=SleepTest.q5)
async def q5(callback, state):
    await process_answer(
        callback, state, SleepTest.q6,
        "Клонит ли тебя в сон днём?",
        [
            ("💪 Почти никогда", 0),
            ("😌 Иногда", 1),
            ("😴 Часто", 2),
            ("🛑 Почти всегда", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q6_"), state=SleepTest.q6)
async def q6(callback, state):
    await process_answer(
        callback, state, SleepTest.q7,
        "Насколько стабилен твой режим сна?",
        [
            ("⏰ Стабилен", 0),
            ("🕰 ±1 час", 1),
            ("🌀 ±2 часа", 2),
            ("🌪 Хаос", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q7_"), state=SleepTest.q7)
async def q7(callback, state):
    await process_answer(
        callback, state, SleepTest.q8,
        "Используешь ли телефон перед сном?",
        [
            ("🌿 Нет", 0),
            ("🙂 Редко", 1),
            ("📱 Почти всегда", 2),
            ("🌃 Всегда", 3),
        ]
    )

@dp.callback_query_handler(lambda c: c.data.startswith("q8_"), state=SleepTest.q8)
async def q8(callback, state):
    await process_answer(callback, state, None, None, None)

# --------------------
# ФИНАЛ
# --------------------
async def finish_test(message, state: FSMContext):
    data = await state.get_data()
    score = data["score"]

    if score <= 5:
        text = "🟢 Сон в норме.\nСтруктура сна сохранена."
    elif score <= 10:
        text = "🟡 Лёгкие нарушения сна.\nЕсть корректируемые факторы."
    elif score <= 15:
        text = "🟠 Умеренные нарушения.\nСон не даёт полного восстановления."
    else:
        text = "🔴 Выраженные проблемы сна.\nОрганизму нужна поддержка."

    await message.answer(
        f"🧠 Результат теста\n\n"
        f"Баллы: {score}\n\n"
        f"{text}\n\n"
        "⚠️ Это не диагноз, а ориентир.\n"
        "В канале — разборы и рекомендации."
    )

    await state.finish()

# --------------------
# ЗАПУСК
# --------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
