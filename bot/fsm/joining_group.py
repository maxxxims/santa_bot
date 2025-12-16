from aiogram.fsm.state import StatesGroup, State


class JoiningGroupState(StatesGroup):
    writing_code = State()