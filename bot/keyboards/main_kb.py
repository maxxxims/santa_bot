from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardMarkup
from collections import defaultdict
from bot.callbacks import JoinGroupCallback, CreateGroupCallback, CloseJoiningGroupCallback, FirstBtnCallback, SecondBtnCallback
import emoji
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton



def get_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":high_voltage:")+ " Давай!",
                                    callback_data=FirstBtnCallback().pack())
            ]
        ]
)
    
def get_joining_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":check_mark_button:")+ " Присоединиться к группе",
                                    callback_data=JoinGroupCallback().pack())
            ],
            [
                InlineKeyboardButton(text=emoji.emojize(":hammer_and_wrench:")+ " Создать группу",
                                    callback_data=CreateGroupCallback().pack())
            ]
        ]
)
    

def get_second_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
           [ InlineKeyboardButton(text=emoji.emojize(":sparkles:")+ " Супер!",
                                 callback_data=SecondBtnCallback().pack()
                                 )]
        ]
    )

    
#CloseJoinGroupKeyboard
def get_close_joining_kb() -> InlineKeyboardMarkup:


    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":left_arrow:")+ "Назад",
                                    callback_data=CloseJoiningGroupCallback().pack())
            ]
        ]
    )