import pytest
from mock import ANY


async def test_decline_client__client_exist_with_2_offers__expected_1_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
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
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
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
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
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
        'status': 'callMissed',
        'source': 'avito'
    }


async def test_call_missed_client__client_doesnt_exist__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
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
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    await pg.execute_scripts(offers_and_clients_fixture)
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
            timeout=1.5,
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
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    await pg.execute_scripts(offers_and_clients_fixture)
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
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 0.001
    })
    await pg.execute_scripts(offers_and_clients_fixture)
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
    any([f'Не удалось отправить событие аналитики для клиента {operator_client}' in line
         for line in logs.get_lines()])


async def test_decline_client_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 0.001
    })
    await pg.execute_scripts(offers_and_clients_fixture)
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
    any([f'Не удалось отправить событие аналитики для клиента {operator_client}' in line
         for line in logs.get_lines()])


async def test_call_later_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 0.001
    })
    await pg.execute_scripts(offers_and_clients_fixture)
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
    any([f'Не удалось отправить событие аналитики для клиента {operator_client}' in line
         for line in logs.get_lines()])



async def test_call_later_client__client_exist_with_2_offers__expected_1_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
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
        'status': 'callLater',
        'source': 'avito'
    }


async def test_call_later_client__client_doesnt_exist__expected_0_messages_to_kafka(
        pg,
        http,
        kafka_service,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
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
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    await pg.execute_scripts(offers_and_clients_fixture)
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
