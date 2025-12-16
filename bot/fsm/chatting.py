from aiogram.fsm.state import StatesGroup, State


class MsgSantaState(StatesGroup):
    writing_msg = State()
    
class MsgPairState(StatesGroup):
    writing_msg = State()