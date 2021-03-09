from datetime import datetime, timedelta
from typing import Optional

import pytz


_FIRST_CALL = 1
_SECOND_CALL = 2


def get_next_call_date_when_call_missed(*, calls_count: int) -> Optional[datetime]:
    if calls_count == _FIRST_CALL:
        return datetime.now(pytz.utc) + timedelta(hours=2)
    if calls_count == _SECOND_CALL:
        return datetime.now(pytz.utc) + timedelta(days=1)
    return None
