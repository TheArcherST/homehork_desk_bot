import datetime

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message

from sqlalchemy import update

from bot.config import dp
from models import User, Session


class UsersMiddleware(BaseMiddleware):
    @staticmethod
    async def on_pre_process_message(message: Message, *_args):
        """Users indexer

        If user not in database yet, creates one
        If in database, update last_activity

        """

        session = Session()
        result = session.get(User, message.from_user.id)

        if not result:
            session.add(User(user_id=message.from_user.id,
                             username=message.from_user.username,
                             last_activity=datetime.datetime.utcnow()))
        else:
            session.execute(update(User)
                            .where(User.user_id == message.from_user.id)
                            .values(last_activity=datetime.datetime.utcnow()))

        session.close()

        return None


dp.setup_middleware(UsersMiddleware())
