import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_CONFIG
from handlers.start import start_router
from handlers.payments import payments_router
from handlers.notifications import setup_scheduler
from handlers.admin import admin_router
# from handlers.access import access_router
from database import init_db, init_access_keys_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/second_vpn.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="extend", description="Продлить подписку"),
        BotCommand(command="support", description="Поддержка"),
        
    ]
    await bot.set_my_commands(commands)

async def main():
    init_db()  # Инициализация базы данных
    init_access_keys_table()
    bot = Bot(token=BOT_CONFIG["token"])
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(payments_router)
    dp.include_router(admin_router)
    # dp.include_router(access_router)с

    await set_bot_commands(bot)
    setup_scheduler(bot)

    logger.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
