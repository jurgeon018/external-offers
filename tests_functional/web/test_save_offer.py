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
        monolith_cian_profileapi_mock,
        save_offer_request_body
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
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        [client_id, '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress']
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'ok'

    offers_event_log = await pg.fetch('SELECT * FROM event_log where operator_user_id=$1', [operator_user_id])
    assert offers_event_log[0]['status'] == 'draft'
    assert offers_event_log[0]['offer_id'] == '1'


async def test_save_offer__correct_json__offer_status_changed_to_draft(
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        save_offer_request_body
):
    # arrange
    operator_user_id = 12345
    offer_id = '1'
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
        """, [
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
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        [client_id, '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress']
    )

    save_offer_request_body['offerId'] = offer_id
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
                    'isAgent': True,
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    status = await pg.fetchval(f"""SELECT status FROM offers_for_call WHERE id='{offer_id}'""")
    assert status == 'draft'


async def test_save_offer__create_user_by_phone_failed__status_registration_failed(
        pg,
        http,
        users_mock,
        save_offer_request_body
):
    # arrange
    user_id = 123123

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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

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
        json=save_offer_request_body,
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
        save_offer_request_body,
):
    # arrange
    user_id = 123123

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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            cian_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', user_id, 7, 'inProgress']
    )

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
                    'isAgent': True,
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'geocodeFailed'


async def test_save_offer__create_new_account_passed__cian_user_id_overwritten(
        pg,
        http,
        users_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body,
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
    new_cian_user_id = 7777777

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            cian_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', user_id, 7, 'inProgress']
    )

    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': new_cian_user_id,
                    'isAgent': True,
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
    save_offer_request_body['createNewAccount'] = True

    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    cian_user_id = await pg.fetchval(
        """
        SELECT cian_user_id FROM clients WHERE client_id=$1
        """,
        ['7']
    )

    # assert
    assert cian_user_id == new_cian_user_id


async def test_save_offer__account_for_draft_passed__cian_user_id_overwritten(
        pg,
        http,
        users_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body,
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
    new_cian_user_id = 7777777

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            cian_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', user_id, 7, 'inProgress']
    )

    register_stub = await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            status=400
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            status=400
        ),
    )
    save_offer_request_body['accountForDraft'] = new_cian_user_id

    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    cian_user_id = await pg.fetchval(
        """
        SELECT cian_user_id FROM clients WHERE client_id=$1
        """,
        ['7']
    )

    # assert
    assert not await register_stub.get_requests()
    assert cian_user_id == new_cian_user_id


async def test_save_offer__geocode_timeout__logged_timeout(
        pg,
        http,
        logs,
        runtime_settings,
        users_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body,
):
    # arrange
    user_id = 123123

    await runtime_settings.set({
        'MONOLITH_CIAN_ANNOUNCEMENTAPI_TIMEOUT': 1
    })
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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

    address = 'ул. просторная 6, квартира 200'
    offer_id = '1'
    save_offer_request_body['address'] = address
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
                    'id': 7777777,
                    'isAgent': True,
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            status=400,
            wait=1500
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
    assert any([f'Таймаут при обработке переданного адреса "{address}" для объявления {offer_id}' in line
                for line in logs.get_lines()])


async def test_save_offer__create_promo_failed__status_promo_creation_failed(
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body
):
    user_id = 123123

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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

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
                    'isAgent': True,
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
        json=save_offer_request_body,
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
        monolith_cian_profileapi_mock,
        save_offer_request_body
):
    # arrange
    user_id = 123123

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
            '7',
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
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
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

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
                    'isAgent': True,
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
        json=save_offer_request_body,
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
        save_offer_request_body,
):
    # arrange
    user_id = 123123

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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

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
                    'isAgent': True,
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
            status=400
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'draftFailed'


async def test_save_offer__announcements_draft_timeout__logged_timeout(
        pg,
        http,
        logs,
        runtime_settings,
        users_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body,
):
    # arrange
    await runtime_settings.set({
        'MONOLITH_CIAN_ANNOUNCEMENTAPI_TIMEOUT': 1
    })
    user_id = 123123

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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

    offer_id = '1'
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
                    'id': 7777777,
                    'isAgent': True,
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
            status=400,
            wait=1500
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
    assert any([f'Таймаут при создании черновика для объявления {offer_id}' in line
                for line in logs.get_lines()])


async def test_save_offer__no_offers_in_progress_left__client_status_accepted(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        monolith_cian_service_mock,
        offers_and_clients_fixture,
        save_offer_request_body,
):
    # arrange
    client_id = '5'
    offer_id = '8'
    user_id = 123123
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute(
        """
        UPDATE offers_for_call SET status='draft' WHERE id='9'
        """
    )
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
                    'id': 7777777,
                    'isAgent': True,
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    status = await pg.fetchval('SELECT status FROM clients WHERE client_id=$1', client_id)
    assert status == 'accepted'


async def test_save_offer__offers_in_progress_left__client_status_in_progress(
        http,
        pg,
        users_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        monolith_cian_service_mock,
        offers_and_clients_fixture,
        save_offer_request_body,
):
    # arrange
    client_id = '5'
    await pg.execute_scripts(offers_and_clients_fixture)
    save_offer_request_body['clientId'] = client_id
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
                    'id': 7777777,
                    'isAgent': True,
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
        json=save_offer_request_body,
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
        monolith_cian_profileapi_mock,
        save_offer_request_body
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
            $1,
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '1',
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
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['1', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress']
    )
    paid_regions = [1, 2]
    save_offer_request_body['clientId'] = client_id

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
                    'id': 7777777,
                    'isAgent': True,
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
                'locationPath': [3, 1],
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': operator_user_id
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
        monolith_cian_profileapi_mock,
        save_offer_request_body,
):
    # arrange
    user_id = 123123
    paid_regions = [1, 2]

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
                    'id': 7777777,
                    'isAgent': True,
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
                'locationPath': [3, 4],
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
        json=save_offer_request_body,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert len(await service_stub.get_requests()) == 0
    assert len(await profileapi_stub.get_requests()) == 0


async def test_save_offer__save_already_saved_offer__returns_already_processed(
        http,
        pg,
        save_offer_request_body,
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
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )

    user_id = 123123
    client_id = '5'

    save_offer_request_body['clientId'] = client_id
    # act
    response = await http.request(
            'POST',
            '/api/admin/v1/save-offer/',
            json=save_offer_request_body,
            headers={
                'X-Real-UserId': user_id
            }
        )

    # assert
    assert json.loads(response.body)['status'] == 'alreadyProcessed'


async def test_save_offer__save_missing_offer__returns_error(
        http,
        pg,
        save_offer_request_body,
):
    # arrange
    user_id = 123123

    save_offer_request_body['offerId'] = 'missing'

    # act
    response = await http.request(
            'POST',
            '/api/admin/v1/save-offer/',
            json=save_offer_request_body,
            headers={
                'X-Real-UserId': user_id
            }
        )

    # assert
    assert json.loads(response.body)['status'] == 'missingOffer'


async def test_save_offer__create_promo_failed_with_create_new_account__second_call_registration_not_called(
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        save_offer_request_body_with_create_new_account
):
    user_id = 123123

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

    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

    stub = await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': 7777777,
                    'isAgent': True,
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
        json=save_offer_request_body_with_create_new_account,
        headers={
            'X-Real-UserId': user_id
        }
    )

    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body_with_create_new_account,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    requests = await stub.get_requests()
    assert len(requests) == 1


async def test_save_offer__suburban__status_ok(
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        save_offer_request_body_for_suburban
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
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        [client_id, '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress']
    )

    save_offer_request_body_for_suburban['clientId'] = client_id

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
        json=save_offer_request_body_for_suburban,
        headers={
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'ok'

    offers_event_log = await pg.fetch('SELECT * FROM event_log where operator_user_id=$1', [operator_user_id])
    assert offers_event_log[0]['status'] == 'draft'
    assert offers_event_log[0]['offer_id'] == '1'
