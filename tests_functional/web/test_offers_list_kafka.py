import asyncio
from datetime import datetime

import pytest
import pytz
from cian_functional_test_utils.pytest_plugin._kafka import KafkaServiceError
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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    calls_messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=2.5,
        count=1
    )

    assert calls_messages[0].data == {
        'managerId': 60024659,
        'sourceUserId': '32131326',
        'date': ANY,
        'timestamp': ANY,
        'phone': '+79812333238',
        'callId': '2dddd3b8-3157-47cc-b50a-419052da6197',
        'status': 'declined',
        'source': 'avito'
    }

    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=1
    )
    assert offers_messages[0].data['offer']['id'] == '12'
    assert offers_messages[0].data['offer']['parsedId'] == '3dddd3b8-3257345cc-b50a-419052da619f'
    assert offers_messages[0].data['offer']['clientId'] == '6'
    assert offers_messages[0].data['offer']['status'] == 'declined'
    assert offers_messages[0].data['offer']['priority'] == 1
    assert offers_messages[0].data['offer']['lastCallId'] == '2dddd3b8-3157-47cc-b50a-419052da6197'
    assert offers_messages[0].data['offer']['syncedWithKafka'] is False
    assert offers_messages[0].data['offer']['isTest'] is False
    assert offers_messages[0].data['offer']['rowVersion'] == 0


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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(KafkaServiceError):
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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    calls_messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=2.5,
        count=1
    )

    assert calls_messages[0].data == {
        'managerId': 60024659,
        'sourceUserId': '32131326',
        'date': ANY,
        'timestamp': ANY,
        'phone': '+79812333238',
        'callId': '2dddd3b8-3157-47cc-b50a-419052da6197',
        'status': 'callMissed',
        'source': 'avito'
    }

    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=1
    )
    assert offers_messages[0].data['offer']['id'] == '12'
    assert offers_messages[0].data['offer']['parsedId'] == '3dddd3b8-3257345cc-b50a-419052da619f'
    assert offers_messages[0].data['offer']['clientId'] == '6'
    assert offers_messages[0].data['offer']['status'] == 'callMissed'
    assert offers_messages[0].data['offer']['priority'] == 200000
    assert offers_messages[0].data['offer']['lastCallId'] == '2dddd3b8-3157-47cc-b50a-419052da6197'
    assert offers_messages[0].data['offer']['syncedWithKafka'] is False
    assert offers_messages[0].data['offer']['isTest'] is False
    assert offers_messages[0].data['offer']['rowVersion'] == 0


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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(KafkaServiceError):
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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(KafkaServiceError):
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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    with pytest.raises(KafkaServiceError):
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
    offer_id = 1
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001,
        'OFFERS_FOR_CALL_CHANGE_KAFKA_TIMEOUT': 0.001,
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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    assert f'???? ?????????????? ?????????????????? ?????????????? ?????????????????? ???????????? ?????? ?????????????? {operator_client}' in logs.get()
    assert f'???? ?????????????? ?????????????????? ?????????????? ?????? ?????????????? {offer_id}' in logs.get()


async def test_decline_client_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    offer_id = 1
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001,
        'OFFERS_FOR_CALL_CHANGE_KAFKA_TIMEOUT': 0.001,
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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    assert f'???? ?????????????? ?????????????????? ?????????????? ?????????????????? ???????????? ?????? ?????????????? {operator_client}' in logs.get()
    assert f'???? ?????????????? ?????????????????? ?????????????? ?????? ?????????????? {offer_id}' in logs.get()


