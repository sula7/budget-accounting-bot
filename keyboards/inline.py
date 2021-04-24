import calendar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from storage.postgres import select_outcome_category

budgets_query = CallbackData('budget', 'amount', 'action')
categories_query = CallbackData('category', 'category_name', 'category_id', 'is_default', 'amount', 'action')

reports_query = CallbackData('report', 'action')
year_query = CallbackData('navigation', 'year', 'action')
period_query = CallbackData('date_c', 'period_date', 'action')


def create_income_outcome_keyboard(amount):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton('📈Доход', callback_data=budgets_query.new(amount=amount, action='add income')),
        InlineKeyboardButton('📉Расход',
                             callback_data=budgets_query.new(amount=amount, action='send categories')))


def create_action_category_keyboard():
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton('Создать категория', callback_data='add_category'),
        InlineKeyboardButton('Удалить категория', callback_data='select category delete'))


def create_outcome_categories_keyboard(chat_id, action, amount=0):
    keyboard = InlineKeyboardMarkup().row()
    if categories := select_outcome_category(chat_id):
        for category_name, category_id, is_default in categories:
            keyboard.insert(InlineKeyboardButton(category_name,
                                                 callback_data=categories_query.new(category_name=category_name,
                                                                                    category_id=category_id,
                                                                                    is_default=is_default,
                                                                                    amount=amount, action=action)))
        keyboard.insert({'text': 'Отмена', 'callback_data': 'cancel'})
        return keyboard
    else:
        return False


def create_report_keyboards():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Текущий месяц', callback_data=reports_query.new(action='current month')),
        InlineKeyboardButton('Период', callback_data=reports_query.new(action='period')))


def create_periods_keyboards(year):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(year - 1, callback_data=year_query.new(year=year - 1, action='add year')),
        InlineKeyboardButton(f'{year}', callback_data=year_query.new(year=year, action='add year')),
        InlineKeyboardButton(year + 1, callback_data=year_query.new(year=year + 1, action='add year')),

        InlineKeyboardButton('⬅', callback_data=year_query.new(year=year, action='previous years')),
        InlineKeyboardButton('Отмена', callback_data='cancel period'),
        InlineKeyboardButton('➡', callback_data=year_query.new(year=year, action='next years'))
    )


def create_months_keyboards(year):
    keyboard = InlineKeyboardMarkup().row()
    for month in range(1, 13):
        keyboard.insert(InlineKeyboardButton(str(month), callback_data=period_query.new(period_date=f'{year}-{month}',
                                                                                        action='add month')))
    return keyboard


def days_keyboards(period_date):
    year, month = period_date.split('-')
    last_dat = calendar.monthrange(int(year), int(month))[-1]
    keyboard = InlineKeyboardMarkup(row_width=5).add()
    for day in range(1, last_dat + 1):
        keyboard.insert(
            InlineKeyboardButton(str(day), callback_data=period_query.new(period_date=f'{period_date}-{day}',
                                                                          action='add period')))
    return keyboard
