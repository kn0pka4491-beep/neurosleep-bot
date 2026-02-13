
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
        "Этот тест помогает оценить\n"
        "*восстановительную функцию сна*.\n\n"
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
    await state.reset_state()
    await state.set_state(SleepTest.q1)
    await ask_q1(callback.message)


# ======================
# QUESTIONS
# ======================
async def ask_q1(message):
    await message.answer(
        "🕰 *Вопрос 1*\n\nСколько времени нужно, чтобы уснуть?",
        reply_markup=kb("q1"),
        parse_mode="Markdown"
    )


async def ask_q2(message):
    await message.answer(
        "🌙 *Вопрос 2*\n\nКак часто просыпаешься ночью?",
        reply_markup=kb("q2"),
        parse_mode="Markdown"
    )


async def ask_q3(message):
    await message.answer(
        "☀️ *Вопрос 3*\n\nКак чувствуешь себя утром?",
        reply_markup=kb("q3"),
        parse_mode="Markdown"
    )


async def ask_q4(message):
    await message.answer(
        "🕰 *Вопрос 4*\n\nВо сколько обычно ложишься спать?",
        reply_markup=kb("q4"),
        parse_mode="Markdown"
    )


async def ask_q5(message):
    keyboard = kb("q5")
    keyboard.add(types.InlineKeyboardButton("✅ Завершить тест", callback_data="finish"))
    await message.answer(
        "😴 *Вопрос 5*\n\nЕсть ли дневная сонливость?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ======================
# KEYBOARDS
# ======================
def kb(prefix):
    options = {
        "q1": ["😴 До 15 мин", "🙂 15–30 мин", "😕 30–60 мин", "😣 > часа"],
        "q2": ["🌙 Не просыпаюсь", "😴 1 раз", "😕 2–3 раза", "😣 ≥4 раз"],
        "q3": ["☀️ Отдохнувшим", "🙂 Нормально", "😕 Уставшим", "😣 Разбитым"],
        "q4": ["🕰 До 23:00", "🌙 23–00", "🌌 00–01", "🌃 После 01"],
        "q5": ["🙂 Почти нет", "😕 Иногда", "😴 Часто", "😣 Почти всегда"],
    }

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for i, text in enumerate(options[prefix]):
        keyboard.add(types.InlineKeyboardButton(text, callback_data=f"{prefix}_{i}"))
    return keyboard


# ======================
# ANSWERS
# ======================
@dp.callback_query_handler(lambda c: c.data.startswith("q"), state="*")
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    prefix, value = callback.data.split("_")
    await state.update_data({prefix: int(value)})
    await callback.answer()

    next_step = {
        "q1": (SleepTest.q2, ask_q2),
        "q2": (SleepTest.q3, ask_q3),
        "q3": (SleepTest.q4, ask_q4),
        "q4": (SleepTest.q5, ask_q5),
    }

    if prefix in next_step:
        new_state, func = next_step[prefix]
        await state.set_state(new_state)
        await func(callback.message)


# ======================
# FINISH
# ======================
@dp.callback_query_handler(lambda c: c.data == "finish", state=SleepTest.q5)
async def finish(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = sum(data.values())

    if score <= 4:
        level = "🟢 Физиологически сохранённый сон"
    elif score <= 8:
        level = "🟡 Пограничное состояние"
    elif score <= 12:
        level = "🟠 Функциональные нарушения сна"
    else:
        level = "🔴 Высокий риск хронического нарушения"

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🔍 Разбор параметров сна", callback_data="details"),
        types.InlineKeyboardButton("🌙 Что можно улучшить", callback_data="improve"),
        types.InlineKeyboardButton("🔁 Пройти тест снова", callback_data="start_test"),
    )

    await callback.message.answer(
        f"🧠 *Результат теста сна*\n\n"
        f"{level}\n\n"
        "ℹ️ Это ориентир, а не диагноз.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.finish()
    await callback.answer()


# ======================
# EXTRA
# ======================
@dp.callback_query_handler(lambda c: c.data == "improve")
async def improve(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🌙 *Что улучшает сон уже сегодня:*\n\n"
        "• 🕰 стабильный режим\n"
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
