import asyncio
import logging
from googletrans import Translator
from random import choice
from aiogram.types import ContentType, Location, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, \
    ReplyKeyboardMarkup, KeyboardButton
from dacite import from_dict
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text
import ast
from langs import lang_callback
import validators
from phrases import *
from config import API_TOKEN, BOT_NAME, MEDIA_PATH
from controllers import UserController, EventController
from database import Database
from forms import UserProfileForm, EventForm
from keyboards import choose_lang_inline_kb
from models import UserProfile, EventData, UserData
from utils import download_image

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
database = Database()
user_controller = UserController(database)
event_controller = EventController(database)
translator = Translator()
langs = dict()


def translate(phrase, _id):
    if len(langs.items()) == 0 or langs.get(_id, "ru") == "ru":
        return phrase
    return translator.translate(phrase, dest=langs[_id]).text


def enter_user_form_kb(id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(translate("Пройти форму", id), callback_data="start_user_form")
    ).add(
        InlineKeyboardButton("Select language", callback_data="choose_lang")
    )


def menu_inline_kb(id):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(translate("🔇", id), callback_data="turn_off_activity"),
        InlineKeyboardButton(translate("🔈", id), callback_data="turn_on_activity"),
    ).add(
        InlineKeyboardButton(translate("✏️ Анкета", id), callback_data="start_user_form"),
        InlineKeyboardButton(translate("🖋️ Событие", id), callback_data="start_event_form")
    ).add(
        InlineKeyboardButton(translate("🧑‍🎓 Моя анкета", id), callback_data="self_form")
    ).add(
        InlineKeyboardButton("🔠 Select language", callback_data="choose_lang")
    )


def un_state_reply_kb(_id):
    return ReplyKeyboardMarkup(resize_keyboard=True).row(
        KeyboardButton("1️⃣"),
        KeyboardButton("2️⃣"),
        KeyboardButton("3️⃣"),
        KeyboardButton("4️⃣"),
    ).add(
        KeyboardButton(translate("Преподаватель", _id)),
        KeyboardButton(translate("Работник", _id)),
    )


def main_reply_kb(_id):
    return ReplyKeyboardMarkup(resize_keyboard=True).row(
        KeyboardButton(translate("🔍 Люди", _id)),
        KeyboardButton(translate("🎇 События", _id)),
    ).add(
        KeyboardButton(translate("🔢 Меню", _id))
    )


def location_reply_kb(_id: int):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(translate(cancel_text, _id)),
        KeyboardButton(translate("📍Tекущее", _id), request_location=True)
    )


def period_selection_reply_kb(_id: int):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(translate(cancel_text, _id)),
        KeyboardButton(translate("☀️ Весь день", _id)),
        KeyboardButton(translate("♾️ Безсрочно", _id))
    )


