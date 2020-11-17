import json
from asyncio import gather

from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_save_offer__multiple_save_offer_requests__second_returns_already_processing(
        http,
        pg,
        runtime_settings,
        users_mock,
        monolith_cian_announcementapi_mock,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    realty_user_id = 77777
    client_id = '5'

    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': 'room',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False,
        'offerId': '1',
        'clientId': client_id,
        'description': 'Test'
    }
    await runtime_settings.set({
        'USERS_TIMEOUT': 10000
    })
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': realty_user_id
                }
            },
            wait=1000
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            status=400
        ),
    )

    # act
    responses = await gather(
        http.request(
            'POST',
            '/api/admin/v1/save-offer/',
            json=request,
            headers={
                'X-Real-UserId': user_id
            }
        ),
        http.request(
            'POST',
            '/api/admin/v1/save-offer/',
            json=request,
            headers={
                'X-Real-UserId': user_id
            }
        )
    )

    # assert
    assert any([json.loads(response.body)['status'] == 'alreadyProcessing' for response in responses])
