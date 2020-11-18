from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


async def test_save_offer__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('POST', '/api/admin/v1/save-offer/', expected_status=400)


async def test_save_offer__correct_json__status_ok(
        pg,
        http,
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
                'location_path': [1],
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


async def test_save_offer__correct_json__offer_status_changed_to_draft(
        pg,
        http,
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
                'location_path': [1],
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
        pg,
        http,
        users_mock,
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
        pg,
        http,
        users_mock,
        monolith_cian_announcementapi_mock,
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
):
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
                'location_path': [1],
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
        pg,
        http,
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
                'location_path': [1],
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
        pg,
        http,
        users_mock,
        monolith_cian_announcementapi_mock,
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
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
                'location_path': [1],
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


async def test_save_offer__no_offers_in_progress_left__client_status_waiting(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        monolith_cian_service_mock,
        offers_and_clients_fixture
):
    # arrange
    client_id = '5'
    user_id = 123123
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute(
        """
        UPDATE offers_for_call SET status='draft' WHERE id='9'
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
        'offerId': '8',
        'clientId': client_id,
        'description': 'Test'
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
                'location_path': [1],
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
    status = await pg.fetchval('SELECT status FROM clients WHERE client_id=$1', client_id)
    assert status == 'waiting'


async def test_save_offer__offers_in_progress_left__client_status_in_progress(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        monolith_cian_service_mock,
        offers_and_clients_fixture
):
    # arrange
    client_id = '5'
    await pg.execute_scripts(offers_and_clients_fixture)
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
        'offerId': '9',
        'clientId': client_id,
        'description': 'Test'
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
                'location_path': [1],
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
    status = await pg.fetchval('SELECT status FROM clients WHERE client_id=$1', client_id)
    assert status == 'inProgress'


async def test_save_offer__offer_with_paid_region__promo_apis_called(
        pg,
        http,
        runtime_settings,
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

    user_id = 123123
    paid_regions = [1, 2]
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
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
    }
    await runtime_settings.set({
        'REGIONS_WITH_PAID_PUBLICATION': paid_regions,
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
                'location_path': [3, 1],
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

    service_stub = await monolith_cian_service_mock.add_stub(
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

    profileapi_stub = await monolith_cian_profileapi_mock.add_stub(
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
    assert len(await service_stub.get_requests()) == 1
    assert len(await profileapi_stub.get_requests()) == 1


async def test_save_offer__offer_with_free_region__promo_apis_not_called(
        http,
        runtime_settings,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock
):
    # arrange
    user_id = 123123
    paid_regions = [1, 2]
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
        'offerId': '3567',
        'clientId': '7',
        'description': 'Test'
    }
    await runtime_settings.set({
        'REGIONS_WITH_PAID_PUBLICATION': paid_regions,
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
                'location_path': [3, 4],
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

    service_stub = await monolith_cian_service_mock.add_stub(
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

    profileapi_stub = await monolith_cian_profileapi_mock.add_stub(
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
    assert len(await service_stub.get_requests()) == 0
    assert len(await profileapi_stub.get_requests()) == 0
