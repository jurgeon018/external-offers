from datetime import datetime, timedelta

import pytz
from freezegun import freeze_time

from external_offers.utils import get_next_call_date_when_call_missed


def test_get_next_call_date_when_call_missed__first_call__returns_2_hours_later():
    # arrange
    calls_count = 1
    now = datetime.now(pytz.utc)

    # act
    with freeze_time(now):
        next_call = get_next_call_date_when_call_missed(
            calls_count=calls_count
        )

    # assert
    assert next_call == now + timedelta(hours=2)


def test_get_next_call_date_when_call_missed__second_call__returns_1_day_later():
    # arrange
    calls_count = 2
    now = datetime.now(pytz.utc)

    # act
    with freeze_time(now):
        next_call = get_next_call_date_when_call_missed(
            calls_count=calls_count
        )

    # assert
    assert next_call == now + timedelta(days=1)


def test_get_next_call_date_when_call_missed__third_call__returns_no_date():
    # arrange
    calls_count = 3

    # act
    next_call = get_next_call_date_when_call_missed(
        calls_count=calls_count
    )

    # assert
    assert next_call is None
