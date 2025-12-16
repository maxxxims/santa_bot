from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.enums import ParseMode
import logging
from bot.utils import logic
from typing import Dict
from aiogram.fsm.context import FSMContext

from uuid import UUID

from bot.fsm import JoiningGroupState, SetWighListState
from bot.crud import santapair, users, groups, user2group
from bot.keyboards import messages, accept_kb, get_admin_menu, get_user_menu, get_choose_group_menu, get_joining_kb
from bot.callbacks import menu_cb, main_cb
from bot.middlewares.base import RegisterUserMiddleware, CheckUserGroupMiddleware
from bot.config import MAX_BASE_USER_MEMBERS, MAX_GROUPS_PER_PAGE


router = Router()
router.message.middleware(CheckUserGroupMiddleware()) 
router.callback_query.middleware(CheckUserGroupMiddleware()) 



# Меню и выбор групп
@router.message(Command("menu"), StateFilter(None))
async def cmd_info(message: Message, user_info: dict):
    user_id = message.from_user.id 
    user_groups = user_info["groups"]
    if len(user_groups) == 0:
        await message.answer(
            messages.THIRD_MSG,
            reply_markup=get_joining_kb()
        )
        return
    await message.answer("Выбери группу:", reply_markup=get_choose_group_menu(user_groups, page_size=MAX_GROUPS_PER_PAGE, current_page=0))
    

@router.callback_query(menu_cb.NavigationGroupCallback.filter(), StateFilter(None))
async def menu_next_button(query: CallbackQuery, user_info: dict, callback_data: menu_cb.NavigationGroupCallback):
    await query.answer()
    user_groups = user_info["groups"]
    if len(user_groups) == 0 or callback_data.next_page < -1:
        return
    
    if callback_data.next_page == -1:
        await query.message.answer(
            messages.THIRD_MSG,
            reply_markup=get_joining_kb()
        )
        await query.message.delete()
        return
    
    await query.message.answer("Выберите группу:",
        reply_markup=get_choose_group_menu(user_groups, page_size=MAX_GROUPS_PER_PAGE, current_page=callback_data.next_page))
    await query.message.delete()

# Основное меню выбранной группы
@router.callback_query(main_cb.ChooseGroupCallback.filter(), StateFilter(None))
async def select_group(query: CallbackQuery, user_info: dict, callback_data: main_cb.ChooseGroupCallback):  
    await query.answer()
    logging.info(f"*************** User {query.from_user.id} selected group {callback_data.group_id}")  
    group_id = callback_data.group_id
    user_id = query.from_user.id
    user_groups = user_info["groups"]
    if group_id not in user_groups.keys():
        logging.info(f"User {query.from_user.id} has no access to group {group_id}")
        return
    user_info["current_group_id"] = group_id
    await logic.send_menu(group_id=group_id, user_id=user_id, message=query.message)


