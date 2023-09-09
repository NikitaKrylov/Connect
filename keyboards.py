from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

enter_user_form_btn = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Пройти форму", callback_data="start_user_form")
)