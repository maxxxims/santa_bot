from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardMarkup
from bot.callbacks import menu_cb, main_cb
import emoji
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton



def get_agree_shuffle_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":check_mark_button:")+ " Да",
                                    callback_data=menu_cb.ShuffleCallbackAccept().pack())
            ],
            [
                InlineKeyboardButton(text=emoji.emojize(":cross_mark:")+ " Нет",
                                    callback_data=menu_cb.ShuffleCallbackDecline().pack())
            ],
        ]
)
    
    
    
def get_agree_exit_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":check_mark_button:")+ " Да",
                                    callback_data=menu_cb.ExitGroupCallbackAccept().pack())
            ],
            [
                InlineKeyboardButton(text=emoji.emojize(":cross_mark:")+ " Нет",
                                    callback_data=menu_cb.ExitGroupCallbackDecline().pack())
            ],
        ]
)
    
    
def get_agree_end_event_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":check_mark_button:")+ " Да",
                                    callback_data=menu_cb.CloseEventCallbackAccept().pack())
            ],
            [
                InlineKeyboardButton(text=emoji.emojize(":cross_mark:")+ " Нет",
                                    callback_data=menu_cb.CloseEventCallbackDecline().pack())
            ],
        ]
)
    
    
def main_exit_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=emoji.emojize(":left_arrow:")+ " Назад",
                                    callback_data=main_cb.MainExitCallback().pack())
            ]
        ]
    )