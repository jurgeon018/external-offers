from datetime import datetime

import pytz

from external_offers.helpers.graphite import send_to_graphite
from external_offers.repositories.postgresql import get_lastest_event_timestamp


async def send_parsed_offers_timestamp_diff_to_graphite():
    event_timestamp = await get_lastest_event_timestamp()
    now = datetime.now(pytz.utc)
    if not event_timestamp:
        value = 0
    else:
        value = int((now - event_timestamp).total_seconds())
    send_to_graphite(
        key='parsed_offers.seconds_since_last_timestamp',
        value=value,
        timestamp=now.timestamp()
    )
