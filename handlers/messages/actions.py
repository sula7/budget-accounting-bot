from aiogram import types

from keyboards.inline import budgets_query, create_outcome_categories_keyboard
from keyboards.inline import create_income_outcome_keyboard, categories_query
from loader import dp
from storage.postgres import add_income, add_outcome


@dp.message_handler()
async def send_action_keyboard(message: types.Message):
    if message.text.isdigit() and int(message.text) < 10000000:
        await message.reply('Выберите действия:', reply_markup=create_income_outcome_keyboard(message.text))
    else:
        pass


@dp.callback_query_handler(budgets_query.filter(action='add income'))
async def save_income(query: types.CallbackQuery, callback_data: dict):
    if add_income(callback_data['amount'], query.message.chat.id, query.from_user.full_name):
        await query.message.edit_text('Добавлено в Доход 📈')
    else:
        await query.message.edit_text('Не удалось подключиться к БД')


@dp.callback_query_handler(budgets_query.filter(action='send categories'))
async def send_outcome_category_keyboard(query: types.CallbackQuery, callback_data: dict):
    if categories := create_outcome_categories_keyboard(query.message.chat.id, 'add outcome', callback_data['amount']):
        await query.message.edit_text('Выберите тип расходов', reply_markup=categories)
    else:
        await query.message.edit_text('Не удалось подключиться к БД')


@dp.callback_query_handler(categories_query.filter(action='add outcome'))
async def save_outcome(query: types.CallbackQuery, callback_data: dict):
    if add_outcome(query.message.chat.id, callback_data['category_id'], callback_data['amount']):
        await query.message.edit_text(f"Потрачено на {callback_data['category_name']}")
    else:
        await query.message.edit_text('Не удалось подключиться к БД')
