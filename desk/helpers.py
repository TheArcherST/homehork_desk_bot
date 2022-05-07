from datetime import time

from .types import ScheduleItem, WeeklyDateTime


def _prepare_time(string: str):
    hour, minute = map(int, string.split(':'))
    return time(hour=hour, minute=minute)


def parse_schedule(string: str):
    """Parse schedule

    fmt:

    0|10:00-14:00|Math
    │   │     │    └ Lesson
    │   │     └ End
    │   └ Start
    └ Number of week day (0-6)

    Example:
        ```txt
        0|10:00-14:00|Math
        0|11:00-13:00|Eng
        1|10:00-14:00|Math
        ```

    """

    result = []

    for i in string.split('\n'):
        day, start_t, end_t, objective = i.split('|')
        start, end = map(_prepare_time, (start_t, end_t))
        day = int(day)

        result.append(ScheduleItem(
            objective=objective,
            start=WeeklyDateTime(day, start),
            end=WeeklyDateTime(day, end)
        ))

    return result
