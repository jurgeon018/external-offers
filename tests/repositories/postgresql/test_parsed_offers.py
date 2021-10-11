from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_parsed_offer_object_model_by_offer_id():
    # arrange
    offer_id = '1'
    pg.get().fetchrow.return_value = future(None)

    # act
    await postgresql.get_parsed_offer_object_model_by_offer_id(
        offer_id=offer_id
    )

    # assert
    pg.get().fetchrow.assert_called_with(
        'SELECT parsed_offers_1.source_object_model \nFROM'
        ' parsed_offers AS parsed_offers_1 JOIN offers_for_call AS offers_for_call_1 ON parsed_'
        'offers_1.id = offers_for_call_1.parsed_id '
        '\nWHERE offers_for_call_1.id = $1',
        offer_id
    )


async def test_get_lastest_event_timestamp():
    # arrange
    pg.get().fetchval.return_value = future(None)

    # act
    await postgresql.get_lastest_event_timestamp()

    # assert
    pg.get().fetchval.assert_called_with(
        'SELECT max(parsed_offers_1.timestamp) AS max_1 \n'
        'FROM parsed_offers AS parsed_offers_1 \n'
        'WHERE parsed_offers_1.external_offer_type IS NOT $1 AND parsed_offers_1.is_test IS false \n '
        'LIMIT $2',
        'commercial',
        1
    )
