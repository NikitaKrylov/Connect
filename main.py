import asyncio
import logging

from aiogram.types import ContentType
from dacite import from_dict
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text

from config import API_TOKEN, BOT_NAME
from forms import UserProfileForm
from keyboards import enter_user_form_kb, cancel_reply_kb, main_reply_kb
from models import UserProfile

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Привет! \nЯ {BOT_NAME}, бот для поиска новых знакомств в рамках университета МИСИС. \nЯ помогу тебе найти новую компанию друзей или клуб по интересам", reply_markup=main_reply_kb)
    await asyncio.sleep(1)
    await message.answer("Расскажи немного о себе, чтобы я смог подобрать людей по интересам",
                         reply_markup=enter_user_form_kb)


@dp.message_handler(Text(equals='меню', ignore_case=True))
async def start(message: types.Message):
    await message.answer("Показываю меню")


@dp.message_handler(Text(equals='смотреть', ignore_case=True))
async def start(message: types.Message):
    await message.answer("Показываю карточку с событием или человеком")


@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(Text(contains='отменить', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer("Ок, закончим позже", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(lambda clb: clb.data == 'start_user_form')
async def start_user_form_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Ок, давай начнем. Как мне к другие смогут к тебе обращаться?", reply_markup=cancel_reply_kb)
    await UserProfileForm.name.set()


@dp.message_handler(state=UserProfileForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Очень приятно, {message.text}. Теперб скажи какой твой возраст", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(lambda message: not message.text.isdigit(), state=UserProfileForm.age)
async def process_age_invalid(message: types.Message, state: FSMContext):
    return await message.reply("Пожалуйста введи возраст числом", reply_markup=cancel_reply_kb)


@dp.message_handler(state=UserProfileForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer(f"Понял")
    await asyncio.sleep(1)
    await message.answer(f"Какая твоя группа, так я смогу познакомить тебя с твоими новыми одногрупниками", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.group)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer(f"Отлично, теперь самое главное. Расскажи немного о себе", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(f"Скинь пару фоток, если есть", reply_markup=cancel_reply_kb)
    await UserProfileForm.next()


@dp.message_handler(content_types=ContentType.PHOTO, state=UserProfileForm.images)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(images="")
    data = from_dict(UserProfile, await state.get_data())
    await message.answer(data, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


