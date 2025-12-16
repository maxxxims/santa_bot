from typing import Dict, Tuple, Union
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ParseMode
from asyncio import sleep
import random
import logging

from bot.models import Group, User, UserGroup, SantaPair
from bot.keyboards import messages, get_admin_menu, get_user_menu
from bot.db import async_session
from bot.crud import groups, user2group, santapair
from bot.redis import redis_manager


async def register_group(user_info: dict, user_id: int, group_name: str, group_description: str, is_extended: bool = False) -> int:
    group_id, link = await groups.add(user_id, group_name=group_name, group_description=group_description, is_extended=is_extended)
    link = str(link)
    await user2group.add(user_id=user_id, group_id=group_id)
    user_info["groups"][group_id] = group_name
    return group_id, link


# async def get_group_id(user_id: int) -> Union[int, None]:
#     redis_key = f"user_{user_id}"
#     user_info = await redis_manager.get_key(redis_key, default={})
#     group_id = user_info.get("group_id")
#     if group_id is not None:
#         return group_id
#     group_id = await user2group.get_user_group(user_id=user_id)
#     if group_id is not None:
#         user_info["group_id"] = group_id
#         await redis_manager.set_key(redis_key, user_info)
#     return group_id




#### NEW FUNCTIONS

async def get_group_stats(group_id: int, user_id: int) -> Union[Dict, None]:
    async with async_session() as session:
        query = (
            select(Group)
            .options(selectinload(Group.participants))
            .where(Group.group_id == group_id)
        )
        result = await session.execute(query)
        group = result.scalar_one_or_none()
        
        
        if not group:
            return None
        
        
        result = (await session.execute(select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.group_id == group_id))).scalar_one()
        logging.info(f"===== user_id {user_id} is {type(result)}; {result.__dict__}; {result is None}")
        user_wighlist = result.wishlist
        
        logging.info(f"===== {user_wighlist}")
        # Подсчет участников
        user_count = len(group.participants)
        
        # Статусы
        is_active = group.is_active
        is_shuffled = group.is_shuffled
        admin_id = group.admin_id
        
        return {
            'user_count': user_count,
            'is_active': is_active,
            'is_shuffled': is_shuffled,
            'admin_id': admin_id,
            'group_name': group.name,
            'group_description': group.description,
            'user_wishlist': user_wighlist,
            'is_extended': group.is_extended
        }
        
    
async def join_group(user_info: dict, user_id: int, group_id: int, group_name: str) -> Union[int, None]:
    await user2group.add(user_id=int(user_id), group_id=int(group_id))
    user_info["groups"][group_id] = group_name
    
    
    
    
async def shuffle_group_members(group_id: int, admin_id: int, bot: Bot, inform_members: bool = True) -> bool:
    group = await groups.get(group_id=group_id)
    if group.is_shuffled is True:
        return False
    users = await user2group.get_group_members(group_id)
    if len(users) < 2:
        return False

    user_ids_list = [el.user_id for el in users]
    random.shuffle(user_ids_list)
    
    group_name = group.name
    
    pairs = []
    
    for i in range(len(user_ids_list) - 1):
        pairs.append(SantaPair(
            group_id=group_id,
            giver_id=user_ids_list[i],
            receiver_id=user_ids_list[i + 1],
        ))
    pairs.append(SantaPair(
        group_id=group_id,
        giver_id=user_ids_list[-1],
        receiver_id=user_ids_list[0],
    ))

    await santapair.add_pairs_orm_bulk(pairs)
    await groups.set_shuffle_status(group_id, True)
    
    await bot.send_message(admin_id, text=f"Ивент начался, пары установлены в группе *{group_name}*! Узнать твоего получателя можно в меню /menu", parse_mode="Markdown")
    
    if inform_members and bot is not None:
        for user in users:
            if user.user_id == admin_id:
                continue
            await bot.send_message(user.user_id, f"Ивент начался, пары установлены в группе *{group_name}*! Узнать твоего получателя можно в меню /menu", parse_mode="Markdown")
            await sleep(1)
            
    return True



async def get_pair(user_id: int, group_id: int) -> Union[None, User]:
    group = await groups.get(group_id=group_id)
    if group.is_shuffled is False:
        return None
    pair = await santapair.get_reciver_user(giver_id=user_id, group_id=group_id)
    return pair.receiver


async def try_to_exit_group(group_id: int, user_id: int, user_info: dict, bot: Bot) -> bool:
    user_group = await groups.get(group_id=group_id)
    
    is_shuffled = user_group.is_shuffled
    
    if is_shuffled:
        return False
    
    admin_id = user_group.admin_id
    
    if admin_id != user_id:
        await user2group.delete_users_from_group(user_ids=[user_id], group_id=group_id)
        del user_info["groups"][group_id]
        del user_info["current_group_id"]
    else:
        group_membres = await user2group.get_group_members(group_id=group_id)
        member_ids = [el.user_id for el in group_membres]
        
        await user2group.delete_users_from_group(user_ids=member_ids, group_id=group_id)
        await groups.remove(group_id=group_id)
        
        for member_id in member_ids:
            if member_id == user_id:
                continue
            redis_key = f"user_{member_id}"
            member_info = await redis_manager.get_key(redis_key, default={})
            del member_info['groups'][group_id]
            del member_info["current_group_id"]
            await redis_manager.set_key(redis_key, member_info)
            await bot.send_message(member_id, text="Ваша группа была распущена")
            await sleep(0.1)
            
        del user_info["groups"][group_id]
        del user_info["current_group_id"]
        
    return True


async def send_menu(group_id: int, user_id: int, message: Message):
    group_stats = await get_group_stats(group_id=group_id, user_id=user_id)
    if group_stats is None:
        logging.info(f"User {user_id} has group {group_id} but no stats!")
        return
    msg = messages.get_group_info_message(group_stats=group_stats, user_id=user_id)
    if user_id == group_stats['admin_id']:
        kb = get_admin_menu(is_extended=group_stats['is_extended'])
    else:
        kb = get_user_menu(is_extended=group_stats['is_extended'])
    await message.answer(msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
    await message.delete()
    
    
async def extend_group(group_id: int) -> None:
    await groups.extend(group_id=group_id, is_extended=True)