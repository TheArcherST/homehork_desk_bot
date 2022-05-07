"""

Place to install bot command hints

"""


import asyncio

from .config import bot
from aiogram.types import BotCommand


asyncio.gather(
    bot.set_my_commands(
        [
            BotCommand('start', 'Начать'),
            BotCommand('help', 'Помощь'),
            BotCommand('cancel', 'Отмена')
        ])
)
