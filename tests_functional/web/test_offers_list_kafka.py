import os

import pytest
from cian_json import json
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
    messages = await kafka_service.get_messages(
        topic='preposition-admin.calls'
    )
    assert len(messages) == 1

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
    messages = await kafka_service.get_messages(
        topic='preposition-admin.calls'
    )
    assert len(messages) == 1

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
    messages = []
    with pytest.raises(TimeoutError):
        messages = await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            timeout=1.5,
            count=1
        )
    assert len(messages) == 0
