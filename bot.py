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
        types.InlineKeyboardButton("🧠 Пройти тест сна", callback_data="start_test"),
        types.InlineKeyboardButton("📘 Перейти в канал", url=CHANNEL_URL),
    )

    await message.answer(
        "🌙 *Neuro Sleep Science*\n\n"
        "Этот тест помогает оценить\n"
        "*структуру и восстановительную функцию сна*.\n\n"
        "⚠️ Не является диагнозом.\n\n"
        "Начнём? 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ======================
# START TEST
# ======================
@dp.callback_query_handler(lambda c: c.data == "start_test")
async def start_test(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SleepTest.q1)
    await ask_q1(callback.message)


# ======================
# QUESTIONS
# ======================
async def ask_q1(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("😴 До 15 минут", callback_data="q1_0"),
        types.InlineKeyboardButton("🙂 15–30 минут", callback_data="q1_1"),
        types.InlineKeyboardButton("😕 30–60 минут", callback_data="q1_2"),
        types.InlineKeyboardButton("😣 Больше часа", callback_data="q1_3"),
    )
    await message.answer(
        "🕰 *Вопрос 1*\n\nСколько времени тебе обычно нужно, чтобы уснуть?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(lambda c: c.data.startswith("q1_"), state=SleepTest.q1)
async def q1(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(q1=int(callback.data.split("_")[1]))
    await state.set_state(SleepTest.q2)
    await ask_q2(callback.message)


async def ask_q2(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🌙 Не просыпаюсь", callback_data="q2_0"),
        types.InlineKeyboardButton("😴 1 раз", callback_data="q2_1"),
        types.InlineKeyboardButton("😕 2–3 раза", callback_data="q2_2"),
        types.InlineKeyboardButton("😣 4 и более", callback_data="q2_3"),
    )
    await message.answer(
        "🌙 *Вопрос 2*\n\nКак часто ты просыпаешься ночью?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(lambda c: c.data.startswith("q2_"), state=SleepTest.q2)
async def q2(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(q2=int(callback.data.split("_")[1]))
    await state.set_state(SleepTest.q3)
    await ask_q3(callback.message)


async def ask_q3(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("☀️ Отдохнувшим", callback_data="q3_0"),
        types.InlineKeyboardButton("🙂 Скорее нормально", callback_data="q3_1"),
        types.InlineKeyboardButton("😕 Уставшим", callback_data="q3_2"),
        types.InlineKeyboardButton("😣 Разбитым", callback_data="q3_3"),
    )
    await message.answer(
        "☀️ *Вопрос 3*\n\nКак ты обычно чувствуешь себя утром?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(lambda c: c.data.startswith("q3_"), state=SleepTest.q3)
async def q3(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(q3=int(callback.data.split("_")[1]))
    await state.set_state(SleepTest.q4)
    await ask_q4(callback.message)


async def ask_q4(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🕰 До 23:00", callback_data="q4_0"),
        types.InlineKeyboardButton("🌙 23:00–00:00", callback_data="q4_1"),
        types.InlineKeyboardButton("🌌 00:00–01:00", callback_data="q4_2"),
        types.InlineKeyboardButton("🌃 После 01:00", callback_data="q4_3"),
    )
    await message.answer(
        "🕰 *Вопрос 4*\n\nВо сколько ты обычно ложишься спать?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.callback_query_handler(lambda c: c.data.startswith("q4_"), state=SleepTest.q4)
async def q4(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(q4=int(callback.data.split("_")[1]))
    await state.set_state(SleepTest.q5)
    await ask_q5(callback.message)


async def ask_q5(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🙂 Почти никогда", callback_data="q5_0"),
        types.InlineKeyboardButton("😕 Иногда", callback_data="q5_1"),
        types.InlineKeyboardButton("😴 Часто", callback_data="q5_2"),
        types.InlineKeyboardButton("😣 Почти каждый день", callback_data="q5_3"),
    )
    await message.answer(
        "😴 *Вопрос 5*\n\nБывает ли у тебя дневная сонливость?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
@dp.callback_query_handler(lambda c: c.data == "finish_test", state="*")
async def finish_test(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    q1 = data.get("q1", 0)
    q2 = data.get("q2", 0)
    q3 = data.get("q3", 0)
    q4 = data.get("q4", 0)
    q5 = data.get("q5", 0)

    score = q1 + q2 + q3 + q4 + q5

    if score <= 4:
        result_text = (
            "🟢 *Физиологически сохранённый сон*\n\n"
            "Сон выполняет восстановительную функцию.\n"
            "Нервная система хорошо справляется с нагрузкой.\n\n"
            "Даже при стрессе сон остаётся опорным механизмом восстановления."
        )
    elif score <= 8:
        result_text = (
            "🟡 *Пограничное состояние сна*\n\n"
            "Сон в целом сохранён, но есть признаки перегрузки.\n\n"
            "Часто связано со стрессом, режимом или вечерней стимуляцией.\n"
            "На этом этапе мягкая коррекция даёт максимальный эффект."
        )
    elif score <= 12:
        result_text = (
            "🟠 *Выраженные функциональные нарушения сна*\n\n"
            "Сон не всегда выполняет восстановительную функцию.\n\n"
            "Возможны поверхностный сон, утренняя усталость,\n"
            "снижение концентрации днём."
        )
    else:
        result_text = (
            "🔴 *Высокий риск хронического нарушения сна*\n\n"
            "Сон, вероятно, не даёт полноценного восстановления.\n\n"
            "Это может отражаться на настроении, энергии и устойчивости к стрессу.\n"
            "Рекомендуется внимательное отношение к режиму сна."
        )

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🔍 Разбор параметров сна", callback_data="details_menu"),
        types.InlineKeyboardButton("🌙 Что можно улучшить", callback_data="improve_sleep"),
        types.InlineKeyboardButton("🔁 Повторить тест через 7 дней", callback_data="repeat_test")
    )

    await callback.message.answer(
        f"🧠 *Результат теста сна*\n\n"
        f"{result_text}\n\n"
        "ℹ️ Это не диагноз, а ориентир для понимания состояния сна.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await callback.answer()
    await state.finish()

# ======================
# FINISH TEST
# ======================

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📊 Пояснить результат", callback_data="explain_result"),
        types.InlineKeyboardButton("🌙 Что можно улучшить", callback_data="improve_sleep"),
        types.InlineKeyboardButton("📘 Читать канал", url=CHANNEL_URL),
    )

    await callback.message.answer(
        f"🧠 *Результат теста*\n\n{result}\n\n"
        "Это ориентир, а не диагноз.\n"
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
        "green": "🟢 Сон выглядит стабильным.\n\nНервная система сохраняет способность к восстановлению.",
        "yellow": "🟡 Возможна накопленная усталость.\n\nЧасто связана с режимом и стрессом.",
        "orange": "🟠 Сон может быть поверхностным.\n\nДаже при нормальной длительности восстановление снижено.",
        "red": "🔴 Сон, вероятно, не выполняет полноценную восстановительную функцию.",
    }

    await callback.answer()
    await callback.message.answer(
        explanations.get(level, "Нет данных"),
        parse_mode="Markdown"
    )


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
        "• ☀️ утренний свет и движение\n\n"
        "Даже небольшие изменения улучшают сон.",
        parse_mode="Markdown"
    )


# ======================
# RUN
# ======================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
