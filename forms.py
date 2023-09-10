from aiogram.dispatcher.filters.state import State, StatesGroup


class UserProfileForm(StatesGroup):
    name = State()
    age = State()
    team = State()
    description = State()
    image = State()


class EventForm(StatesGroup):
    location = State()
    time = State()
    description = State()
    invite_link = State()
    image = State()


