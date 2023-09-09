from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser

cancel_btn = KeyboardButton("Отменить")

enter_user_form_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Пройти форму", callback_data="start_user_form")
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

menu_inline_kb = InlineKeyboardMarkup().row(
    InlineKeyboardButton("Выключить поиск", callback_data="turn_off_activity"),
    InlineKeyboardButton("Включить поиск", callback_data="turn_on_activity"),
).add(
    InlineKeyboardButton("Перезаполнить форму", callback_data="start_user_form"),
    InlineKeyboardButton("Создать событие", callback_data="start_event_form")
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