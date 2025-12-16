from aiogram.fsm.state import StatesGroup, State


class SetWighListState(StatesGroup):
    writing_wishlist = State()