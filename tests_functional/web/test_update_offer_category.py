import json

import pytest
from cian_test_utils import future

from external_offers.entities.save_offer import DealType, OfferType
from external_offers.enums import SaveOfferCategory, SaveOfferTerm
from external_offers.services.save_offer import mapping_offer_params_to_category


async def test_update_offer_category__non_valid_parameters__categories_not_changed(
    http,
    pg,
    offers_and_clients_fixture,
    parsed_offers_fixture,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    offer_id = "1"
    user_id = 1

    # act
    offer_for_call_before_api_call = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE id=$1;
        """,
        [offer_id,]
    )
    parsed_offer_before_api_call = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id=$1;
        """,
        [offer_for_call_before_api_call['parsed_id']]
    )
    response = await http.request(
        'POST',
        '/api/admin/v1/update-offer-category/',
        json={
            'offerId': offer_id,
            # wrong parameters
            'termType': SaveOfferTerm.daily_term.value,
            'categoryType': SaveOfferCategory.land.value,
            'dealType': DealType.sale.value,
            'offerType': OfferType.suburban.value,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    offer_for_call_after_api_call = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE id=$1;
        """,
        [offer_id,]
    )
    parsed_offer_after_api_call = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id=$1;
        """,
        [offer_for_call_after_api_call['parsed_id']]
    )
    body = json.loads(response.body.decode('utf-8'))
    source_object_model_before_api_call = json.loads(parsed_offer_before_api_call['source_object_model'])
    source_object_model_after_api_call = json.loads(parsed_offer_after_api_call['source_object_model'])

    # assert
    assert body['success'] == False
    assert offer_for_call_after_api_call['category'] == offer_for_call_before_api_call['category']
    assert source_object_model_before_api_call['category'] == source_object_model_after_api_call['category']


@pytest.mark.parametrize('offer_params, expected_category', 
    [(k, v) for k, v in mapping_offer_params_to_category.items()]
)
async def test_update_offer_category__valid_parameters__categories_are_changed(
    http,
    runtime_settings,
    pg,
    offers_and_clients_fixture,
    parsed_offers_fixture,
    offer_params,
    expected_category,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    offer_id = "1"
    user_id = 1
    term_type = offer_params[0]
    category_type = offer_params[1].value
    deal_type = offer_params[2].value
    offer_type = offer_params[3].value
    if offer_params[0] is not None:
        term_type = term_type.value
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-offer-category/',
        json={
            'offerId': offer_id,
            'termType': term_type,
            'categoryType': category_type,
            'dealType': deal_type,
            'offerType': offer_type,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    offer_for_call = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE id=$1;
        """,
        [offer_id,]
    )
    parsed_offer = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id=$1;
        """,
        [offer_for_call['parsed_id']]
    )
    source_object_model = json.loads(parsed_offer['source_object_model'])
    body = json.loads(response.body.decode('utf-8'))

    assert body['success'] == True
    assert offer_for_call['category'] == expected_category.value
    assert source_object_model['category'] == expected_category.value
