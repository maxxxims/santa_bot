from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
import logging
from aiogram.fsm.context import FSMContext
from uuid import UUID, uuid4
import asyncio

from bot.fsm import JoiningGroupState, SetWighListState
from bot.crud import users, groups, user2group
from bot.keyboards import messages, accept_kb, get_payment_kb
from bot.callbacks import menu_cb, main_cb
from bot.middlewares.base import RegisterUserMiddleware, CheckUserGroupMiddleware
from bot.config import MAX_BASE_USER_MEMBERS, SUB_PRICE_RUB, TERMINAL_KEY, TERMINAL_PWD, PAYED_GROUPS
from bot.utils import logic, payment

router = Router()
router.message.middleware(CheckUserGroupMiddleware()) 
router.callback_query.middleware(CheckUserGroupMiddleware()) 


# Купить подписку на группу
@router.callback_query(menu_cb.ExtendGroupCallback.filter(), StateFilter(None))
async def buy_subscription(query: CallbackQuery, user_info: dict, state: FSMContext):
    await query.answer()
    current_group_id = user_info.get("current_group_id", None)
    user_id = query.from_user.id
    
    if current_group_id is None:
        await query.message.delete()
        return
    
    order_id = str(uuid4())
    
    group = await groups.get(group_id=current_group_id)
    if group.is_extended:
        await query.message.answer("Подписка уже активна!")
        await query.message.delete()
        return
    
    username = query.from_user.username
    group_name = group.name
    
    payment_url, payment_id = await payment.initialize_payment(order_id=order_id, SUB_PRICE_RUB=SUB_PRICE_RUB, username=username, group_name=group_name)
    
    if payment_url is None:
        await query.message.answer("Произошла ошибка. Попробуйте позже")
        return
    
    await query.message.answer(messages.EXTEND_GROUP_MSG.format(group_name=group_name),
                               reply_markup=get_payment_kb(payment_url, payment_id),
                               parse_mode="Markdown"
                               )
    
    await asyncio.sleep(5 * 60)
    group = await groups.get(group_id=current_group_id)
    
    if not group.is_extended:
        status = await payment.check_payment(payment_id=payment_id, SUB_PRICE_RUB=SUB_PRICE_RUB)
        if status == True:
            await logic.extend_group(group_id=current_group_id)
            PAYED_GROUPS.add(current_group_id)
            await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message)
            await query.message.answer(f"Оплата прошла успешна в группе {group_name}!")
            return
    
    
# проверить подписку
@router.callback_query(menu_cb.RefreshPaymentCallback.filter(), StateFilter(None))
async def check_payment(query: CallbackQuery, user_info: dict, state: FSMContext, callback_data: menu_cb.RefreshPaymentCallback):
    await query.answer()
    current_group_id = user_info.get("current_group_id", None)
    user_id = query.from_user.id
    
    if current_group_id is None:
        await query.message.delete()
        return
    
    
    # logging.info(f"payment_id = {callback_data.payment_id}")
    status = await payment.check_payment(payment_id=callback_data.payment_id, SUB_PRICE_RUB=SUB_PRICE_RUB)
    # logging.info(f"=== status = {status}")
    
    if status == True:
        await logic.extend_group(group_id=current_group_id)
        await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message)
        # await query.message.delete()
        PAYED_GROUPS.add(current_group_id)
        await query.message.answer("Оплата прошла успешна!")
        return
    else:
        await query.message.answer("Оплата не прошла, попробуйте позже")
