from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Случайное GIF-изображение'),
         KeyboardButton(text='Найти GIF по запросу')],
    ], resize_keyboard=True
)