from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
import logging
from bot.utils import logic
from typing import Dict
from aiogram.fsm.context import FSMContext
from uuid import UUID

from bot.fsm import JoiningGroupState, CreatingGroupState
from bot.redis import redis_manager
from bot.crud import users, groups, user2group
from bot.keyboards import messages, get_close_joining_kb, get_start_kb, get_joining_kb
from bot.callbacks import CreateGroupCallback, JoinGroupCallback, CloseJoiningGroupCallback
from bot.middlewares.base import CheckUserGroupMiddleware
from bot.config import MAX_BASE_USER_MEMBERS
from bot.utils import access


router = Router()
router.message.middleware(CheckUserGroupMiddleware()) 
router.callback_query.middleware(CheckUserGroupMiddleware()) 


# Создание группы
@router.callback_query(CreateGroupCallback.filter(), StateFilter(None))
async def make_group(query: CallbackQuery, user_info: dict, state: FSMContext):
    await query.answer()
    user_groups = user_info['groups']
    if len(user_groups) > 30:
        await query.message.answer(messages.TOO_MUCH_GROUPS)
        return
    
    await query.bot.send_photo(
        chat_id=query.from_user.id,
        photo=messages.IMG_ID_3,
        caption=messages.CREATE_GROUP_MGS_NAME,
    )
    
    await state.set_state(CreatingGroupState.writing_name)
    await query.message.delete()
    

@router.message(StateFilter(CreatingGroupState.writing_name))
async def write_group_name(message: Message, user_info: dict, state: FSMContext):
    group_name = message.text
    if len(group_name) > 40 or group_name.startswith("/"):
        await message.answer("Некорректное название группы")
        return
    await state.set_data({"group_name": group_name})
    await message.answer(messages.CREATE_GROUP_MGS_DESC)
    await state.set_state(CreatingGroupState.writing_description)
    

@router.message(StateFilter(CreatingGroupState.writing_description))
async def write_group_descr(message: Message, user_info: dict, state: FSMContext):
    # await query.answer()
    logging.info(f"=== user_info before = {user_info}")
    group_description = message.text
    if len(group_description) > 200 or group_description.startswith("/"):
        await message.answer("Некорректное описание группы")
        return
    
    user_id = message.from_user.id
    
    group_name = (await state.get_data())["group_name"]
    white_list = await access.get_privileged_users()
    username = message.from_user.username
    is_extended = False
    
    if username in white_list:
        is_extended = True
        
    group_id, link = await logic.register_group(user_id=user_id, user_info=user_info, group_name=group_name, group_description=group_description, is_extended=is_extended)
    logging.info(f"=== group_id = {group_id}; type(group_id) = {type(group_id)}")
    logging.info(f"=== user_info after = {user_info}")
    
    await message.answer(messages.CREATE_GROUP_MSG.format(link=link, group_name=group_name), parse_mode="Markdown")
    await state.clear()


# Вступление в группу
@router.callback_query(JoinGroupCallback.filter(), StateFilter(None))
async def join_group(query: CallbackQuery, user_info: dict, state: FSMContext):
    await query.answer()
    
    user_groups = user_info["groups"]
    if len(user_groups) > 30:
        await query.message.answer(messages.TOO_MUCH_GROUPS)
        await query.message.delete()
        return
        
    await state.set_state(JoiningGroupState.writing_code)
    await query.message.answer(f"Введите код группы:", reply_markup=get_close_joining_kb())
    await query.message.delete()
    

@router.callback_query(CloseJoiningGroupCallback.filter())
async def close_join(query: CallbackQuery, user_info: dict, state: FSMContext):
    await query.answer()
    if await state.get_state() == JoiningGroupState.writing_code:
        await query.message.answer(
            messages.THIRD_MSG,
            reply_markup=get_joining_kb()
        )
    await state.clear()
    await query.message.delete()


@router.message(StateFilter(JoiningGroupState.writing_code))
async def check_invite_link(message: Message, user_info: dict, state: FSMContext) -> dict:
    user_id = message.from_user.id
    user_groups = user_info["groups"]
    
    if len(user_groups) > 30:
        await message.answer(messages.TOO_MUCH_GROUPS)
        await state.clear()
        return
    
    if len(message.text.split()) > 1:
        await message.answer(messages.INCORRECT_INVITE_LINK, reply_markup=get_close_joining_kb())
        return
    
    invite_link = message.text  
    try:
        invite_link = UUID(invite_link)
    except:
        await message.answer(messages.INCORRECT_INVITE_LINK, reply_markup=get_close_joining_kb())
        return
    
    group = await groups.get_by_link(invite_link=invite_link)
    if group is None:
        await message.answer(messages.INCORRECT_INVITE_LINK, reply_markup=get_close_joining_kb())
        return
    
    if group.group_id in user_groups.keys():
        await message.answer(messages.ALREADY_IN_GROUP, reply_markup=get_close_joining_kb())
        return
    
    if group.is_active == False or group.is_shuffled == True:
        await message.answer(messages.GROUP_IS_NOT_ACTIVE)
        await state.clear()
        return

    if len(group.participants) + 1 > MAX_BASE_USER_MEMBERS and not group.is_extended:
        await message.answer(messages.GROUP_IS_FULL)
        await state.clear()
        return
    
    await logic.join_group(user_id=user_id, group_id=group.group_id, user_info=user_info, group_name=group.name)
    
    # if not group.is_extended:
    #     white_list = await access.get_privileged_users()
    #     if message.from_user.username in white_list:
    #         await logic.extend_group(group_id=group.group_id)
    
    await message.answer(messages.USER_JOIN_GROUP.format(group_name=group.name))
    await state.clear()
    