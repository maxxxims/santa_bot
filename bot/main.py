import asyncio
import logging
import sys

# НАСТРАИВАЕМ КОРНЕВОЙ ЛОГГЕР ДЛЯ ВСЕГО ПРИЛОЖЕНИЯ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Логи в stdout (для Docker)
        # logging.FileHandler('bot.log')  # Дополнительно в файл (опционально)
    ]
)

# ЗАСТАВЛЯЕМ AIOGRAM ЛОГИРОВАТЬ ВСЁ
logging.getLogger('aiogram').setLevel(logging.INFO)
logging.getLogger('aiogram.event').setLevel(logging.INFO)
logging.getLogger('aiogram.dispatcher').setLevel(logging.DEBUG)  # Для дебага обработчиков

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

from bot.utils.utils import get_logger
from bot.handlers import start, group_joining, group_menu, chatting, group_payment
from bot.redis.manager import redis_manager
from bot.db import init_db, drop_db
from bot.utils import access


logger = get_logger(__name__)
load_dotenv()


def get_bot_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Вступить или создать группу"),
        types.BotCommand(command="/menu", description="Меню группы")
    ]
    return bot_commands

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Инициализация бота и диспетчера
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем роутеры
    dp.include_routers(start.router, group_joining.router, group_menu.router, chatting.router, group_payment.router)

    logging.info("Database connected")
    logging.info("🔄 Connecting to Redis...")
    # Инициализация базы данных
    # await drop_db()
    await init_db()
    await redis_manager.connect()
    # await redis_manager.flush_all()
    await access.update_white_list_file()
    
    
    
    await bot.set_my_commands(commands=get_bot_commands())
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()
        # await drop_db()
        # await redis_manager.flush_all()
        await redis_manager.disconnect()
        

if __name__ == "__main__":
    asyncio.run(main())