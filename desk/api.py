import sys
from typing import Union, Iterable, TypeVar

from datetime import datetime, time
from itertools import cycle, chain, islice

from sqlalchemy import case, select, cast, DATETIME, func

from . import models, types
from .models import Session


# TODO: make api async


_T = TypeVar('_T')


def rebuild_sequence(sequence: Iterable[_T], first_index: int) -> Iterable[_T]:
    """ Rebuild sequence according to new first element """

    return chain(islice(sequence, first_index, sys.maxsize),
                 islice(sequence, first_index))


class DeskAPI:
    """ Desk API. """

    # TODO: make it as api service and add auth by access token

    def __init__(self):
        pass

    @staticmethod
    def new_desk(schedule: list[types.ScheduleItem]) -> int:
        """ Create new desk """

        with Session() as session:
            desk = models.Desk()
            session.add(desk)
            session.commit()

            desk_id = int(desk.id)

            objects = [
                models.ScheduleItem(objective=i.objective,
                                    start=i.start.to_datetime(),
                                    end=i.end.to_datetime(),
                                    desk_id=desk_id)

                for i in schedule]

            session.bulk_save_objects(objects)
            session.commit()

        return desk_id

    # TODO: make method to edit desk schedule

    @staticmethod
    def remove_desk(desk_id):
        """ Remove desk

        Removes desk and all meta information about she.

        """

        with Session() as session:
            session.query(models.Desk).filter(id=desk_id).delete()
            session.query(models.Task).filter(desk_id=desk_id).delete()
            session.query(models.ScheduleItem).filter(desk_id=desk_id).delete()
            session.commit()

    def add_task(self, desk_id: int, lesson: Union[int, types.WeeklyDateTime], content: str) -> int:
        """Add task to desk into selected lesson

        You can provide lesson mention as it's id or as current datetime,
        skipping step of converting datetime to task_id via predict_lesson.

        """

        if isinstance(lesson, types.WeeklyDateTime):
            lesson = self.predict_lesson(desk_id, lesson)

        with Session() as session:
            task = models.Task(
                desk_id=desk_id,
                lesson_id=lesson,
                content=content
            )
            session.add(task)
            session.commit()
            task_id = int(task.id)

        return task_id

    @staticmethod
    def remove_task(task_id: int):
        """ Remove task method """

        with Session() as session:
            session.query(models.Task).filter(task_id=task_id).remove()
            session.commit()

    @staticmethod
    def predict_lesson(desk_id: int, dt: Union[types.WeeklyDateTime, datetime]) -> int:
        """Predict lesson method

        Predicts lesson by current WeeklyDateTime. Prediction is processing
        by provided schedule.

        """

        if isinstance(dt, datetime):
            dt = types.WeeklyDateTime.from_datetime(dt)

        dt = dt.to_datetime()
        with Session() as session:
            lessons = (session.query(models.ScheduleItem)
                       .filter_by(desk_id=desk_id)
                       .filter(models.ScheduleItem.start <= cast(dt, DATETIME))
                       .order_by(cast(dt, DATETIME) - models.ScheduleItem.end))

            lesson = lessons.first()

            result = int(lesson.id)

        return result

    @staticmethod
    def get_lesson(lesson_id: int) -> types.Lesson:
        with Session() as session:
            schedule_item = session.get(models.ScheduleItem, lesson_id)
            tasks = session.query(models.Task).filter_by(lesson_id=lesson_id).all()

            result = types.Lesson(objective=schedule_item.objective,
                                  start=types.WeeklyDateTime.from_datetime(schedule_item.start),
                                  end=types.WeeklyDateTime.from_datetime(schedule_item.end),
                                  tasks=[
                                      types.Task(content=i.content)
                                      for i in tasks
                                  ],
                                  id=schedule_item.id)

        return result

    @classmethod
    def get_lessons_generator(cls,
                              desk_id: int,
                              first_lesson_id: int):

        """Get objectives generator

        Note: please, remove generator at and of fetching.

        """

        with Session() as session:
            first_schedule_item = session.get(models.ScheduleItem, first_lesson_id)
            target_objective = first_schedule_item.objective

            order_query = (
                session.query(
                    models.ScheduleItem.id,
                    func.row_number().over(order_by=models.ScheduleItem.start).label('num')
                )
                .filter_by(desk_id=desk_id,
                           objective=target_objective)
            )

            target_lesson = order_query.filter_by(id=first_lesson_id).one()
            ids = [i.id for i in order_query.all()]
            result_ids = rebuild_sequence(
                ids,
                ids.index(target_lesson.id) + 1,  # offset 1 to ignore lesson passed into function
            )

        for lesson_id in cycle(result_ids):
            with Session():
                yield cls.get_lesson(lesson_id)

    @staticmethod
    def get_lesson_ids(desk_id: int, weekday: int = None) -> list[int]:
        with Session() as session:
            query = (session.query(models.ScheduleItem.id)
                     .filter_by(desk_id=desk_id))

            if weekday:
                query = query.filter_by(func.day(weekday+1))

            result = map(lambda x: x[0], query.all())

        return list(result)
