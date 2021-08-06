import asyncio
from datetime import datetime

import pytest

from tests.utils import load_json_data


@pytest.mark.parametrize('offer', [
    load_json_data(__file__, 'announcement_similar.json')
])
async def test_process_announcement_consumer__similar_save(queue_service, pg, offer):
    # act
    await queue_service.wait_consumer('my-offers.process_announcement_v2')
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow('SELECT * FROM offers_similars_flat ORDER BY offer_id DESC LIMIT 1')

    assert row['offer_id'] == 236954116


@pytest.mark.parametrize('offer', [
    load_json_data(__file__, 'announcement_similar.json')
])
async def test_process_announcement_consumer__similar_update_price(queue_service, pg, offer):
    # arrange
    await pg.execute(
        """
        INSERT INTO public.offers_similars_flat (
            offer_id,
            group_id,
            house_id,
            district_id,
            price,
            rooms_count,
            deal_type,
            sort_date,
            old_price
        )
        VALUES
            ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        [
            236954116,
            None,
            None,
            341,
            4000000.0,
            2,
            'sale',
            datetime(2020, 9, 5),
            None,
        ]
    )

    # act
    await queue_service.wait_consumer('my-offers.process_announcement_v2', timeout=15)
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow('SELECT * FROM offers_similars_flat ORDER BY offer_id DESC LIMIT 1')

    assert row['offer_id'] == 236954116
    assert row['price'] == 4539000.0
    assert row['old_price'] == 4000000.0
