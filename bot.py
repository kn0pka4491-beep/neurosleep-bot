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
    raise ValueError("BOT_TOKEN is not set")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

CHANNEL_URL = "https://t.me/neuro_sleep_science"


# ======================
# STATES
# ======================
class SleepTest(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()


# ======================
# START
# ======================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🧠 Пройти тест сна", callback_data="start_test"),
        types.InlineKeyboardButton("📘 Перейти в канал", url=CHANNEL_URL),
    )

    await message.answer(
        "🌙 *Neuro Sleep Science*\n\n"
        "Тест оценивает восстановительную функцию сна.\n\n"
        "⚠️ Не является диагнозом.\n\n"
        "Готовы начать?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ======================
# START TEST
# ======================
@dp.callback_query_handler(lambda c: c.data == "start_test")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.finish()
    await state.set_state(SleepTest.q1)
    await ask_question(callback.message, 1)


# ======================
# QUESTIONS
# ======================
QUESTIONS = {
    1: ("🕰 *Вопрос 1*\n\nСколько времени нужно, чтобы уснуть?",
        ["😴 До 15 мин", "🙂 15–30 мин", "😕 30–60 мин", "😣 Более часа"]),
    2: ("🌙 *Вопрос 2*\n\nКак часто просыпаешься ночью?",
        ["🌙 Не просыпаюсь", "😴 1 раз", "😕 2–3 раза", "😣 4+ раз"]),
    3: ("☀️ *Вопрос 3*\n\nКак чувствуешь себя утром?",
        ["☀️ Отдохнувшим", "🙂 Нормально", "😕 Уставшим", "😣 Разбитым"]),
    4: ("🕰 *Вопрос 4*\n\nВо сколько обычно ложишься спать?",
        ["🕰 До 23:00", "🌙 23–00", "🌌 00–01", "🌃 После 01"]),
    5: ("😴 *Вопрос 5*\n\nЕсть ли дневная сонливость?",
        ["🙂 Почти нет", "😕 Иногда", "😴 Часто", "😣 Почти всегда"]),
}


async def ask_question(message, number):
    text, answers = QUESTIONS[number]
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for i, ans in enumerate(answers):
        keyboard.add(
            types.InlineKeyboardButton(ans, callback_data=f"q{number}_{i}")
        )

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


# ======================
# ANSWERS HANDLER
# ======================
@dp.callback_query_handler(lambda c: c.data.startswith("q"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    q, value = callback.data.split("_")
    question_number = int(q[1])

    await state.update_data({q: int(value)})

    if question_number < 5:
        await state.set_state(getattr(SleepTest, f"q{question_number + 1}"))
        await ask_question(callback.message, question_number + 1)
    else:
        await finish_test(callback, state)


# ======================
# FINISH TEST
# ======================
async def finish_test(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = sum(data.values())

    if score <= 4:
        result = "🟢 *Физиологически сохранённый сон*"
    elif score <= 8:
        result = "🟡 *Пограничное состояние сна*"
    elif score <= 12:
        result = "🟠 *Функциональные нарушения сна*"
    else:
        result = "🔴 *Высокий риск хронического нарушения сна*"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🌙 Что можно улучшить", callback_data="improve"),
        types.InlineKeyboardButton("🔁 Пройти тест снова", callback_data="start_test"),
        types.InlineKeyboardButton("📘 Читать канал", url=CHANNEL_URL),
    )

    await callback.message.answer(
        f"🧠 *Результат теста сна*\n\n"
        f"{result}\n\n"
        "ℹ️ Это ориентир, а не диагноз.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.finish()


# ======================
# IMPROVE
# ======================
@dp.callback_query_handler(lambda c: c.data == "improve")
async def improve(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🌙 *Что улучшает сон уже сегодня:*\n\n"
        "• 🕰 стабильное время сна\n"
        "• 📵 без экранов за 60 мин\n"
        "• ☀️ утренний свет\n"
        "• 🚶 движение днём",
        parse_mode="Markdown"
    )


# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
