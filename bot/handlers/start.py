from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
import logging
from typing import Dict
from aiogram.fsm.context import FSMContext

from bot.utils import logic, access
from bot.crud import users, groups, user2group
from bot.keyboards import get_start_kb, messages, get_second_kb, get_joining_kb
from bot.callbacks import FirstBtnCallback, SecondBtnCallback
from bot.middlewares.base import RegisterUserMiddleware, CheckUserGroupMiddleware


router = Router()
router.message.middleware(RegisterUserMiddleware()) 
router.callback_query.middleware(RegisterUserMiddleware()) 



@router.message(CommandStart(), StateFilter(None))
async def cmd_start(message: Message, user_info: dict):
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=messages.IMG_ID_1,
        caption=messages.START_MSG,
        reply_markup=get_start_kb()
    )


# кнопка давай
@router.callback_query(FirstBtnCallback.filter(), StateFilter(None))
async def first_btn(query: CallbackQuery, user_info: dict):
    await query.answer()
    await query.message.bot.send_photo(
        chat_id=query.from_user.id,
        photo=messages.IMG_ID_2,
        caption=messages.SECOND_MSG,
        reply_markup=get_second_kb()
    )
    # await query.message.delete()
    
    
# кнопка супер
@router.callback_query(SecondBtnCallback.filter(), StateFilter(None))
async def second_btn(query: CallbackQuery, user_info: dict):
    await query.answer()
    await query.message.answer(
            messages.THIRD_MSG,
            reply_markup=get_joining_kb()
        )
    # await query.message.delete()
    
      
@router.message(Command("ideas"))
async def cmd_ideas(message: Message, user_info: dict):
    await message.answer(messages.IDEAS_MSG)
    
    
@router.message(Command("error"))
async def cmd_ideas(message: Message, user_info: dict):
    # await message.answer(messages.IDEAS_MSG)
    1 / 0
    
@router.message(Command("refresh"))
async def cmd_ideas(message: Message, user_info: dict):
    await access.update_white_list_file()
    
    
@router.message(Command("whitelist"))
async def cmd_ideas(message: Message, user_info: dict):
    white_list = await access.get_white_list()
    username = message.from_user.username
    if username in white_list["admin_names"]:
        await message.answer(f"{white_list}")

    
    

@router.message(F.photo)
async def handle_photo(message: Message):
    # Получаем file_id самого лучшего качества
    white_list = await access.get_white_list()
    username = message.from_user.username
    file_id = message.photo[-1].file_id
    if username in white_list["admin_names"]:
        await message.bot.send_photo(chat_id=message.chat.id, caption=f"{file_id}", photo=file_id)