async def test_call_later_client__client_exist_send_exceeded_timeout__expected_log_warning(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings,
        logs
):
    # arrange
    offer_id = '1'
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [],
        'DEFAULT_KAFKA_TIMEOUT': 0.001,
        'OFFERS_FOR_CALL_CHANGE_KAFKA_TIMEOUT': 0.001,
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
            'clientId': operator_client,
            'callLaterDatetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )

    # assert
    assert f'???? ?????????????? ?????????????????? ?????????????? ?????????????????? ???????????? ?????? ?????????????? {operator_client}' in logs.get()
    assert f'???? ?????????????? ?????????????????? ?????????????? ?????? ?????????????? {offer_id}' in logs.get()


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
            'clientId': operator_client,
            'callLaterDatetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )
    await asyncio.sleep(1)

    # assert
    calls_messages = await kafka_service.get_messages(
        topic='preposition-admin.calls',
    )

    assert any([message.data == {
        'managerId': 60024659,
        'sourceUserId': '32131326',
        'date': ANY,
        'timestamp': ANY,
        'phone': '+79812333238',
        'callId': '2dddd3b8-3157-47cc-b50a-419052da6197',
        'status': 'callLater',
        'source': 'avito'
    } for message in calls_messages])

    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=1
    )
    assert any((message.data['offer']['id'] == '12' for message in offers_messages))


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
            'clientId': operator_client,
            'callLaterDatetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )

    # assert
    with pytest.raises(KafkaServiceError):
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
            'clientId': operator_client,
            'callLaterDatetime': datetime.now(pytz.utc).isoformat()

        },
        expected_status=200
    )

    # assert
    with pytest.raises(KafkaServiceError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )


@pytest.mark.parametrize(
    'method_name',
    [
        'delete-offer',
        'already-published-offer'
    ]
)
async def test_status_offer_methods__exist_offers_in_progress__client_accepted_message_if_no_in_progress_and_draft(
        pg,
        http,
        method_name,
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
        f'/api/admin/v1/{method_name}/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offerId': offer_in_progress,
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    calls_messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=2.5,
        count=1
    )

    assert calls_messages[0].data == {
        'managerId': 70024649,
        'sourceUserId': '32131327',
        'date': ANY,
        'timestamp': ANY,
        'phone': '+79812932338',
        'callId': 'last-call-id',
        'status': 'accepted',
        'source': 'avito'
    }

    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=1
    )
    assert offers_messages[0].data['offer']['id'] == '13'
    assert offers_messages[0].data['offer']['parsedId'] == '1d6c7dxc-3057-47cc-b50a-419052dfasf'
    assert offers_messages[0].data['offer']['clientId'] == '7'
    assert offers_messages[0].data['offer']['status'] == 'inProgress'
    assert offers_messages[0].data['offer']['priority'] == 1
    assert offers_messages[0].data['offer']['lastCallId'] == 'last-call-id'
    assert offers_messages[0].data['offer']['syncedWithKafka'] is False
    assert offers_messages[0].data['offer']['isTest'] is False
    assert offers_messages[0].data['offer']['rowVersion'] == 0


@pytest.mark.parametrize(
    'method_name, status',
    [
        ('decline-client', 'declined'),
        ('call-interrupted-client', 'callInterrupted'),
        ('phone-unavailable-client', 'phoneUnavailable'),
        ('promo-given-client', 'promoGiven'),
    ]
)
async def test_change_client_status_methods__exist_draft__client_accepted_message(
        pg,
        http,
        kafka_service,
        runtime_settings,
        offers_and_clients_fixture,
        method_name,
        status,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await runtime_settings.set({
        'TEST_OPERATOR_IDS': [60024659]
    })
    operator_user_id = 70024649
    operator_client = '7'

    # act
    await http.request(
        'POST',
        f'/api/admin/v1/{method_name}/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    calls_messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        timeout=2.5,
        count=1
    )

    assert calls_messages[0].data == {
        'managerId': 70024649,
        'sourceUserId': '32131327',
        'date': ANY,
        'timestamp': ANY,
        'phone': '+79812932338',
        'callId': 'last-call-id',
        'status': 'accepted',
        'source': 'avito'
    }

    offers_messages = await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=1
    )
    assert offers_messages[0].data['offer']['id'] == '13'
    assert offers_messages[0].data['offer']['parsedId'] == '1d6c7dxc-3057-47cc-b50a-419052dfasf'
    assert offers_messages[0].data['offer']['clientId'] == '7'
    assert offers_messages[0].data['offer']['status'] == status
    assert offers_messages[0].data['offer']['priority'] == 1
    assert offers_messages[0].data['offer']['lastCallId'] == 'last-call-id'
    assert offers_messages[0].data['offer']['syncedWithKafka'] is False
    assert offers_messages[0].data['offer']['isTest'] is False
    assert offers_messages[0].data['offer']['rowVersion'] == 0