# Вернуться в меню выбора
@router.callback_query(menu_cb.BackButtonCallback.filter(), StateFilter(None))
async def menu_back_button(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_groups = user_info["groups"]
    if len(user_groups) == 0:
        return
    await query.message.answer("Выберите группу:", reply_markup=get_choose_group_menu(user_groups, page_size=MAX_GROUPS_PER_PAGE, current_page=0))
    await query.message.delete()
      
    
# Приглашение в группу 
@router.callback_query(menu_cb.InviteCallback.filter(), StateFilter(None))
async def cmd_invite(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    
    # отправляем информацию с ссылкой если юзер в группе
    # если юзер не в группе, отправляем ошибку
    if current_group_id is None:
        await query.message.delete()
        return 
    # юзер в группе, отправляем ссылку
    else:
        group = await groups.get(group_id=current_group_id)
        if len(group.participants) + 1 > MAX_BASE_USER_MEMBERS and not group.is_extended:
            await query.message.answer(f"Лимит в {MAX_BASE_USER_MEMBERS} человек исчерпан! Необходимо расширить группу через /menu")
            return 
        
        invite_link = str(group.invite_link)
        await query.message.answer(messages.INVITE_LINK_MSG.format(code=invite_link), parse_mode="Markdown")
        return
    
    
    
# Распределение в группе 
@router.callback_query(menu_cb.ShuffleCallback_1.filter(), StateFilter(None))
async def cmd_shuffle(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    
    await query.message.answer("Вы действительно хотите перемешать группу и распределить тайных сант?", reply_markup=accept_kb.get_agree_shuffle_kb())
    await query.message.delete()
    
    
@router.callback_query(menu_cb.ShuffleCallbackDecline.filter(), StateFilter(None))
async def shuffle_decline(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    
    # Отправляем обратно в меню
    
    await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message)
    # await query.message.delete()
    

@router.callback_query(menu_cb.ShuffleCallbackAccept.filter(), StateFilter(None))
async def shuffle_accept(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    # ДОБАВИТЬ ПРОВЕРКУ НА АДМИНА
    status = await logic.shuffle_group_members(group_id=current_group_id, admin_id=user_id, inform_members=True, bot=query.bot)
    if not status:
        await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message)
        await query.message.answer("В вашей группе 1 человек или ивент уже начался!")
    await query.message.delete()
    
#Узнать подопечного
@router.callback_query(menu_cb.GetPairCallback.filter(), StateFilter(None))
async def get_pair(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    
    group_name = user_info["groups"].get(current_group_id, None)

    receiver = await logic.get_pair(user_id=user_id, group_id=current_group_id)

    if receiver is None:
        await query.message.answer("Ивент ещё не начался, группа не перемешана!")
    else:
        reciver_wishlist = await user2group.get_wishlist(user_id=receiver.user_id, group_id=current_group_id)
    
        msg_text = ''
        
        if group_name is not None:
            msg_text += f'Группа: <b>{group_name}</b>\n'
        
        msg_text += f'Твой подопечный <a href="tg://user?id={receiver.user_id}">@{receiver.username}</a>'
        if reciver_wishlist is not None:
            msg_text += f'\nЕго пожелания: {reciver_wishlist}'
        else:
            msg_text += '\nОн пока не указал свои пожелания‼️\nТы можешь написать подопечному анонимное сообщение и помочь ему с идеями или просто передать тёплые слова 💌'
            
        await query.message.answer(
            msg_text, parse_mode="HTML"
        )
        # await query.message.delete()
    
    

# Покинуть группу
@router.callback_query(menu_cb.ExitGroupCallback_1.filter(), StateFilter(None))
async def exit_group(query: CallbackQuery, user_info: dict):
    await query.answer()
    
    current_group_id = user_info.get("current_group_id", None)
    if current_group_id is None:
        await query.message.delete()
        return
    
    group = await groups.get(group_id=current_group_id)
    if group is None:
        await query.message.delete()
        return
    
    is_shuffled = group.is_shuffled
    
    if is_shuffled:
        await query.message.answer("Ивент уже начался, нельзя покинуть группу")
        return
    
    await query.message.answer("Вы действительно хотите покинуть группу?", reply_markup=accept_kb.get_agree_exit_kb())
    await query.message.delete()
    
    
@router.callback_query(menu_cb.ExitGroupCallbackDecline.filter(), StateFilter(None))
async def exit_group_decline(query: CallbackQuery, user_info: dict):
    await query.answer()
    
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return

    # Отправляем обратно в меню
    await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message)
    
    
    
@router.callback_query(menu_cb.ExitGroupCallbackAccept.filter(), StateFilter(None))
async def exit_group_accept(query: CallbackQuery, user_info: dict):
    await query.answer()
    
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    
    status = await logic.try_to_exit_group(group_id=current_group_id, user_id=user_id, user_info=user_info, bot=query.bot)
    
    if status is False:
        await query.message.answer("Ивент уже начался, нельзя покинуть группу")

    await query.message.delete()
    return



@router.callback_query(menu_cb.CloseEventCallback_1.filter(), StateFilter(None))
async def exit_group(query: CallbackQuery, user_info: dict):
    await query.answer()
    current_group_id = user_info.get("current_group_id", None)
    if current_group_id is None:
        await query.message.delete()
        return
    await query.message.answer("Вы действительно хотите закончить ивент и расскрыть тайных сант?", reply_markup=accept_kb.get_agree_end_event_kb())
    await query.message.delete()
    
    
@router.callback_query(menu_cb.CloseEventCallbackDecline.filter(), StateFilter(None))
async def exit_group_decline(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    if current_group_id is None:
        await query.message.delete()
        return
    
    # Отправляем обратно в меню
    await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message) 
    
    
    
@router.callback_query(menu_cb.CloseEventCallbackAccept.filter(), StateFilter(None))
async def exit_group_decline(query: CallbackQuery, user_info: dict):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    if current_group_id is None:
        await query.message.delete()
        return
    
    # Отправляем обратно в меню
    await logic.send_menu(group_id=current_group_id, user_id=user_id, message=query.message)
    await query.message("заглушка, пока не работает завершение ивента")
    
    
    
# Установить wishlist
@router.callback_query(menu_cb.SetWishlistCallback.filter(), StateFilter(None))
async def set_wishlist_button(query: CallbackQuery, user_info: dict, state: FSMContext):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    await state.set_state(SetWighListState.writing_wishlist)
    wishlist = await user2group.get_wishlist(user_id=user_id, group_id=current_group_id)
    msg = messages.SET_WISHLIST_MSG
    if wishlist is not None:
        msg = msg + f"\n\nТекущее пожелание:\n{wishlist}"
    await query.message.answer(msg, reply_markup=accept_kb.main_exit_kb())
    await query.message.delete()


@router.message(StateFilter(SetWighListState.writing_wishlist))
async def set_wishlist(message: Message, user_info: dict, state: FSMContext):
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await message.delete()
        return
    
    wishlist = message.text
    if len(wishlist) > 500:
        await message.answer("Слишком длинный список желаний")
        return
    if wishlist.startswith("/"):
        await message.answer("""Чтобы прекратить заполнение вишлиста, нажмите кнопку "Назад" """)
        return 
    
    await user2group.update_wishlist(user_id=message.from_user.id, group_id=current_group_id, wishlist=wishlist)
    await state.clear()    
    await logic.send_menu(group_id=user_info['current_group_id'], user_id=message.from_user.id, message=message)
    # await message.answer("Список желаний установлен!")
    
    
# members 
@router.callback_query(menu_cb.GetMembersCallback.filter(), StateFilter(None))
async def get_members(query: CallbackQuery, user_info: dict, state: FSMContext):
    await query.answer()
    user_id = query.from_user.id
    current_group_id = user_info.get("current_group_id", None)
    
    if current_group_id is None:
        await query.message.delete()
        return
    members = await user2group.get_group_members(group_id=current_group_id)
    
    msg = f"Участники группы:\n" 
    
    for member in members:
        msg += f'<a href="tg://user?id={member.user_id}">@{member.user.username}</a>, '
    
    msg = msg[:-2]    
    await query.message.answer(msg, parse_mode="HTML")    
    
    

    
##### ГЛОБАЛЬНАЯ КНОПКА ВЫХОДА #####
@router.callback_query(main_cb.MainExitCallback.filter())
async def main_exit_button(query: CallbackQuery, user_info: dict, state: FSMContext, callback_data: main_cb.MainExitCallback):
    await query.answer()
    await state.clear()
    if callback_data.send_menu and user_info['current_group_id'] is not None:
        await logic.send_menu(group_id=user_info['current_group_id'], user_id=query.from_user.id, message=query.message)
        return 
    await query.message.delete()
    

@router.message(Command("exit"))
async def main_exit_command(message: Message, user_info: dict, state: FSMContext):
    await state.clear()