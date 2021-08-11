from datetime import datetime, timedelta
from typing import Optional

import pytz


_FIRST_CALL = 1


def get_next_call_date_when_call_missed(*, calls_count: int) -> Optional[datetime]:
    if calls_count == _FIRST_CALL:
        return datetime.now(pytz.utc) + timedelta(days=1)
    return None


def get_next_call_date_when_draft() -> datetime:
    next_call = datetime.now(pytz.utc) + timedelta(days=3)
    if next_call.isoweekday() == 7:
        # если попадает на воскресенье, то еще +1 день до понедельника
        next_call += timedelta(days=1)
    elif next_call.isoweekday() == 6:
        # если попадает на субботу, то еще +2 дня до понедельника
        next_call += timedelta(days=2)
    return next_call
