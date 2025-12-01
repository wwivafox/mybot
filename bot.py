from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
from config import BOT_TOKEN
from handler import start, register
from utils.members import get_birthdays_today
from utils.chats import get_all_chat_ids
from apscheduler.schedulers.asyncio import AsyncIOScheduler


TEST_CHAT_ID = -4899703259

async def send_daily_birthdays(bot: Bot):
    chat_ids = get_all_chat_ids()
    for chat_id in chat_ids:
        today_birthdays = get_birthdays_today(chat_id)
        if today_birthdays:
            for m in today_birthdays:
                await bot.send_message(chat_id, f"🎉 Сегодня день рождения у {m['name']}! Давайте её поздравим!🌸")

async def send_christmas_message(bot: Bot, date_label: str):
    chat_ids = get_all_chat_ids()
    for chat_id in chat_ids:
        await bot.send_message(chat_id, f"🎄Сегодня {date_label}. Всех с Рождеством!🌟")

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(register.router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


    scheduler.add_job(send_daily_birthdays, "cron", hour=9, minute=0, args=[bot])


    scheduler.add_job(
        send_christmas_message,
        "cron",
        month=12,
        day=25,
        hour=9,
        minute=0,
        args=[bot, "25 декабря"]
    )

    scheduler.add_job(
        send_christmas_message,
        "cron",
        month=1,
        day=7,
        hour=9,
        minute=0,
        args=[bot, "7 января"]
    )

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
