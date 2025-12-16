from aiogram.fsm.state import StatesGroup, State


class CreatingGroupState(StatesGroup):
    writing_name = State()
    writing_description = State()