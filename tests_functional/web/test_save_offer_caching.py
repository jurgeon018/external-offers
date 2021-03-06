from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_save_offer__register_user_by_phone_called_success__cian_user_id_saved(
        http,
        pg,
        users_mock,
        runtime_settings,
        monolith_cian_announcementapi_mock,
        offers_and_clients_fixture,
        save_offer_request_body,
        get_old_users_by_phone_mock
):
    # arrange
    await runtime_settings.set({
        'RECENTLY_REGISTRATION_CHECK_DELAY': 120
    })
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    cian_user_id = 77777
    client_id = '5'
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
                    'id': cian_user_id,
                    'isAgent': True
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    saved_cian_user_id = await pg.fetchval('SELECT cian_user_id FROM clients WHERE client_id=$1', client_id)
    assert saved_cian_user_id == cian_user_id


async def test_save_offer__cian_user_id_exists__register_user_by_phone_not_called(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        offers_and_clients_fixture,
        save_offer_request_body
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    cian_user_id = 77777
    client_id = '5'
    save_offer_request_body['clientId'] = client_id
    await pg.execute('UPDATE clients SET cian_user_id=$1 WHERE client_id=$2', [cian_user_id, client_id])

    register_mock = await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': cian_user_id,
                    'isAgent': True
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
        json=save_offer_request_body,
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
        runtime_settings,
        monolith_cian_announcementapi_mock,
        monolith_cian_service_mock,
        offers_and_clients_fixture,
        save_offer_request_body,
        get_old_users_by_phone_mock
):
    # arrange
    await runtime_settings.set({
        'RECENTLY_REGISTRATION_CHECK_DELAY': 120
    })
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    cian_user_id = 77777
    offer_cian_id = 7777
    client_id = '5'
    offer_id = '8'

    save_offer_request_body['clientId'] = client_id
    save_offer_request_body['offerId'] = offer_id

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': cian_user_id,
                    'isAgent': True
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
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
        json=save_offer_request_body,
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
        monolith_cian_service_mock,
        save_offer_request_body
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    cian_user_id = 77777
    offer_cian_id = 7777
    client_id = '5'
    offer_id = '8'
    await pg.execute('UPDATE offers_for_call SET offer_cian_id=$1 WHERE id=$2', [offer_cian_id, offer_id])
    save_offer_request_body['clientId'] = client_id
    save_offer_request_body['offerId'] = offer_id

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': cian_user_id,
                    'isAgent': True
                }
            }
        ),
    )

    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert len(await draft_stub.get_requests()) == 0


async def test_save_offer__create_promo_called_success__promocode_saved(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_service_mock,
        offers_and_clients_fixture,
        monolith_cian_profileapi_mock,
        save_offer_request_body,
        get_old_users_by_phone_mock
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    cian_user_id = 77777
    offer_cian_id = 7777
    client_id = '5'
    offer_id = '8'
    promocode = 'TESTTEST'

    save_offer_request_body['clientId'] = client_id
    save_offer_request_body['offerId'] = offer_id

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': cian_user_id,
                    'isAgent': True
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
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
            body={
                'id': 1,
                'promocodes': [
                    {
                        'promocode': promocode
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
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    saved_promocode = await pg.fetchval('SELECT promocode FROM offers_for_call WHERE id=$1', offer_id)
    assert saved_promocode == promocode


async def test_save_offer__promocode_exists__promo_apis_not_called(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        offers_and_clients_fixture,
        monolith_cian_service_mock,
        monolith_cian_profileapi_mock,
        save_offer_request_body
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    user_id = 123123
    cian_user_id = 77777
    offer_cian_id = 7777
    client_id = '5'
    offer_id = '8'
    promocode = 'TESTTEST'

    await pg.execute('UPDATE offers_for_call SET promocode=$1 WHERE id=$2', [promocode, offer_id])

    save_offer_request_body['clientId'] = client_id
    save_offer_request_body['offerId'] = offer_id

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': cian_user_id,
                    'isAgent': True
                }
            }
        ),
    )

    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
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

    create_promo_stub = await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            body={
                'id': 1,
                'promocodes': [
                    {
                        'promocode': promocode
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
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert len(await create_promo_stub.get_requests()) == 0
