from typing import Optional, Callable, Awaitable
from datetime import datetime, timedelta, timezone, timedelta

from desk.helpers import parse_schedule

from aiogram_keyboards import Keyboard, DialogMeta, Button
from aiogram_keyboards.core.markup_scheme import MarkupConstructor, MarkupSchemeButton
from aiogram_keyboards.core.dialog_context import DialogContext


from ..config import desk_api


class Node(Keyboard[False], DialogContext):
    __markup_scope__ = 'c'

    desk_id: int


WEEKDAY_TRANSLATE_LIB = {
    0: 'ПН',
    1: 'ВТ',
    2: 'СР',
    3: 'ЧТ',
    4: 'ПТ',
    5: 'СБ',
    6: 'ВС',
}


class Commands(Node):
    __ignore_state__ = True
    __state__ = '*'

    start = Button('/start')
    reset = Button('/reset')


@Commands.start.handle()
async def start_handler(o):
    meta = DialogMeta(o)

    async with Node(meta) as ctx:
        if ctx.desk_id is None:
            await DeskBuilder.process(o)
        else:
            await ProcessDesk.process(o)


@Commands.reset.handle()
async def reset_handler(o):
    meta = DialogMeta(o)
    await meta.fsm_context.reset_data()


class DeskBuilder(Node):
    __global__ = True
    __text__ = ('Введите расписание.\n\n'
                'Формат: <code>day|hh:mm|hh:mm|objective</code>')

    async def handler(self, meta: DialogMeta) -> None:
        string = meta.content
        try:
            schedule = parse_schedule(string)
        except ValueError:
            return await meta.source.answer('Что-то не так! Попробуйте изменить отправить снова')

        self.desk_id = desk_api.new_desk(schedule)

        await self._save()
        await ProcessDesk.process(meta)


class ProcessDesk(Node):
    add = Button('➕')

    async def __text__(self, meta: DialogMeta) -> str:
        await self.__aenter__(meta)  # TODO: fix it

        text = f'<b>Доска {self.desk_id}</b>\n\n'

        lessons = desk_api.get_lesson_ids(self.desk_id)
        lesson_number = 1
        weekday_cache = 0
        for i in lessons:
            lesson = desk_api.get_lesson(i)

            if lesson.start.week_day != weekday_cache:
                weekday_cache = lesson.start.week_day
                lesson_number = 1
            else:
                lesson_number += 1

            tasks_text = "\n".join(i.content for i in lesson.tasks)
            week_d = WEEKDAY_TRANSLATE_LIB[lesson.start.to_datetime().weekday()]
            if tasks_text:
                text += (f'<b>{week_d} {lesson.objective} - {lesson_number}</b>\n'
                         f'<code>{tasks_text}</code>\n\n')

        return text


@ProcessDesk.add.handle()
async def add_handler(m):
    meta = DialogMeta(m)
    await ChooseTheme.process(meta)


class ChooseTheme(Node):
    __global__ = True
    __text__ = 'Введи задание'

    async def handler(self, meta: DialogMeta) -> None:
        description = meta.content
        dt = datetime.now(tz=timezone(timedelta(hours=3)))
        current_lesson = desk_api.predict_lesson(self.desk_id, dt)
        next_lesson = desk_api.get_lessons_generator(self.desk_id, current_lesson).__next__()
        desk_api.add_task(self.desk_id, next_lesson.id, description)

        await meta.source.delete()
        meta.active_message_id -= 1
        await ProcessDesk.process(meta)
