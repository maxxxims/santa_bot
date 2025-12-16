from logging import Logger
from aiogram import Bot


def get_logger(name: str) -> Logger:
    return Logger(name)


async def delete_msg(bot: Bot, chat_id: int, message_id: int):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(e)