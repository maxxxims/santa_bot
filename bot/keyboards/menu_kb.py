from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardMarkup
from collections import defaultdict
from bot.callbacks import menu_cb, main_cb
import emoji
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton


def get_choose_group_menu(groups_info: dict, page_size: int, current_page: int = 0) -> InlineKeyboardMarkup:
    groups_ids_sorted = sorted(list(groups_info.keys()))
    
    page_groups = groups_ids_sorted[current_page * page_size : (current_page + 1) * page_size]
    
    inline_keyboard = []
    
    for group_id in page_groups:
        inline_keyboard.append([
        InlineKeyboardButton(text=groups_info[group_id],
            callback_data=main_cb.ChooseGroupCallback(group_id=group_id).pack())
        ])
    
    navigation_btns = []
    
    if current_page >= 0:
        navigation_btns.append(
            InlineKeyboardButton(text="⬅️ Назад",
                callback_data=menu_cb.NavigationGroupCallback(next_page=current_page - 1).pack())
        )
        
    next_batch = groups_ids_sorted[(current_page + 1) * page_size : (current_page + 2) * page_size]
    if len(next_batch) > 0:
        navigation_btns.append(
            InlineKeyboardButton(text="➡️ Вперед",
                callback_data=menu_cb.NavigationGroupCallback(next_page=current_page + 1).pack())
        )
    
    if len(navigation_btns) > 0:
        inline_keyboard.append(navigation_btns)
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    
    # local_cnt = 0
    # inline_keyboard = []
    # for group_id, group_name in groups_info.items():
    #     if local_cnt >= max_len:
    #         break
    #     inline_keyboard.append([
    #         InlineKeyboardButton(text=group_name,
    #             callback_data=main_cb.ChooseGroupCallback(group_id=group_id).pack())
    #     ])
    #     local_cnt += 1
    # return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def __get_buttons():
    return {
        'link':  InlineKeyboardButton(text=emoji.emojize(":link:")+ " Пригласить",
                                    callback_data=menu_cb.InviteCallback().pack()),
        'pair': InlineKeyboardButton(text=emoji.emojize(":bust_in_silhouette:")+ "Подопечный",
                                    callback_data=menu_cb.GetPairCallback().pack()),
        
        'exit':  InlineKeyboardButton(text=emoji.emojize(":cross_mark:")+ " Покинуть группу",
                                    callback_data=menu_cb.ExitGroupCallback_1().pack()),
        
        'shuffle':  InlineKeyboardButton(text=emoji.emojize(":recycling_symbol:")+ " Распределить",
                                    callback_data=menu_cb.ShuffleCallback_1().pack()),
        
        'close_event': InlineKeyboardButton(text=emoji.emojize(":stop_sign:")+ " Закончить ивент",
                                    callback_data=menu_cb.CloseEventCallback_1().pack()),
        
        'close_group': InlineKeyboardButton(text=emoji.emojize(":cross_mark:")+ " Покинуть группу",
                                    callback_data=menu_cb.ExitGroupCallback_1().pack()),
        
        'set_wishlist': InlineKeyboardButton(text=emoji.emojize(":wrapped_gift:")+ " Пожелания",
                                    callback_data=menu_cb.SetWishlistCallback().pack()),
        
        'back': InlineKeyboardButton(text=emoji.emojize(":left_arrow:")+ " Назад",
                                    callback_data=menu_cb.BackButtonCallback().pack()),
        
        'msg_santa': InlineKeyboardButton(text=emoji.emojize(":love_letter:")+ " Письмо Санте",
                                    callback_data=menu_cb.MsgCallback(send_to_santa=True).pack()),
        
        'msg_pair': InlineKeyboardButton(text=emoji.emojize(":love_letter:")+ " Письмо подопечному",
                                    callback_data=menu_cb.MsgCallback(send_to_santa=False).pack()),
        
        'extend_btn': InlineKeyboardButton(text=emoji.emojize(":money_bag:")+ " Расширить группу",
                                    callback_data=menu_cb.ExtendGroupCallback(send_to_santa=False).pack()),
        'members': InlineKeyboardButton(text="👥 Участники",
                                    callback_data=menu_cb.GetMembersCallback().pack()),
    }


def get_user_menu(is_extended: bool = True) -> InlineKeyboardMarkup:
    buttons = __get_buttons()
    inline_keyboard = [
            [
                buttons['link'], buttons['set_wishlist'],
            ],
            [
                buttons['members'],
            ],
            [
                buttons['msg_santa']
            ],
            [
                buttons['msg_pair'],
            ],
            
    ]
    
    if not is_extended:
        inline_keyboard.append([buttons['extend_btn'], buttons['pair']])
    else:
        inline_keyboard.append([buttons['pair']])
    
    inline_keyboard += [
            [
                buttons['close_group'], buttons['back']
            ],
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    


def get_admin_menu(is_extended: bool = True) -> InlineKeyboardMarkup:
    buttons = __get_buttons()
    
    inline_keyboard = [
            [
                buttons['link'], buttons['set_wishlist'],
            ],
            [
                buttons['shuffle'], buttons['pair'], 
            ],
            [
                buttons['members'],
            ],
            [
                buttons['msg_santa']
            ],
            [
                buttons['msg_pair'],
            ],
            
    ]
    
    if not is_extended:
        inline_keyboard.append([buttons['extend_btn']])
    
    inline_keyboard += [
            [
                buttons['close_group'], buttons['back']
            ],
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



def get_payment_kb(url: str, payment_id: str) -> InlineKeyboardMarkup:
    # btns = __get_buttons()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌟 Волшебный тариф 💸 490₽",
                                    url=url)
            ],
            [
                InlineKeyboardButton(text=emoji.emojize(":counterclockwise_arrows_button:")+ " Обновить",
                                    callback_data=menu_cb.RefreshPaymentCallback(payment_id=payment_id).pack())
            ]
        ]
    )
    ...