from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_parsed_offer_object_model_by_offer_id():
    # arrange
    offer_id = '1'

    # act
    pg.get().fetchrow.return_value = future(None)
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
