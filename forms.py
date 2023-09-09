from aiogram.dispatcher.filters.state import State, StatesGroup


class UserProfileForm(StatesGroup):
    name = State()
    age = State()
    team = State()
    description = State()
    image = State()




