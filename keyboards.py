from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

enter_user_form_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Пройти форму", callback_data="start_user_form")
)

cancel_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Отменить")
)

main_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Смотреть"),
    KeyboardButton("Меню"),

)

menu_inline_kb = InlineKeyboardMarkup().row(
    InlineKeyboardButton("Выключить поиск", callback_data="turn_off_activity"),
    InlineKeyboardButton("Включить поиск", callback_data="turn_on_activity"),
).add(
    InlineKeyboardButton("Перезаполнить форму", callback_data="start_user_form"),

)