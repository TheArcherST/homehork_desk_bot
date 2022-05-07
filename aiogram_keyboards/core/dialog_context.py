from typing import Union, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from .dialog_meta import DialogMeta


class DialogContext:
    async def __aenter__(self, meta: 'DialogMeta' = None):
        if meta is not None:
            self._meta = meta

        await self._load()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._save()
        self._data.clear()

    def __init__(self, meta: 'DialogMeta' = None, data: dict = None):
        self._meta = meta
        self._data = data

    async def _load(self):
        if self._data is None:
            self._data = await self._meta.fsm_context.get_data()

    async def _save(self):
        await self._meta.fsm_context.set_data(self._data)

    def __getattr__(self, item):
        if item.startswith("_DialogContext"):
            return

        if self._data is None:
            raise RuntimeError('Data not provided. Use object in context manager.')

        return self._data.get(item)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._data.update({key: value})
