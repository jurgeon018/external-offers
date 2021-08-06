import asyncio
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
import pytz
from cian_json import json
from cian_functional_test_utils.data_fixtures import load_json_data


@pytest.mark.parametrize('offer_archive', [
    load_json_data(__file__, 'announcement_archive.json')
])
async def test(
    queue_service,
    pg,
    offer_archive,
):
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await asyncio.sleep(2)
    await queue_service.publish('announcement_reporting.change', offer_archive, exchange='announcements')
    await asyncio.sleep(1)

    # # assert
    rows = await pg.fetch('SELECT * FROM offers_for_call')
    for row in rows:
        print(row)
        # assert row['row_version'] == 1
