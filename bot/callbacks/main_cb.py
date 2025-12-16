from aiogram.filters.callback_data import CallbackData
from typing import Union

class JoinGroupCallback(CallbackData, prefix="join_group"):
    ...

class CreateGroupCallback(CallbackData, prefix="create_group"):
    ...
    
class CloseJoiningGroupCallback(CallbackData, prefix="close_joining"):
    ...
    

class MainExitCallback(CallbackData, prefix="main_exit"):
    send_menu: bool = True
    
class ChooseGroupCallback(CallbackData, prefix="choose"):
    group_id: int
    
    
class FirstBtnCallback(CallbackData, prefix="first"):
    ...

class SecondBtnCallback(CallbackData, prefix="second"):
    ...