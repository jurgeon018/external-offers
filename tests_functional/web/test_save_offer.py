from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


async def test_save_offer__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('POST', '/api/admin/v1/save-offer/', expected_status=400)


async def test_save_offer__correct_json__status_ok(
    http,
    users_mock,
    monolith_cian_service_mock,
    monolith_cian_announcementapi_mock,
    monolith_cian_profileapi_mock
):
    # arrange
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
        'offerId': '3567',
        'clientId': '7'
    }
    user_id = 123123
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777
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
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
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
            body={
                'id': 1,
                'promocodes': [
                    {
                        'promocode': 'TESTTEST'
                    }
                ]
            }
        ),
    )

    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            body='success'
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'ok'


async def test_save_offer__register_user_by_phone_called_success__realty_user_id_saved(
    http,
    pg,
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
        'offerId': '3567',
        'clientId': client_id
    }
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
            }
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
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    saved_realty_user_id = await pg.fetchval('SELECT realty_user_id FROM clients WHERE client_id=$1', client_id)
    assert saved_realty_user_id == realty_user_id


async def test_save_offer__realty_user_id_exists__register_user_by_phone_not_called(
    http,
    pg,
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
        'offerId': '3567',
        'clientId': client_id
    }
    await pg.execute('UPDATE clients SET realty_user_id=$1 WHERE client_id=$2', [realty_user_id, client_id])

    register_mock = await users_mock.add_stub(
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
            }
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
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert len(await register_mock.get_requests()) == 0


async def test_save_offer__add_draft_called_success__offer_cian_id_saved(
    http,
    pg,
    users_mock,
    monolith_cian_announcementapi_mock,
    monolith_cian_service_mock,
    offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    realty_user_id = 77777
    offer_cian_id = 7777
    client_id = '5'
    offer_id = '8'

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
        'offerId': offer_id,
        'clientId': client_id
    }
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
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'country_id': 1233,
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='POST',
        path='/v2/announcements/draft/',
        response=MockResponse(
            body={
                'realtyObjectId': offer_cian_id,
            }
        ),
    )

    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=400
        )
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    saved_offer_cian_id = await pg.fetchval('SELECT offer_cian_id FROM offers_for_call WHERE id=$1', offer_id)
    assert saved_offer_cian_id == offer_cian_id


async def test_save_offer__offer_cian_id_exists__add_draft_not_called(
    http,
    pg,
    users_mock,
    monolith_cian_announcementapi_mock,
    offers_and_clients_fixture,
    monolith_cian_service_mock
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    realty_user_id = 77777
    offer_cian_id = 7777
    client_id = '5'
    offer_id = '8'
    await pg.execute('UPDATE offers_for_call SET offer_cian_id=$1 WHERE id=$2', [offer_cian_id, offer_id])
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
        'offerId': offer_id,
        'clientId': client_id
    }

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
            }
        ),
    )

    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'country_id': 1233,
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
                'realtyObjectId': offer_cian_id,
            }
        ),
    )

    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=400
        )
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert len(await draft_stub.get_requests()) == 0


async def test_save_offer__correct_json__offer_status_changed_to_draft(
    http,
    pg,
    users_mock,
    monolith_cian_service_mock,
    monolith_cian_announcementapi_mock,
    monolith_cian_profileapi_mock
):
    # arrange
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
            '1',
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
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
        'clientId': '7'
    }
    user_id = 123123
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777
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
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
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
            body={
                'id': 1,
                'promocodes': [
                    {
                        'promocode': 'TESTTEST'
                    }
                ]
            }
        ),
    )

    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            body='success'
        ),
    )
    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    status = await pg.fetchval("""SELECT status FROM offers_for_call WHERE id='1'""")
    assert status == 'draft'


async def test_save_offer__create_user_by_phone_failed__status_registration_failed(
    http,
    users_mock,
):
    # arrange
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
        'offerId': '3567',
        'clientId': '7'
    }
    user_id = 123123
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone',
        response=MockResponse(
            status=400
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'registrationFailed'


async def test_save_offer__geocode_failed__status_geocode_failed(
    http,
    users_mock,
    monolith_cian_announcementapi_mock,
):
    # arrange
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
        'offerId': '3567',
        'clientId': '7'
    }
    user_id = 123123
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777
                }
            }
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
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'geocodeFailed'


async def test_save_offer__create_promo_failed__status_promo_creation_failed(
    http,
    users_mock,
    monolith_cian_service_mock,
    monolith_cian_announcementapi_mock,
):
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
        'offerId': '3567',
        'clientId': '7'
    }
    user_id = 123123

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777
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
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
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
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'promoCreationFailed'


async def test_save_offer__promo_apply_failed__status_promo_activation_failed(
    http,
    users_mock,
    monolith_cian_service_mock,
    monolith_cian_announcementapi_mock,
    monolith_cian_profileapi_mock
):
    # arrange
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
        'offerId': '3567',
        'clientId': '7'
    }
    user_id = 123123
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777
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
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
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
            body={
                'id': 1,
                'promocodes': [
                    {
                        'promocode': 'TESTTEST'
                    }
                ]
            }
        ),
    )

    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            status=400
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'promoActivationFailed'


async def test_save_offer__announcements_draft_failed__status_draft_failed(
    http,
    users_mock,
    monolith_cian_announcementapi_mock,
):
    # arrange
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
        'offerId': '3567',
        'clientId': '7'
    }
    user_id = 123123
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777
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
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='POST',
        path='/v2/announcements/draft/',
        response=MockResponse(
            status=400
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'draftFailed'
