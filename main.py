import asyncio
import logging
from googletrans import Translator
from random import choice
from aiogram.types import ContentType
from dacite import from_dict
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text

from phrases import *
from config import API_TOKEN, BOT_NAME, MEDIA_PATH
from database import Database
from forms import UserProfileForm
from keyboards import enter_user_form_kb, cancel_reply_kb, main_reply_kb, menu_inline_kb
from models import UserProfile
from utils import download_image

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
database = Database()
translator = Translator()
langs = dict()
def translate(phrase, id):
    return translator.translate(phrase, dest=langs[id]).text


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    langs[message.from_user.id] = 'en'
    await message.answer(translator.translate(welcome_phrase, 'en').text, reply_markup=main_reply_kb)
    await asyncio.sleep(1)
    await message.answer(translator.translate(start_form_phrase, 'en').text, reply_markup=enter_user_form_kb)


@dp.message_handler(commands='menu', state='*')
@dp.message_handler(Text(equals='меню', ignore_case=True))
async def start(message: types.Message):
    await message.answer(translate(show_menu_phrase, message.from_user.id), reply_markup=menu_inline_kb)


@dp.message_handler(Text(equals='Искать людей', ignore_case=True))
async def start(message: types.Message):
    user_data = choice(database.get_all_users())

    with open(user_data.image, 'rb') as image:
        await message.answer_photo(image, translate(f"{user_data.name} {user_data.age} курс \nГруппа: {user_data.team} \n{user_data.description}", message.from_user.id), reply_markup=
                                   types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(translate(link_tg_profile_phrase, message.from_user.id), url=f"tg://user?id={user_data.id}")))


@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(contains='отменить', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer(translate(break_creating_phrase, message.from_user.id), reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(lambda clb: clb.data == 'start_user_form')
async def start_user_form_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer(recreate_profile_phrase, reply_markup=cancel_reply_kb)
    await bot.answer_callback_query(callback_query.id)
    await UserProfileForm.name.set()


@dp.message_handler(state=UserProfileForm.name)
async def process_name(message: types.Message, state: FSMContext):
    message.text = translator.translate(message.text, 'ru').text
    await state.update_data(name=message.text)
    await message.answer(translate(f"Очень приятно, {message.text}. Теперь скажи, на каком курсе ты сейчас учишься", message.from_user.id), reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserProfileForm.age)
async def process_age_invalid(message: types.Message, state: FSMContext):
    return await message.reply(translate(age_not_digit_phrase, message.from_user.id), reply_markup=cancel_reply_kb)


@dp.message_handler(state=UserProfileForm.age)
async def process_age(message: types.Message, state: FSMContext):
    message.text = translator.translate(message.text, 'ru').text
    await state.update_data(age=int(message.text))
    await message.answer(translate(anderstand_phrase, message.from_user.id))
    await asyncio.sleep(1)
    await message.answer(translate(whot_is_u_group_phrase, message.from_user.id), reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.team)
async def process_team(message: types.Message, state: FSMContext):
    message.text = translator.translate(message.text, 'ru').text
    await state.update_data(team=message.text)
    await message.answer(translate(tell_about_yousalf, message.from_user.id), reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.description)
async def process_description(message: types.Message, state: FSMContext):
    message.text = translator.translate(message.text, 'ru').text
    await state.update_data(description=message.text)
    await message.answer(translate(select_ava_phrase, message.from_user.id), reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(content_types=ContentType.PHOTO, state=UserProfileForm.image)
async def process_team(message: types.Message, state: FSMContext):
    path = await download_image(MEDIA_PATH, message.photo[-1])
    await state.update_data(image=path)
    data = from_dict(UserProfile, await state.get_data())
    database.create_user(message.from_user.id, data.name, data.age, data.team, data.description, 1,data.image)
    await message.answer(translate(created_phrase, message.from_user.id), reply_markup=main_reply_kb)
    await state.finish()


@dp.callback_query_handler(lambda clb: clb.data == 'turn_off_activity')
async def turn_off_user_activity(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer(translate(is_n_active_phrase, callback_query.from_user.id), reply_markup=main_reply_kb)


@dp.callback_query_handler(lambda clb: clb.data == 'turn_on_activity')
async def turn_on_user_activity(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer(translate(is_active_phrase, callback_query.from_user.id), reply_markup=main_reply_kb)

if __name__ == '__main__':
    langs = database.get_users_langs()
    executor.start_polling(dp, skip_updates=True)


