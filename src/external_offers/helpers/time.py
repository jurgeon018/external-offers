from datetime import datetime
from typing import Optional

from cian_helpers.timezone import is_aware, make_aware


def get_aware_date(date: Optional[datetime]) -> Optional[datetime]:
    if not date:
        return None

    if is_aware(date):
        return date

    return make_aware(date)
