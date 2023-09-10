from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser

from langs import lang_callback, langs_code_and_icon
from phrases import cancel_text

cancel_btn = KeyboardButton(cancel_text)



cancel_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn
)

main_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton("🔍"),
    KeyboardButton("🎇"),
).add(
    KeyboardButton("🔢")
)

period_reply_kb = InlineKeyboardMarkup().add(

)

location_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn,
    KeyboardButton("📍Tекущее", request_location=True)
)


period_selection_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    cancel_btn,
    KeyboardButton("☀️ Весь день"),
    KeyboardButton("♾️ Безсрочно")
)

choose_lang_inline_kb = InlineKeyboardMarkup().add(
    *[InlineKeyboardButton(icon, callback_data=lang_callback.new("lang", code, icon)) for code, icon in langs_code_and_icon]
)

