from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser
from main import translate

cancel_btn = KeyboardButton("Отменить")

def enter_user_form_kb(id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(translate("Пройти форму", id), callback_data="start_user_form")
        )

cancel_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn
)

main_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton("Искать людей"),
    KeyboardButton("События"),
).add(
    KeyboardButton("Меню")
)

def menu_inline_kb(id):
    return InlineKeyboardMarkup().row(
    InlineKeyboardButton(translate("Выключить поиск", id), callback_data="turn_off_activity"),
    InlineKeyboardButton(translate("Включить поиск", id), callback_data="turn_on_activity"),
    ).add(
    InlineKeyboardButton(translate("Перезаполнить форму", id), callback_data="start_user_form"),
    InlineKeyboardButton(translate("Создать событие", id), callback_data="start_event_form")
    )

period_reply_kb = InlineKeyboardMarkup().add(

)

location_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn,
    KeyboardButton("Отпраить текущее", request_location=True)
)
self_invite_link_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn,
    KeyboardButton("Отправить юзернейм")
)

period_selection_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn,
    KeyboardButton("Весь день"),
    KeyboardButton("Безсрочно")
)