def cancel_reply_kb(_id: int):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton(translate(cancel_text, _id)),
    )


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    # langs[message.from_user.id] = 'en'
    await message.answer(translate(welcome_phrase, message.from_user.id) + '\n\n' + lang_annotation,
                         reply_markup=main_reply_kb(message.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)
    await asyncio.sleep(1)
    await message.answer(translate(start_form_phrase, message.from_user.id),
                         reply_markup=enter_user_form_kb(message.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)


@dp.message_handler(commands='menu', state='*')
@dp.message_handler(Text(contains='🔢', ignore_case=True))
async def show_menu(message: types.Message):
    await message.answer(translate(show_menu_phrase, message.from_user.id),
                         reply_markup=menu_inline_kb(message.from_user.id))


@dp.message_handler(Text(contains='🔍', ignore_case=True))
async def show_users(message: types.Message):
    users = list(filter(lambda data: data.id != message.from_user.id, user_controller.get_all_users()))

    if len(users) <= 0:
        return await message.answer(translate("Пока я не могу найти людей", message.from_user.id),
                                    reply_markup=main_reply_kb(message.from_user.id))

    user_data = choice(users)
    await show_user_profile_card(message, user_data, message.from_user.id)


@dp.message_handler(Text(contains='🎇', ignore_case=True))
async def show_events(message: types.Message):
    events = list(filter(lambda data: data.author_id != message.from_user.id, event_controller.get_all_events()))

    if len(events) <= 0:
        return await message.answer(translate("Событий пока нет", message.from_user.id),
                                    reply_markup=main_reply_kb(message.from_user.id))
    event = choice(events)

    await show_event_card(message, event, message.from_user.id)


# выход из любого состояния

@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(contains=cancel_text, ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer(translate(break_creating_phrase, message.from_user.id), reply_markup=main_reply_kb(message.from_user.id))


# ----------------------------Обработка формы пользователя------------------------------------

@dp.callback_query_handler(lambda clb: clb.data == 'start_user_form')
async def start_user_form_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer(translate(recreate_profile_phrase, callback_query.from_user.id),
                                        reply_markup=cancel_reply_kb(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)
    await bot.answer_callback_query(callback_query.id)
    await UserProfileForm.name.set()


@dp.message_handler(state=UserProfileForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(translate(which_course_question,
                                   message.from_user.id), reply_markup=un_state_reply_kb(message.from_user.id),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.un_state)
async def process_university_state(message: types.Message, state: FSMContext):
    message.text = translator.translate(message.text, 'ru').text
    await state.update_data(un_state=message.text)
    await message.answer(translate(whot_is_u_group_phrase, message.from_user.id), reply_markup=cancel_reply_kb(message.from_user.id),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.team)
async def process_team(message: types.Message, state: FSMContext):
    await state.update_data(team=message.text)
    await message.answer(translate(tell_about_yousalf, message.from_user.id), reply_markup=cancel_reply_kb(message.from_user.id),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.description)
async def process_description(message: types.Message, state: FSMContext):
    message.text = translator.translate(message.text, 'ru').text
    await state.update_data(description=message.text)
    await message.answer(translate(select_ava_phrase, message.from_user.id), reply_markup=cancel_reply_kb(message.from_user.id))
    await UserProfileForm.next()


@dp.message_handler(content_types=ContentType.PHOTO, state=UserProfileForm.image)
async def process_image(message: types.Message, state: FSMContext):
    path = await download_image(MEDIA_PATH, message.photo[-1])
    await state.update_data(image=path)
    # print(await state.get_data())
    data = from_dict(UserProfile, await state.get_data())
    user_controller.create_user(
        UserData(
            message.from_user.id,
            data.name,
            data.un_state,
            data.team,
            data.description,
            1,
            path,
            langs.get(message.from_user.id, 'ru')
        )
    )
    await message.answer(translate(successfully_user_creation, message.from_user.id), reply_markup=main_reply_kb(message.from_user.id),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await state.finish()


# ----------------------------Форма события/мероприятия------------------------------------


@dp.callback_query_handler(lambda clb: clb.data == 'start_event_form')
async def start_event_form_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer(
        translate(event_place_question,
                  callback_query.message.from_user.id), reply_markup=location_reply_kb(callback_query.from_user.id),
        parse_mode=ParseMode.MARKDOWN_V2)
    await EventForm.location.set()


@dp.message_handler(state=EventForm.location, content_types=[ContentType.LOCATION, ContentType.TEXT])
async def process_location(message: types.Message, state: FSMContext):
    if not message.location:
        await state.update_data(location=message.text)
    else:
        await state.update_data(location=str(message.location))

    await message.answer(
        translate(event_time_question,
                  message.from_user.id), reply_markup=period_selection_reply_kb(message.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)
    await EventForm.next()


@dp.message_handler(state=EventForm.time)
async def process_period(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer(translate(tell_about_event, message.from_user.id), reply_markup=cancel_reply_kb(message.from_user.id),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await EventForm.next()


@dp.message_handler(state=EventForm.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(translate(event_link_question, message.from_user.id), reply_markup=cancel_reply_kb(message.from_user.id),
                         parse_mode=ParseMode.MARKDOWN_V2)
    await EventForm.next()


@dp.message_handler(lambda msg: not (msg.text[0] == "@" or validators.url(msg.text)), state=EventForm.invite_link)
async def process_invite_link_invalid(message: types.Message, state: FSMContext):
    return await message.answer(translate(event_link_invalid, message.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)


@dp.message_handler(state=EventForm.invite_link)
async def process_invite_link(message: types.Message, state: FSMContext):
    await state.update_data(invite_link=message.text)
    await message.answer(
        translate(select_event_preview, message.from_user.id),
        reply_markup=cancel_reply_kb(message.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)
    await EventForm.next()


@dp.message_handler(state=EventForm.image, content_types=ContentType.PHOTO)
async def process_event_image(message: types.Message, state: FSMContext):
    path = await download_image(MEDIA_PATH, message.photo[-1])
    await state.update_data(image=path)
    state_data = await state.get_data()
    state_data['id'] = 0
    state_data['author_id'] = message.from_user.id
    state_data['image'] = path
    data = from_dict(EventData, state_data)

    event_controller.create_event(EventData(
        0,
        message.from_user.id,
        str(data.location),
        data.time,
        data.description,
        data.invite_link,
        path
    ))
    await state.finish()
    await message.answer(translate(successfully_event_creation, message.from_user.id), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=main_reply_kb(message.from_user.id))


# ----------------------------Choose language------------------------------------


@dp.message_handler(Text(equals='choose_lang', ignore_case=True))
@dp.callback_query_handler(lambda clb: clb.data == 'choose_lang')
async def choose_language_handler(data):
    if isinstance(data, types.CallbackQuery):
        await bot.answer_callback_query(data.id)
    message = data.message if isinstance(data, types.CallbackQuery) else data
    user_id = data.from_user.id if isinstance(data, types.CallbackQuery) else data.message.from_user.id

    await message.answer(translate("🔱*Select a language from the suggested ones*", user_id),
                         reply_markup=choose_lang_inline_kb, parse_mode=ParseMode.MARKDOWN_V2)


@dp.callback_query_handler(lang_callback.filter(command="lang"))
async def process_choose_lang(callback_query: types.CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(callback_query.id)
    langs[callback_query.from_user.id] = callback_data['code']
    user_controller.update_user_lang(callback_query.from_user.id, callback_data['code'])
    await callback_query.message.answer(
        translate("👊 Отлично, теперь мы сможем говорить на одном языке", callback_query.from_user.id),
        parse_mode=ParseMode.MARKDOWN_V2, reply_markup=main_reply_kb(callback_query.from_user.id))


@dp.callback_query_handler(lambda clb: clb.data == 'turn_off_activity')
async def turn_off_user_activity(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_controller.change_user_activity(callback_query.from_user.id, 0)
    await callback_query.message.answer(translate(is_n_active_phrase, callback_query.from_user.id),
                                        reply_markup=main_reply_kb(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)


@dp.callback_query_handler(lambda clb: clb.data == 'turn_on_activity')
async def turn_on_user_activity(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_controller.change_user_activity(callback_query.from_user.id, 1)
    await callback_query.message.answer(translate(is_active_phrase, callback_query.from_user.id),
                                        reply_markup=main_reply_kb(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN_V2)


@dp.callback_query_handler(lambda clb: clb.data == 'self_form')
async def show_self_form(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user = user_controller.get_user(callback_query.from_user.id)
    if user is None:
        return await callback_query.message.answer("Ты еще не созадл анкету 😗")
    await show_user_profile_card(callback_query.message, user, callback_query.from_user.id)


# ----------------------------Message templates------------------------------------


async def show_user_profile_card(message: types.Message, data: UserData, user_id: int):
    with open(data.image, 'rb') as image:
        await message.answer_photo(image,
                                   f"{data.name} \n{data.un_state + translate('Курс', user_id) if data.un_state in ['2️⃣', '1️⃣', '3️⃣', '4️⃣'] else data.un_state} \n{translate('Группа', user_id)}: {data.team} \n{translate(data.description, user_id)}",
                                   reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                       translate(link_tg_profile_phrase, user_id),
                                       url=f"tg://user?id={data.id}")
                                   )
                                   )


async def show_event_card(message: types.Message, data: EventData, user_id: int):
    try:
        loc = ast.literal_eval(data.location)
    except (ValueError, SyntaxError):
        with open(data.image, 'rb') as image:
            await message.answer_photo(image,
                                       translate(f"{data.description} \nМесто: {data.location} \nВремя: {data.time}",
                                                 user_id),
                                       reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                           translate("Смотреть", user_id),
                                           url=data.invite_link if data.invite_link[
                                                                       0] != '@' else f"https://t.me/{data.invite_link[1::]}")
                                       ))
    else:
        with open(data.image, 'rb') as image:
            await message.answer_photo(image,
                                       translate(f"{data.description} \nВремя: {data.time}",
                                                 user_id),
                                       reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                           translate("Смотреть", user_id),
                                           url=data.invite_link if data.invite_link[
                                                                       0] != '@' else f"https://t.me/{data.invite_link[1::]}")
                                       ))

            await message.answer(translate("⬇️ *Место проведения* ⬇️", user_id), parse_mode=ParseMode.MARKDOWN_V2)
            await message.answer_location(loc['latitude'], loc['longitude'], reply_markup=main_reply_kb(message.from_user.id))


if __name__ == '__main__':
    langs = user_controller.get_users_langs()
    executor.start_polling(dp, skip_updates=True)
