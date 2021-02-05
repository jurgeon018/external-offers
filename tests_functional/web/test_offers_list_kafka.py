import asyncio

import pytest
from mock import ANY


async def test_decline_client__client_exist_with_2_offers__expected_1_messages_to_kafka(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': []
    })
    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=1.5,
        count=1
    )

    assert messages[0].data == {
        'managerId': 60024659,
        'sourceUserId': '32131326',
        'date': ANY,
        'timestamp': ANY,
        'userId': None,
        'phone': '+79812333238',
        'status': 'declined',
        'source': 'avito'
    }


async def test_decline_client__client_doesnt_exist__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': []
    })
    operator_user_id = 60024660
    operator_client = 'missing'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_call_missed_client__client_exist_with_2_offers__expected_1_messages_to_kafka(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': []
    })
    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=2.5,
        count=1
    )

    assert messages[0].data == {
        'managerId': 60024659,
        'sourceUserId': '32131326',
        'date': ANY,
        'timestamp': ANY,
        'userId': None,
        'phone': '+79812333238',
        'status': 'callMissed',
        'source': 'avito'
    }


async def test_call_missed_client__client_doesnt_exist__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': []
    })
    operator_user_id = 60024660
    operator_client = 'missing'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_call_missed_client__client_exist_with_2_offers_and_operator_test__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture,
        runtime_settings
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=2.5,
            count=1
        )


async def test_decline_client__client_exist_with_2_offers_and_operator_test__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture,
        runtime_settings
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_call_missed_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001
    })

    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    assert f'Не удалось отправить событие аналитики для клиента {operator_client}' in logs.get()


async def test_decline_client_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001
    })

    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    assert f'Не удалось отправить событие аналитики для клиента {operator_client}' in logs.get()


async def test_call_later_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001
    })

    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    assert f'Не удалось отправить событие аналитики для клиента {operator_client}' in logs.get()


async def test_call_later_client__client_exist_with_2_offers__expected_1_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture,
        runtime_settings
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 1
    })
    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )
    await asyncio.sleep(2)

    # assert
    messages = await kafka_service.get_messages(
        topic='preposition-admin.calls',
    )

    assert any([message.data == {
        'managerId': 60024659,
        'sourceUserId': '32131326',
        'date': ANY,
        'timestamp': ANY,
        'userId': None,
        'phone': '+79812333238',
        'status': 'callLater',
        'source': 'avito'
    } for message in messages])


async def test_call_later_client__client_doesnt_exist__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': []
    })
    operator_user_id = 60024660
    operator_client = 'missing'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_call_later_client__client_exist_with_2_offers_and_operator_test__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture,
        runtime_settings
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    operator_user_id = 60024659
    operator_client = '6'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


async def test_delete_offer__exist_offers_in_progress__client_accepted_message_if_no_offers_in_progress_and_draft(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    operator_user_id = 70024649
    operator_client = '7'
    offer_in_progress = '13'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': offer_in_progress,
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=1.5,
        count=1
    )

    assert messages[0].data == {
        'managerId': 70024649,
        'sourceUserId': '32131327',
        'date': ANY,
        'timestamp': ANY,
        'userId': None,
        'phone': '+79812932338',
        'status': 'accepted',
        'source': 'avito'
    }
