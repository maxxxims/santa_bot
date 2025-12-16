from functools import wraps
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from copy import deepcopy

from bot.redis.manager import redis_manager
from bot.crud import users, user2group


class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        logging.info(f"=== Middleware called from {event.from_user.id}")
        user_id = event.from_user.id
        redis_key = f"user_{user_id}"
        user_info = await redis_manager.get_key(redis_key)
        if user_info is None:
            logging.info(f"No cahce info from {event.from_user}")
            is_register = await users.is_exist(user_id)
            logging.info(f"=== Info from db {event.from_user.id} is_register = {is_register}")
            if not is_register:
                await users.add(user_id=user_id, username=event.from_user.username, full_name=event.from_user.full_name)
                user_info = {}
                await redis_manager.set_key(redis_key, user_info)
            user_info = {}
        else:
            logging.info(f"=== Has cache info from {event.from_user}")
        
        user_info_old = user_info.copy()
        data['user_info'] = user_info
        try:
            await handler(event, data)
            if user_info_old != data['user_info']:
                await redis_manager.set_key(redis_key, data['user_info'])
                logging.info(f"=== Find diff")
                return
            logging.info(f"=== Diff not found!")
        except Exception as e:
            logging.error(f"=== Error in middleware \n{e}")
            return 
        
        
        
class CheckUserGroupMiddleware(BaseMiddleware):
    """
        Гарантирует регистрацию пользователя и существования поля group_id в user_info
    """
    async def __call__(
        self,
        handler: Callable,
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        logging.info(f"=== Middleware CheckUserGroupMiddleware called from {event.from_user.id}")
        user_id = event.from_user.id
        redis_key = f"user_{user_id}"
        user_info = await redis_manager.get_key(redis_key)
        if user_info is None:
            if not await users.is_exist(user_id):
                await users.add(user_id=user_id, username=event.from_user.username, full_name=event.from_user.full_name)
                user_info = {"groups": []}
            else:
                user_info = {}
        if 'groups' not in user_info:
            user_groups = await user2group.get_user_groups(user_id=user_id)
            user_info['groups'] = user_groups
        elif 'current_group_id' in user_info:
            if user_info['current_group_id'] not in user_info['groups'].keys():
                logging.warning(f"=== WARNING OF EXTRA OPERATION User {user_id} has no access to group {user_info['current_group_id']}")
                user_groups = await user2group.get_user_groups(user_id=user_id)
                user_info['groups'] = user_groups
                
            if user_info['current_group_id'] not in user_info['groups'].keys():
                user_info['current_group_id'] = None
        
        user_info_old = deepcopy(user_info)
        data['user_info'] = user_info
        
        logging.info(f"\n\n{user_info}\n\n")
        
        try:
            await handler(event, data)
            needs_update = len(user_info['groups']) != len(user_info_old['groups']) or user_info_old != data['user_info']
            if needs_update:
                await redis_manager.set_key(redis_key, data['user_info'])
                logging.info(f"=== Find diff")
                return
            logging.info(f"=== Diff not found!")
        except Exception as e:
            logging.error(f"=== Error in middleware \n{e}\nreset user info")
            await redis_manager.delete_key(redis_key)
            state: FSMContext = data.get('state')
            if state is not None:
                await state.clear()
            return 