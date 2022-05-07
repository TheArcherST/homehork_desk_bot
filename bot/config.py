from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage

from desk.api import DeskAPI

from config import config


bot = Bot(config.bot_token)
storage = JSONStorage('userflow.json')
dp = Dispatcher(bot, storage=storage)


desk_api = DeskAPI()
