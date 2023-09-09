import asyncio
import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart

from config import API_TOKEN, BOT_NAME
from forms import UserProfileForm
from keyboards import enter_user_form_btn

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Привет! \nЯ {BOT_NAME}, бот для поиска новых знакомств в рамках университета МИСИС. \nЯ помогу тебе найти новую компанию друзей или клуб по интересам")
    await asyncio.sleep(1)
    await message.answer("Расскажи немного о себе, чтобы я смог подобрать людей по интересам",
                         reply_markup=enter_user_form_btn)


@dp.callback_query_handler(lambda clb: clb.data == 'start_user_form')
async def start_user_form_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Ок, давай начнем. Как мне к другие смогут к тебе обращаться?")
    await UserProfileForm.name.set()


@dp.message_handler(state=UserProfileForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Очень приятно, {message.text}. Теперб скажи какой твой возраст")
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(f"Понял")
    await asyncio.sleep(1)
    await message.answer(f"Какая твоя группа, так я смогу познакомить тебя с твоими новыми одногрупниками")
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.group)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text)
    await message.answer(f"Отлично, теперь самое главное. Расскажи немного о себе")
    await UserProfileForm.next()


@dp.message_handler(state=UserProfileForm.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await message.answer(data)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
