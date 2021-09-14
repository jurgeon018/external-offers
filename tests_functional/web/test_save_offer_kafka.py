from unittest.mock import ANY

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_functional_test_utils.pytest_plugin._kafka import KafkaServiceError


async def test_save_offer__correct_json__expected_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings,
        save_offer_request_body,
        get_old_users_by_phone_mock
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
            synced_at,
            last_call_id
        ) VALUES (
            '1',
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            'ddd86dec-20f5-4a70-bb3a-077b2754df77'
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
        'phone': '+79812333292',
        'callId': 'ddd86dec-20f5-4a70-bb3a-077b2754df77',
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
        runtime_settings,
        save_offer_request_body,
        get_old_users_by_phone_mock
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
    calls_messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=2.5,
        count=1
    )
    assert calls_messages[0].data == {
        'managerId': operator_user_id,
        'sourceUserId': '555bb598767308327e1dffbe7241486c',
        'date': ANY,
        'timestamp': ANY,
        'userId': 7777777,
        'phone': '+79812333292',
        'status': 'accepted',
        'source': 'avito'
    }
    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=1
    )
    assert offers_messages[0].data['offer']['id'] == '1'
    assert offers_messages[0].data['offer']['parsedId'] == 'ddd86dec-20f5-4a70-bb3a-077b2754dfe6'
    assert offers_messages[0].data['offer']['clientId'] == '7'
    assert offers_messages[0].data['offer']['status'] == 'inProgress'
    assert offers_messages[0].data['offer']['createdAt'] == ANY
    assert offers_messages[0].data['offer']['syncedAt'] == ANY
    assert offers_messages[0].data['offer']['startedAt'] == ANY
    assert offers_messages[0].data['offer']['syncedWithKafka'] is False
    assert offers_messages[0].data['offer']['isTest'] is False
    assert offers_messages[0].data['offer']['rowVersion'] == 0


async def test_save_offer__client_with_offers_left__expected_no_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_service_mock,
        monolith_cian_announcementapi_mock,
        monolith_cian_profileapi_mock,
        runtime_settings,
        save_offer_request_body
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
    with pytest.raises(KafkaServiceError):
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
        runtime_settings,
        save_offer_request_body
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
            'X-Real-UserId': test_operator
        }
    )

    # assert
    with pytest.raises(KafkaServiceError):
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
        logs,
        save_offer_request_body,
        get_old_users_by_phone_mock
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
    assert f'Не удалось отправить событие аналитики для объявления {offer_id}' in logs.get()


async def test_save_offer__account_for_draft_changed__expected_message_to_kafka(
        pg,
        http,
        kafka_service,
        users_mock,
        monolith_cian_announcementapi_mock,
        runtime_settings,
        save_offer_request_body
):
    # arrange
    operator_user_id = 60024640
    expected_cian_user_id = 2
    save_offer_request_body['accountForDraft'] = expected_cian_user_id
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 2
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
            synced_at,
            last_call_id
        ) VALUES (
            '1',
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            'ddd86dec-20f5-4a70-bb3a-077b2754df77'
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
            status,
            cian_user_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress', 1]
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
            'X-Real-UserId': operator_user_id
        }
    )

    # assert
    calls_messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=3.5,
        count=1
    )

    assert calls_messages[0].data['userId'] == expected_cian_user_id
    assert calls_messages[0].data['status'] == 'mainAccountChanged'

    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=3.5,
        count=1
    )
    assert offers_messages[0].data['offer']['id'] == '1'
    assert offers_messages[0].data['offer']['parsedId'] == 'ddd86dec-20f5-4a70-bb3a-077b2754dfe6'
    assert offers_messages[0].data['offer']['clientId'] == '7'
    assert offers_messages[0].data['offer']['status'] == 'inProgress'
    assert offers_messages[0].data['offer']['createdAt'] == '2020-10-12T04:05:06+00:00'
    assert offers_messages[0].data['offer']['syncedAt'] == '2020-10-12T04:05:06+00:00'
    assert offers_messages[0].data['offer']['lastCallId'] == 'ddd86dec-20f5-4a70-bb3a-077b2754df77'
    assert offers_messages[0].data['offer']['startedAt'] == '2020-10-12T04:05:06+00:00'
    assert offers_messages[0].data['offer']['syncedWithKafka'] is False
    assert offers_messages[0].data['offer']['isTest'] is False
    assert offers_messages[0].data['offer']['rowVersion'] == 0
