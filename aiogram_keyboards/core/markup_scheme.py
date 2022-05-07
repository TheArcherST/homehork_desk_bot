from typing import overload, Callable, Awaitable, Optional, Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from .dialog_meta import DialogMeta
from .button import Button
from .helpers import MarkupType


class MarkupSchemeButton:
    @overload
    def __init__(self,
                 text: str,
                 url: str = None,
                 row_width: int = 1,
                 callback_data: str = None):

        pass

    @overload
    def __init__(self, *,
                 button: Button,
                 row_width: int = 1):
        pass

    def __init__(self,
                 text: str = None,
                 callback_data: str = None,
                 url: str = None,
                 button: Button = None,
                 row_width: int = 1):

        if button is not None:
            text = button.text
            callback_data = button.inline().callback_data

        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.row_width = row_width


class SelectionMask:
    def __init__(self, selection: list[int], ignored: list[int]):
        self.selection = selection
        self.ignored = ignored
        self.length = len(selection) + len(ignored)

    @classmethod
    def parse(cls, string: str) -> 'SelectionMask':
        selection = []
        ignored = []
        n = 0
        for i in string:
            if i == ' ':
                continue
            elif i == '.':
                ignored.append(n)
                n += 1
            else:
                selection.append(n)
                n += 1

        mask = SelectionMask(selection, ignored)
        return mask

    def resolve_index(self, index: int):
        return self.selection[index]

    def resolve_ignored_index(self, index: int) -> int:
        return self.ignored[index]


class MarkupConstructor:
    """ Object, that helps you fastly change markup """

    def __init__(self, rows: list[list[MarkupSchemeButton]]):
        self.rows = rows

    @property
    def buttons(self) -> list[MarkupSchemeButton]:
        for i in self.rows:
            yield from i

    def add_row(self, row: list[MarkupSchemeButton], index: int = None):
        if index is None:
            self.rows.append(row)
        else:
            self.rows[index] = row

    def add(self,
            row: int,
            buttons: Union[MarkupSchemeButton, str, list[Union[MarkupSchemeButton, str]]],
            mask: str = None):

        # prepare buttons
        if isinstance(buttons, list):
            for i in range(len(buttons)):
                if isinstance(buttons[i], str):
                    buttons[i] = MarkupSchemeButton(buttons[i])
        else:
            if isinstance(buttons, str):
                buttons = [MarkupSchemeButton(buttons)]
            else:
                buttons = [buttons]

        if mask is not None:
            if isinstance(mask, str):
                mask = SelectionMask.parse(mask)

            if len(mask.selection) != len(buttons):
                raise IndexError("Selection length != len of buttons list, can't insert")

            result: list = [0 for _ in range(mask.length)]

            for i in range(len(self.rows[row])):
                result[mask.resolve_ignored_index(i)] = self.rows[row][i]
            for i in range(len(buttons)):
                result[mask.resolve_index(i)] = buttons[i]

            return self.add_row(result, row)

        try:
            self.rows[row].append(buttons[0])
        except IndexError:
            self.rows.append(buttons)

    def remove(self,
               row: int,
               col: int,
               mask: str = None):

        if mask is not None:
            mask = SelectionMask.parse(mask)
            col = mask.resolve_index(col)

        return self.rows[row].pop(col)

    def move(self, row: int, to: int = None):
        el = self.rows.pop(row)
        self.add_row(el, to)
        return el


class MarkupScheme:
    def __init__(self,
                 construct: Callable[[DialogMeta, MarkupConstructor],
                                     Awaitable[Optional[bool]]] = None):

        self.construct = construct

    async def apply_construct(self,
                              meta: DialogMeta,
                              rows: list[list[MarkupSchemeButton]]
                              ) -> Optional[list[list[MarkupSchemeButton]]]:

        if self.construct is not None:
            constructor = MarkupConstructor(rows.copy())
            is_actual = await self.construct(meta, constructor)

            if is_actual is False:
                return None
            else:
                rows = constructor.rows

        return rows

    async def get_markup(self,
                         rows: list[list[MarkupSchemeButton]],
                         meta: DialogMeta,
                         markup_type: str) -> Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]]:

        rows = await self.apply_construct(meta, rows)

        if rows is None:
            return None

        if markup_type == MarkupType.TEXT:
            markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True)
        elif markup_type == MarkupType.INLINE:
            markup = InlineKeyboardMarkup()
        else:
            raise KeyError(f'No markup type {markup_type}')

        for i in rows:
            if markup_type == MarkupType.TEXT:
                markup.row(*[KeyboardButton(j.text)
                             for j in i])

            elif markup_type == MarkupType.INLINE:
                markup.row(*[InlineKeyboardButton(j.text,
                                                  callback_data=j.callback_data,
                                                  url=j.url)

                             for j in i])
            else:
                raise RuntimeError()

        return markup
