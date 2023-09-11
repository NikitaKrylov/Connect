from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser

from langs import lang_callback, langs_code_and_icon
from phrases import cancel_text


choose_lang_inline_kb = InlineKeyboardMarkup().add(
    *[InlineKeyboardButton(icon, callback_data=lang_callback.new("lang", code, icon)) for code, icon in langs_code_and_icon]
)

