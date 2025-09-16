import os
from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.types import FSInputFile
from database import Database
from default_papka.default import menu_button
from state import StateClas
from aiogram.fsm.context import FSMContext
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import asyncio
from aiohttp import web  # 🔄 YANGI: HTTP server uchun

API_TOKEN_BOT = os.getenv("API_TOKEN")
if not API_TOKEN_BOT:
    raise ValueError("API_TOKEN environment variable not set!")

bot = Bot(token=API_TOKEN_BOT)
dp = Dispatcher()
db = Database()

# 🔄 YANGI: HTTP server (Render uchun port ochish)
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def start_web_app():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# 🔄 O'ZGARTIRILGAN: main() ichida HTTP serverni ishga tushurish
async def main():
    db.create_table()
    print("Bot ishga tushdi 🤖 ...")
    await start_web_app()  # <-- YANGI
    await dp.start_polling(bot)

def generate_life_calendar(birth_date: datetime):
    today = datetime.today()
    days_passed = (today - birth_date).days
    weeks_passed = days_passed // 7
    total_years = 90
    weeks_per_year = 52
    total_weeks = total_years * weeks_per_year

    fig, ax = plt.subplots(figsize=(weeks_per_year/4, total_years/4))
    ax.set_title("90 лет твоей жизни в неделях", fontsize=16, pad=20)
    ax.set_xlabel("Недели года")
    ax.set_ylabel("Годы")

    for year in range(total_years):
        for week in range(weeks_per_year):
            week_index = year * weeks_per_year + week
            color = 'red' if week_index < weeks_passed else 'white'
            rect = patches.Rectangle(
                (week, year), 1, 1,
                linewidth=0.5, edgecolor='gray', facecolor=color,
                alpha=0.7 if color == 'red' else 1.0
            )
            ax.add_patch(rect)

    ax.set_xlim(0, weeks_per_year)
    ax.set_ylim(0, total_years)
    ax.set_xticks(range(0, weeks_per_year + 1, 5))
    ax.set_yticks(range(0, total_years + 1, 5))
    ax.invert_yaxis()
    plt.tight_layout()

    file_path = "life.png"
    plt.savefig(file_path, dpi=100, bbox_inches='tight')
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
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1

    months = today.month - birth_date.month
    if today.day < birth_date.day:
        months -= 1
    if months < 0:
        months += 12

    total_months = age * 12 + months
    delta = today - birth_date
    weeks = delta.days // 7
    total_days = delta.days

    await msg.answer(
        f"📅 Ты родился: {birth_date.strftime('%d.%m.%Y')}\n\n"
        f"⌛ С твоего рождения прошло:\n"
        f"• {age} лет\n"
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
