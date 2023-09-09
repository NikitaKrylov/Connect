import asyncio
import logging
from random import choice
from aiogram.types import ContentType
from dacite import from_dict
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text
from config import API_TOKEN, BOT_NAME, MEDIA_PATH
from controllers import UserController
from database import Database
from forms import UserProfileForm, EventForm
from keyboards import enter_user_form_kb, cancel_reply_kb, main_reply_kb, menu_inline_kb, location_reply_kb, \
    self_invite_link_reply_kb, period_selection_reply_kb
from models import UserProfile, EventData, UserData
from utils import download_image, translate

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
database = Database()
user_controller = UserController(database)


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Привет!!! 👋\nЯ {BOT_NAME}, бот для поиска новых знакомств в рамках университета МИСИС. \nЕсли хочешь найти друга или интересно провести время, ты обратился по адресу 😉", reply_markup=main_reply_kb)
    await asyncio.sleep(1)
    await message.answer(f"Расскажи немного о себе, чтобы я смог подобрать людей по интересам",
                         reply_markup=enter_user_form_kb)


@dp.message_handler(commands='menu', state='*')
@dp.message_handler(Text(equals='меню', ignore_case=True))
async def start(message: types.Message):
    await message.answer("Это меню взаимодействия, здесь перечислены основные комманды", reply_markup=menu_inline_kb)


@dp.message_handler(Text(equals='Искать людей', ignore_case=True))
async def start(message: types.Message):
    user_data = choice(user_controller.get_all_users())

    with open(user_data.image, 'rb') as image:
        await message.answer_photo(image, f"{user_data.name} {user_data.age} курс \nГруппа: {user_data.team} \n{user_data.description}", reply_markup=
                                   types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Познакомиться", url=f"tg://user?id={user_data.id}")))
    # await message.answer(choice(user_data))


# выход из любого состояния

@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(contains='отменить', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer("Ок, закончим позже", reply_markup=main_reply_kb)


# ----------------------------Обработка формы пользователя------------------------------------

@dp.callback_query_handler(lambda clb: clb.data == 'start_user_form')
async def start_user_form_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Ок, давай начнем. Как другие смогут к тебе обращаться?", reply_markup=cancel_reply_kb)
    await bot.answer_callback_query(callback_query.id)
    await UserProfileForm.name.set()


@dp.message_handler(state=UserProfileForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Очень приятно, {message.text}. Теперь скажи, на каком курсе ты сейчас учишься", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserProfileForm.age)
async def process_age_invalid(message: types.Message, state: FSMContext):
    return await message.reply("Пожалуйста, введи курса числом", reply_markup=cancel_reply_kb)


@dp.message_handler(state=UserProfileForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer(f"Понял")
    await asyncio.sleep(1)
    await message.answer(f"Какая твоя группа, так я смогу подобрать более интересные мероприятия", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.team)
async def process_team(message: types.Message, state: FSMContext):
    await state.update_data(team=message.text)
    await message.answer(f"Отлично, теперь самое главное. Расскажи немного о себе", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(f"Пожалуйста, выбери аватарку", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(content_types=ContentType.PHOTO, state=UserProfileForm.image)
async def process_team(message: types.Message, state: FSMContext):
    path = await download_image(MEDIA_PATH, message.photo[-1])
    await state.update_data(image=path)
    data = from_dict(UserProfile, await state.get_data())
    user_controller.create_user(UserData(
        message.from_user.id, data.name, data.age, data.team, data.description, 1, data.image
        ))
    await message.answer("Пользователь успешно созданн!", reply_markup=main_reply_kb)
    await state.finish()


# ----------------------------Форма события/мероприятия------------------------------------


@dp.callback_query_handler(lambda clb: clb.data == 'start_event_form')
async def start_event_form_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer(translate("Давай заполним форму события/мероприятия. \nУкажи место проведения или отправь локацию"), reply_markup=location_reply_kb)
    await EventForm.location.set()


@dp.message_handler(state=EventForm.location, content_types=[ContentType.LOCATION, ContentType.TEXT])
async def process_location(message: types.Message, state: FSMContext):
    if not message.location:
        await state.update_data(location=message.text)
    else:
        await state.update_data(location=message.location)

    await message.answer(translate("В какое время будет проходить мероприятие? \nЕсли време неоднозначно, выбери пункт из меню"), reply_markup=period_selection_reply_kb)
    await EventForm.next()


@dp.message_handler(state=EventForm.period)
async def process_period(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)
    await message.answer(translate("Отправь описание"))
    await EventForm.next()


@dp.message_handler(state=EventForm.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(translate("Чтобы люди смогли перейти на мероприятие или узнать о нем больше, дай мне ссылку на событие или нажми на кнопку ниже чтобы люди смогли написать тебе"), reply_markup=self_invite_link_reply_kb)
    await EventForm.next()


@dp.message_handler(state=EventForm.invite_link)
async def process_invite_link(message: types.Message, state: FSMContext):
    await state.update_data(invite_link=message.text)
    await message.answer(translate("И наконец, пришли какое-нибудь фото чтобы заинтересовать людей)"))
    await EventForm.next()


@dp.message_handler(state=EventForm.image, content_types=ContentType.PHOTO)
async def process_event_image(message: types.Message, state: FSMContext):
    # path = await download_image(MEDIA_PATH, message.photo[-1])
    # await state.update_data(image=path)
    await message.answer(translate("Все готово!"))
    state_data = await state.get_data()
    # data = from_dict(EventData, state_data)
    await message.answer(state_data, reply_markup=main_reply_kb)
    await state.finish()





@dp.callback_query_handler(lambda clb: clb.data == 'turn_off_activity')
async def turn_off_user_activity(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Ок, теперь вы не будете появляться в подборке у других людей 🙈", reply_markup=main_reply_kb)


@dp.callback_query_handler(lambda clb: clb.data == 'turn_on_activity')
async def turn_on_user_activity(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Теперь тебя видят другие люди", reply_markup=main_reply_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

