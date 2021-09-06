from datetime import datetime

from cian_helpers.timezone import make_aware

from external_offers.helpers.time import get_aware_date


async def test_get_aware_date():
    date = datetime.now()
    aware_date = make_aware(date)
    assert get_aware_date(None) is None
    assert get_aware_date(aware_date) == aware_date
    assert get_aware_date(date) == aware_date
