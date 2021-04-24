from aiogram import types
from aiogram.utils.markdown import hbold

from loader import dp


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(message: types.Message):
    await message.reply('Отправьте любую сумму для сохранения в бюджете\n'
                        'Команда {} - для работы с категориями\n'
                        'Команда {} - для вывода отчета\n'.format(hbold('/category'), hbold('/report')))
