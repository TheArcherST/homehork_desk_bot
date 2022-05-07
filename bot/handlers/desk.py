from aiogram_keyboards import Keyboard, DialogMeta


class DeskHandler(Keyboard):
    async def __text__(self, meta: DialogMeta) -> str:
        pass
