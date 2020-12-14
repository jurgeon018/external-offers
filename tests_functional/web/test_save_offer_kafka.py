from unittest.mock import ANY

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_save_offer__correct_json__expected_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings
):
    # arrange
    operator_user_id = 60024640
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
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
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress']
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
                    'is_agent': True,
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
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.draft-announcements',
        timeout=1.5,
        count=1
    )

    assert messages[0].data == {
        'managerId': operator_user_id,
        'sourceUserId': '555bb598767308327e1dffbe7241486c',
        'date': ANY,
        'timestamp': ANY,
        'userId': 7777777,
        'phone': '+79134488338',
        'draft': 1243433
    }


async def test_save_offer__client_with_no_offers_left__expected_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings
):
    # arrange
    operator_user_id = 60024640

    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
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
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress']
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
                    'is_agent': True,
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
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=1.5,
        count=1
    )

    assert messages[0].data == {
        'managerId': operator_user_id,
        'sourceUserId': '555bb598767308327e1dffbe7241486c',
        'date': ANY,
        'timestamp': ANY,
        'userId': 7777777,
        'phone': '+79812333292',
        'status': 'accepted',
        'source': 'avito'
    }


async def test_save_offer__client_with_offers_left__expected_no_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings
):
    # arrange
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
    })

    operator_user_id = 60024640

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
            ), (
            '2',
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe7',
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
         ['+79812333292'], 'nemoy@gmail.com', operator_user_id, 'inProgress']
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
                    'is_agent': True,
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
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_save_offer__correct_json_test_operator__expected_no_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings
):
    # arrange
    test_operator = 60024640
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [test_operator],
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
         ['+79812333292'], 'nemoy@gmail.com', test_operator, 'inProgress']
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
                    'is_agent': True,
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
            'X-Real-UserId': test_operator
        }
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_save_offer__kafka_publish_timeout__expected_log_warning(
        pg,
        http,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings,
        logs
):
    # arrange
    operator_user_id = 60024640
    offer_id = '1'
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001
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
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress']
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
                    'is_agent': True,
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
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    assert f'Не удалось отправить событие аналитики для объявления {offer_id}' in logs.get()
