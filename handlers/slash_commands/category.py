from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.inline import create_outcome_categories_keyboard, categories_query, create_action_category_keyboard
from loader import dp
from storage.postgres import add_outcome_category, delete_outcome_category


class Category(StatesGroup):
    category_name = State()


@dp.message_handler(commands='category')
async def category(message: types.Message):
    await message.reply('Выберите действие', reply_markup=create_action_category_keyboard())


@dp.callback_query_handler(text_contains='add_category')
async def get_category(message: types.CallbackQuery):
    await message.message.answer('Введите название категории')
    await Category.category_name.set()


@dp.message_handler(state=Category.category_name)
async def add_category(message: types.Message, state: FSMContext):
    if add_outcome_category(message.text, message.chat.id):
        await state.finish()
        await message.reply(f'Категория {message.text} сохранилась')
    else:
        await message.reply('Не удалось подключиться к БД')


@dp.callback_query_handler(text='select category delete')
async def select_category_to_delete(query: types.CallbackQuery):
    if categories := create_outcome_categories_keyboard(query.message.chat.id, 'delete category'):
        await query.message.edit_text('Какую категорию удалить:', reply_markup=categories)
    else:
        await query.message.edit_text('Не удалось подключиться к БД')


@dp.callback_query_handler(categories_query.filter(action='delete category'))
async def delete_category(query: types.CallbackQuery, callback_data: dict):
    if callback_data['is_default'] == 'False':
        if delete_outcome_category(callback_data['category_id']):
            await query.message.edit_text('Удалено')
        else:
            await query.message.edit_text('Не удалось подключиться к БД')
    else:
        await query.message.edit_text('Нельзя удалить')


@dp.callback_query_handler(text='cancel')
async def cancel(call: types.CallbackQuery):
    await call.message.edit_text('Отменено')
