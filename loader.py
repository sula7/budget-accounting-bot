import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Тут погружаем все переменные которые нужны для хендлеров

bot = Bot(token="TOKEN", parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.ERROR, filename='budget.log', filemode='a',
                    format='%(asctime)s ; %(message)s ; %(levelname)s ; %(filename)s:%(lineno)s')
logger.setLevel(logging.DEBUG)
