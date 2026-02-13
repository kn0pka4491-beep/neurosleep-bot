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
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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
        types.InlineKeyboardButton(
            text="🧠 Пройти тест сна",
            callback_data="start_test"
        ),
        types.InlineKeyboardButton(
            text="📘 Перейти в канал",
            url=CHANNEL_URL
        )
    )

    await message.answer(
        "🌙 Привет\n\n"
        "Я — бот канала *Neuro Sleep Science*.\n\n"
        "Я помогаю:\n"
        "• лучше понять, как работает твой сон\n"
        "• увидеть возможные причины усталости\n"
        "• получить научные ориентиры\n\n"
        "🧠 Тест основан на клинической логике,\n"
        "но *не является диагнозом*.\n\n"
        "С чего начнём? 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ======================
# START TEST
# ======================
@dp.callback_query_handler(lambda c: c.data == "start_test")
async def start_test(callback: types.CallbackQuery):
    await callback.answer()
    await SleepTest.q1.set()

    await callback.message.answer(
        "🧠 *Тест сна*\n\n"
        "❓ *Вопрос 1*\n"
        "⏳ Сколько времени тебе обычно нужно, чтобы уснуть?\n\n"
        "1️⃣ до 15 минут\n"
        "2️⃣ 15–30 минут\n"
        "3️⃣ 30–60 минут\n"
        "4️⃣ больше часа",
        parse_mode="Markdown"
    )

# ======================
# QUESTIONS
# ======================
@dp.message_handler(state=SleepTest.q1)
async def q1(message: types.Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await SleepTest.q2.set()

    await message.answer(
        "❓ *Вопрос 2*\n"
        "🌙 Как часто ты просыпаешься ночью?\n\n"
        "1️⃣ не просыпаюсь\n"
        "2️⃣ 1 раз\n"
        "3️⃣ 2–3 раза\n"
        "4️⃣ 4 и более",
        parse_mode="Markdown"
    )

@dp.message_handler(state=SleepTest.q2)
async def q2(message: types.Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await SleepTest.q3.set()

    await message.answer(
        "❓ *Вопрос 3*\n"
        "☀️ Как ты обычно чувствуешь себя утром?\n\n"
        "1️⃣ отдохнувшим(ей)\n"
        "2️⃣ скорее нормально\n"
        "3️⃣ уставшим(ей)\n"
        "4️⃣ разбитым(ой)",
        parse_mode="Markdown"
    )

@dp.message_handler(state=SleepTest.q3)
async def q3(message: types.Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await SleepTest.q4.set()

    await message.answer(
        "❓ *Вопрос 4*\n"
        "🕰 Во сколько ты обычно ложишься спать?\n\n"
        "1️⃣ до 23:00\n"
        "2️⃣ 23:00–00:00\n"
        "3️⃣ 00:00–01:00\n"
        "4️⃣ после 01:00",
        parse_mode="Markdown"
    )

@dp.message_handler(state=SleepTest.q4)
async def q4(message: types.Message, state: FSMContext):
    await state.update_data(q4=message.text)
    await SleepTest.q5.set()

    await message.answer(
        "❓ *Вопрос 5*\n"
        "😴 Бывает ли у тебя дневная сонливость?\n\n"
        "1️⃣ почти никогда\n"
        "2️⃣ иногда\n"
        "3️⃣ часто\n"
        "4️⃣ почти каждый день",
        parse_mode="Markdown"
    )

# ======================
# FINISH TEST
# ======================
@dp.message_handler(state=SleepTest.q5)
async def finish_test(message: types.Message, state: FSMContext):
    await state.update_data(q5=message.text)
    data = await state.get_data()

    score = 0
    for answer in data.values():
        if isinstance(answer, str) and answer.strip().isdigit():
            score += int(answer.strip()) - 1

    if score <= 4:
        result = "🟢 *Сон в пределах физиологической нормы*"
        level = "green"
    elif score <= 8:
        result = "🟡 *Признаки умеренного нарушения сна*"
        level = "yellow"
    elif score <= 12:
        result = "🟠 *Выраженные признаки нарушения структуры сна*"
        level = "orange"
    else:
        result = "🔴 *Высокая вероятность хронического нарушения сна*"
        level = "red"

    await state.update_data(result_level=level)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            text="📊 Пояснить результат",
            callback_data="explain_result"
        ),
        types.InlineKeyboardButton(
            text="🌙 Что можно улучшить",
            callback_data="improve_sleep"
        ),
        types.InlineKeyboardButton(
            text="📘 Читать канал",
            url=CHANNEL_URL
        )
    )

    await message.answer(
        f"🧠 *Результат теста*\n\n"
        f"{result}\n\n"
        "ℹ️ Это не диагноз, а ориентир.\n"
        "Выбери следующий шаг 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ======================
# EXPLAIN RESULT
# ======================
@dp.callback_query_handler(lambda c: c.data == "explain_result")
async def explain_result(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    level = data.get("result_level")

    explanations = {
        "green": (
            "🟢 Сон выглядит стабильным.\n\n"
            "Нервная система сохраняет способность "
            "к восстановлению и адаптации."
        ),
        "yellow": (
            "🟡 Возможна накопленная усталость.\n\n"
            "Часто связана с режимом, стрессом "
            "или вечерней стимуляцией."
        ),
        "orange": (
            "🟠 Сон может быть поверхностным или фрагментированным.\n\n"
            "Даже при достаточной длительности "
            "восстановление может быть неполным."
        ),
        "red": (
            "🔴 Сон, вероятно, не выполняет полноценную "
            "восстановительную функцию.\n\n"
            "Это может отражаться на самочувствии "
            "и концентрации."
        )
    }

    await callback.answer()
    await callback.message.answer(explanations.get(level, "Нет данных"))

# ======================
# IMPROVE SLEEP
# ======================
@dp.callback_query_handler(lambda c: c.data == "improve_sleep")
async def improve_sleep(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🌙 *Что можно улучшить уже сегодня:*\n\n"
        "• 🕰 стабильное время отхода ко сну\n"
        "• 📵 меньше стимулов за 60 минут до сна\n"
        "• ☀️ утренний свет и дневная активность\n\n"
        "Даже небольшие изменения\n"
        "могут улучшить качество сна.",
        parse_mode="Markdown"
    )

# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
