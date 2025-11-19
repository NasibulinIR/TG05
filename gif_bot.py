import asyncio
import json
import random
from translate import Translator as TextTranslator
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import requests
import logging
from keyboards import main_kb
from config import TOKEN, GIPHY_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class GifFind(StatesGroup):
    waiting_of_query = State()


def translate_text(text: str, target_lang: str = 'ru') -> str:
    """Функция для машинного перевода описания изображения"""
    if not text or text == 'Без описания':
        return text

    try:
        translator = TextTranslator(from_lang='en', to_lang=target_lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        logging.error(f"Ошибка при переводе текста: {e}")
        return text

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Добро пожаловать в бот по поиску GIF-изображений. Используйте клавиатуру '
                         'для взаимодействия с функционалом бота', reply_markup=main_kb)

@dp.message(F.text == 'Случайное GIF-изображение')
async def get_random_gif(message: Message):
    url = f'https://api.giphy.com/v1/gifs/trending'
    params = {
        'api_key': GIPHY_API_KEY,
        'limit': 50,
        'rating': 'pg',
        'lang': 'ru',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            gif = random.choice(data['data'])
            gif_url = gif['images']['original']['url']
            gif_desc = gif.get('alt_text', '')
            await message.answer_animation(gif_url, caption=translate_text(gif_desc) if gif_desc else 'Без описания', reply_markup=main_kb)
        except json.decoder.JSONDecodeError:
            await message.answer('Не удалось обработать ответ от сервера')
    else:
        await message.answer(f'Ошибка при запросе к API: {response.status_code}')


@dp.message(F.text == 'Найти GIF по запросу')
async def find_gif_initialization(message: Message, state: FSMContext):
    await message.answer('Введите поисковый запрос для поиска GIF по ключевому слову (максимальная длина запроса 50 знаков)')
    await state.set_state(GifFind.waiting_of_query)

@dp.message(GifFind.waiting_of_query)
async def find_gif(message: Message, state: FSMContext):
    search_query = message.text.strip()

    if not search_query:
        await message.answer('Запрос не может быть пустым. Попробуйте снова.')
        return

    url = f'https://api.giphy.com/v1/gifs/search'
    params = {
        'api_key': GIPHY_API_KEY,
        'q': search_query, # я знаю что так нельзя, но как мне реализовать ввод от пользователя и поиск GIF по запросу
        'rating': 'r',
        'limit': 50,
        'lang': 'ru',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            if data['data']:
                gif = random.choice(data['data'])
                gif_url = gif['images']['original']['url']
                gif_desc = gif.get('alt_text', '')
                await message.answer_animation(gif_url,
                                               caption=translate_text(gif_desc) if gif_desc else f'Результат по запросу "{search_query}"',
                                               reply_markup=main_kb)
            else:
                await message.answer(f'По запросу "{search_query}" ничего не удалось найти', reply_markup=main_kb)
        except json.decoder.JSONDecodeError:
            await message.answer('Не удалось обработать ответ от сервера', reply_markup=main_kb)
    else:
        await message.answer(f'Ошибка при запросе к API: {response.status_code}', reply_markup=main_kb)

    await state.clear()

@dp.message()
async def empty_handler(message: Message):
    await message.answer('Выбери необходимую функцию, через клавиатуру бота', reply_markup=main_kb)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
