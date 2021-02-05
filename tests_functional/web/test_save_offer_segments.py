import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


@pytest.mark.parametrize(
    ('segment', 'is_by_homeowner'),
    (
        ('c', False),
        ('d', True)
    )
)
async def test_save_offer__smb_segment__is_by_homeowner_false(
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body,
        segment,
        is_by_homeowner
):
    # arrange
    operator_user_id = 123123
    client_id = '1'
    await pg.execute(
        """
        INSERT INTO public.offers_for_call(
            id,
            parsed_id,
            client_id,
            status,
            created_at,
            started_at,
            synced_at
        ) VALUES (
            '1',
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            $1,
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """,
        [
            client_id
        ]
    )
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status,
            segment
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        [client_id, '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress',
         segment]
    )

    save_offer_request_body['clientId'] = client_id

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777,
                    'is_agent': True
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'country_id': 1233,
                'location_path': [1],
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    draft_stub = await monolith_cian_announcementapi_mock.add_stub(
        method='POST',
        path='/v2/announcements/draft/',
        response=MockResponse(
            body={
                'realtyObjectId': 1243433,
            }
        ),
    )

    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=400
        ),
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    request = await draft_stub.get_request()
    request_body = json.loads(request.body)

    assert request_body['model']['isByHomeOwner'] is is_by_homeowner
