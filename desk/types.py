from typing import overload
from dataclasses import dataclass

from datetime import time, datetime


@dataclass
class WeeklyDateTime:
    week_day: int
    time: time

    @classmethod
    def from_datetime(cls, o: datetime) -> 'WeeklyDateTime':
        result = cls(
            week_day=o.weekday(),
            time=o.time()
        )
        return result

    def to_datetime(self):
        result = datetime(
            year=1,
            month=1,
            day=self.week_day+1,
            hour=self.time.hour,
            minute=self.time.minute,
            second=self.time.second,
            microsecond=self.time.microsecond,
        )
        return result


@dataclass
class ScheduleItem:
    objective: str
    start: WeeklyDateTime
    end: WeeklyDateTime


@dataclass
class Task:
    content: str


@dataclass
class Lesson(ScheduleItem):
    tasks: list[Task]
    id: int
