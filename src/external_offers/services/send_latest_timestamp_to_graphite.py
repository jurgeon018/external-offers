from datetime import datetime

import pytz

from external_offers.helpers.graphite import send_to_graphite
from external_offers.repositories.postgresql import get_lastest_event_timestamp


NO_EVENTS_TIMESTAMP = 0


async def send_parsed_offers_timestamp_diff_to_graphite():
    event_timestamp = await get_lastest_event_timestamp() or NO_EVENTS_TIMESTAMP
    if event_timestamp == NO_EVENTS_TIMESTAMP:
        value = (datetime.now(pytz.utc)).total_seconds()
    else:
        value = (datetime.now(pytz.utc) - event_timestamp).total_seconds()
    send_to_graphite(
        key='parsed_offers.seconds_since_last_timestamp',
        value=value,
        timestamp=datetime.now(pytz.utc).timestamp()
    )
