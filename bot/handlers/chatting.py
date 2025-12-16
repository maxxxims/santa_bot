from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
import logging
from bot.utils import logic
from typing import Dict, Union
from aiogram.fsm.context import FSMContext

from uuid import UUID

from bot.fsm import MsgSantaState, MsgPairState
from bot.crud import users, groups, santapair
from bot.keyboards import messages, accept_kb, main_exit_kb
from bot.callbacks import menu_cb, main_cb
from bot.middlewares.base import RegisterUserMiddleware, CheckUserGroupMiddleware
from bot.config import MAX_MSG_LIMIT_FREE, MAX_MSG_LIMIT_EXTENDED


router = Router()
router.message.middleware(CheckUserGroupMiddleware()) 
router.callback_query.middleware(CheckUserGroupMiddleware()) 



# Письмо санте
@router.callback_query(menu_cb.MsgCallback.filter(), StateFilter(None))
async def msg_santa(query: CallbackQuery, user_info: dict, state: FSMContext, callback_data: menu_cb.MsgCallback):
    await query.answer()
    user_groups = user_info["groups"]
    current_group_id = user_info.get("current_group_id", None)
    if len(user_groups) == 0 or current_group_id is None:
        await query.message.delete()
        return
    
    group = await groups.get(group_id=current_group_id)
    if group is None:
        await query.message.delete()
        return
    
    if group.is_shuffled is False:
        await query.message.answer(messages.EVENT_NOT_STARTED)
        return
    
    info = await santapair.get_by_user(user_id=query.from_user.id, group_id=current_group_id)
    
    msg_limit = MAX_MSG_LIMIT_EXTENDED if group.is_extended else MAX_MSG_LIMIT_FREE
    
    if info.msg_counter >= msg_limit:
        limit_msg = messages.MSG_LIMIT_REACHED_EXTENDED if group.is_extended else messages.MSG_LIMIT_REACHED
        await query.message.answer(limit_msg.format(limit=msg_limit))
        return
    
    if callback_data.send_to_santa:
        await state.set_state(MsgSantaState.writing_msg)
        await query.message.answer(messages.MSG_TO_SANTA.format(current=info.msg_counter, limit=msg_limit),
                                   reply_markup=main_exit_kb())
    else:
        await state.set_state(MsgPairState.writing_msg)
        await query.message.answer(messages.MSG_TO_PAIR.format(current=info.msg_counter, limit=msg_limit),
                                   reply_markup=main_exit_kb())
    await query.message.delete()
    

@router.message(StateFilter(MsgSantaState.writing_msg, MsgPairState.writing_msg))
async def msg_santa(message: Message, user_info: dict, state: FSMContext):
    user_groups = user_info["groups"]
    current_group_id = user_info.get("current_group_id", None)
    if len(user_groups) == 0 or current_group_id is None:
        await message.delete()
        return
    
    msg = message.text
    current_state = await state.get_state()
    
    if current_state == MsgSantaState.writing_msg:
        pair = await santapair.get_giver_user(receiver_id=message.from_user.id, group_id=current_group_id)
        if pair is None:
            return
        send_to = pair.giver_id
        await message.bot.send_message(chat_id=send_to, text=f"*Сообщение от подопечного:*\n\n{msg}", parse_mode="Markdown")
        
        
    elif current_state == MsgPairState.writing_msg:
        pair = await santapair.get_reciver_user(giver_id=message.from_user.id, group_id=current_group_id)
        if pair is None:
            return
        send_to = pair.receiver_id
        await message.bot.send_message(chat_id=send_to, text=f"*Сообщение от санты:*\n\n{msg}", parse_mode="Markdown")
        
    await state.clear()
    status = await santapair.increment_msg_counter(group_id=current_group_id, giver_id=message.from_user.id)
    if status:
        await message.answer("Сообщение отправлено!")