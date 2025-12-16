import json
import logging

from bot.redis import redis_manager
from bot.config import WHITE_LIST_PATH

def __load_white_list_file() -> dict:
    with open(WHITE_LIST_PATH, "r") as f:
        return json.load(f)


async def update_white_list_file() -> None:
    white_list = __load_white_list_file()
    logging.info(f"=== white_list = {white_list}")
    await redis_manager.set_key("white_list", white_list)
    
    
async def get_white_list() -> dict:
    return await redis_manager.get_key("white_list")


async def get_privileged_users() -> list:
    white_list = await redis_manager.get_key("white_list")
    return white_list.get("privileged_users", [])