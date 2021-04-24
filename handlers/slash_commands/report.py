import calendar
from datetime import date

from aiogram import types
from aiogram.utils.markdown import hbold, hunderline

from keyboards.inline import create_report_keyboards, reports_query, create_periods_keyboards, create_months_keyboards, \
    days_keyboards, year_query, period_query
from loader import dp
from storage.postgres import get_report_json

period = []


@dp.message_handler(state='*', commands=['report'])
async def select_report(message: types.Message):
    await message.reply('📅 Выберите отчет:',
                        reply_markup=create_report_keyboards())


@dp.callback_query_handler(reports_query.filter(action='current month'))
async def send_report_current_month(query: types.CallbackQuery):
    year = date.today().year
    month = date.today().month
    last_day = calendar.monthrange(year, month)[-1]
    start = f'{year}-{month}-1'
    end = f'{year}-{month}-{last_day}'
    await query.message.edit_text(create_report(start, end, query.message.chat.id))


@dp.callback_query_handler(reports_query.filter(action='period'))
async def select_period(query: types.CallbackQuery):
    await query.message.edit_text('Начало периода', reply_markup=create_periods_keyboards(date.today().year))


@dp.callback_query_handler(year_query.filter(action='previous years'))
async def previous_years(query: types.CallbackQuery, callback_data: dict):
    await query.message.edit_text('Выберите год', reply_markup=create_periods_keyboards(int(callback_data['year']) - 3))


@dp.callback_query_handler(text='cancel period')
async def cancel(call: types.CallbackQuery):
    period.clear()
    await call.message.edit_text('Отменено')


@dp.callback_query_handler(year_query.filter(action='next years'))
async def next_years(query: types.CallbackQuery, callback_data: dict):
    await query.message.edit_text('Выберите год', reply_markup=create_periods_keyboards(int(callback_data['year']) + 3))


@dp.callback_query_handler(year_query.filter(action='add year'))
async def select_month(query: types.CallbackQuery, callback_data: dict):
    await query.message.edit_text('Выберите месяц', reply_markup=create_months_keyboards(callback_data['year']))


@dp.callback_query_handler(period_query.filter(action='add month'))
async def select_day(query: types.CallbackQuery, callback_data: dict):
    await query.message.edit_text('Выберите день', reply_markup=days_keyboards(callback_data['period_date']))


@dp.callback_query_handler(period_query.filter(action='add period'))
async def send_period_report(query: types.CallbackQuery, callback_data: dict):
    period.append(callback_data['period_date'])
    if len(period) == 2:
        start, end = period[0], period[1]
        period.clear()
        await query.message.edit_text(create_report(start, end, query.message.chat.id))
    else:
        await query.message.edit_text('Конец даты', reply_markup=create_periods_keyboards(date.today().year))


def create_report(start, end, chat_id):
    if report_json := get_report_json(start, end, chat_id):
        if report_json['incomes'] is not None and report_json['outcome']:
            report = [hbold(f'📊 Отчет \n{start}\n{end}\n'), hbold('📈 Доходы')]

            for income in report_json['incomes']:
                report.append(f"👤 {income['username']}: {income['user_amount']} ({income['percentage']})")
            report.append(hunderline(f"💰 Итого: {report_json['incomes_total_amount']}\n"))

            report.append(hbold('📉 Расходы'))
            for outcome in report_json['outcome']:
                report.append(f"{outcome['category_name']}: {outcome['category_amount']} ({outcome['percentage']})")
            report.append(hunderline(f"💰 Итого: {report_json['outcome_total_amount']}"))
            report.append(hbold(
                f"\n💸 Остаток: {round(report_json['incomes_total_amount'] - report_json['outcome_total_amount'], 0)}"))
            return '\n'.join(report)
        else:
            return 'Необходимо заполнить доходы и расходы'
    else:
        return 'Не удалось подключиться к БД'
