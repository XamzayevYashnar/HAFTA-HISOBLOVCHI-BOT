from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.types import FSInputFile
from database import Database
from default_papka.default import menu_button
from state import StateClas
from aiogram.fsm.context import FSMContext
from datetime import datetime
from calendar import monthrange
import matplotlib.pyplot as plt
import asyncio

API_TOKEN_BOT = "8223968206:AAEDgtzMWRwTKyWNnZWCoRgK2Gxqj-zaLoQ"
bot = Bot(token=API_TOKEN_BOT)
dp = Dispatcher()
db = Database()


async def main():
    db.create_table()
    print("Bot ishga tushdi 🤖 ...")
    await dp.start_polling(bot)


def generate_life_calendar(birth_date: datetime):
    today = datetime.today()
    delta = today - birth_date
    weeks_passed = delta.days // 7

    total_years = 90
    weeks_per_year = 52
    total_weeks = total_years * weeks_per_year

    fig, ax = plt.subplots(figsize=(12, 18))
    ax.set_title("90 лет твоей жизни в неделях", fontsize=16, color="blue")
    ax.set_xlabel("Номер недели")
    ax.set_ylabel("Возраст")

    for i in range(total_years):
        for j in range(weeks_per_year):
            index = i * weeks_per_year + j
            color = "red" if index < weeks_passed else "white"
            ax.add_patch(plt.Rectangle((j, total_years - i), 1, 1,
                                       edgecolor="black", facecolor=color))

    ax.set_xlim(0, weeks_per_year)
    ax.set_ylim(0, total_years)
    ax.set_xticks(range(0, weeks_per_year + 1, 5))
    ax.set_yticks(range(0, total_years + 1, 5))
    ax.invert_yaxis()
    plt.tight_layout()

    file_path = "life.png"
    plt.savefig(file_path, dpi=300)
    plt.close()
    return file_path


@dp.message(F.text == "/start")
async def hello(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    username = msg.from_user.username or "NoUsername" 
    user = db.get_user(user_id)
    if user:
        await msg.answer(
            """Привет!
Пришли мне дату своего рождения и я покажу сколько недель прошло с твоего рождения!
Отправь мне дату рождения в формате дд.мм.гггг или дд/мм/гггг (например, 01.01.2000).""",
            reply_markup=menu_button(user[3])
        )
        await state.set_state(StateClas.birth_data)
    else:
        db.add_user(user_id, username)
        user = db.get_user(user_id)
        if user:
            await msg.answer(
                """Привет!
Пришли мне дату своего рождения и я покажу сколько недель прошло с твоего рождения!
Отправь мне дату рождения в формате дд.мм.гггг или дд/мм/гггг (например, 01.01.2000).""",
                reply_markup=menu_button(user[3])
            )
            await state.set_state(StateClas.birth_data)
        else:
            await msg.answer("Xato")


@dp.message(StateClas.birth_data)
async def week_counter(msg: types.Message, state: FSMContext):
    text = msg.text.strip()

    birth_date = None
    for fmt in ("%d.%m.%Y", "%d/%m/%Y"):
        try:
            birth_date = datetime.strptime(text, fmt)
            break
        except ValueError:
            continue

    if not birth_date:
        await msg.answer("❌ Неверный формат даты! Попробуй ещё раз.")
        return

    today = datetime.today()

    years = today.year - birth_date.year
    months = today.month - birth_date.month
    days = today.day - birth_date.day

    if days < 0:
        if today.month == 1:
            prev_month_days = monthrange(today.year - 1, 12)[1]  
        else:
            prev_month_days = monthrange(today.year, today.month - 1)[1]
        days += prev_month_days
        months -= 1

    if months < 0:
        years -= 1
        months += 12

    total_months = years * 12 + months

    delta = today - birth_date
    weeks = delta.days // 7
    total_days = delta.days

    await msg.answer(
        f"📅 Ты родился: {birth_date.strftime('%d.%m.%Y')}\n\n"
        f"⌛ С твоего рождения прошло:\n"
        f"• {years} лет\n"
        f"• {total_months} месяцев\n"
        f"• {weeks} недель\n"
        f"• {total_days} дней"
    )

    file_path = generate_life_calendar(birth_date)
    photo = FSInputFile(file_path)  
    await msg.answer_photo(photo)

    await state.clear()


if __name__ == '__main__':
    asyncio.run(main())