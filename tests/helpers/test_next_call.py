from datetime import datetime

import pytest
from freezegun import freeze_time

from external_offers.utils.next_call import get_next_call_date_when_draft


monday_1 = datetime.strptime('2021-08-16', '%Y-%m-%d')
tuesday_1 = datetime.strptime('2021-08-17', '%Y-%m-%d')
wednesday_1 = datetime.strptime('2021-08-18', '%Y-%m-%d')
thursday_1 = datetime.strptime('2021-08-19', '%Y-%m-%d')
friday_1 = datetime.strptime('2021-08-20', '%Y-%m-%d')
saturday_1 = datetime.strptime('2021-08-21', '%Y-%m-%d')
sunday_1 = datetime.strptime('2021-08-22', '%Y-%m-%d')
monday_2 = datetime.strptime('2021-08-23', '%Y-%m-%d')
tuesday_2 = datetime.strptime('2021-08-24', '%Y-%m-%d')
wednesday_2 = datetime.strptime('2021-08-25', '%Y-%m-%d')
thursday_2 = datetime.strptime('2021-08-26', '%Y-%m-%d')
friday_2 = datetime.strptime('2021-08-27', '%Y-%m-%d')
saturday_2 = datetime.strptime('2021-08-28', '%Y-%m-%d')
sunday_2 = datetime.strptime('2021-08-29', '%Y-%m-%d')


@pytest.mark.parametrize('today, expected_next_call_day', [
    (monday_1, thursday_1),
    (tuesday_1, friday_1),
    (wednesday_1, monday_2),
    (thursday_1, monday_2),
    (friday_1, monday_2),
    (saturday_1, tuesday_2),
    (sunday_1, wednesday_2),
    (monday_2, thursday_2),
    (tuesday_2, friday_2),
])
async def test_get_next_call_date_when_draft(
    today,
    expected_next_call_day,
):
    with freeze_time(today):
        assert get_next_call_date_when_draft().date() == expected_next_call_day.date()
