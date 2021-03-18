from datetime import datetime

import pytz
from cian_kafka._producer.exceptions import KafkaProducerError
from simple_settings.utils import settings_stub

from external_offers.entities.kafka import CallsKafkaMessage
from external_offers.queue.helpers import send_kafka_already_published_analytics_message_if_not_test


async def test_send_already_publisher__test_user__returns_without_call(mocker):
    # arrange
    create_mock = mocker.patch(
        'external_offers.queue.helpers.create_already_published_kafka_message',
        autospec=True
    )
    operator_user_id = 1
    test_operator_user_ids = [1]
    client = mocker.MagicMock()
    client.operator_user_id = operator_user_id

    # act
    with settings_stub(
        TEST_OPERATOR_IDS=test_operator_user_ids
    ):
        await send_kafka_already_published_analytics_message_if_not_test(
            client=client,
            offer=mocker.sentinel.offer,
            parsed_offer=mocker.sentinel.parsed_offer,
        )

    # assert
    assert not create_mock.called


async def test_send_already_publisher__kafka_error__warning_call(mocker):
    # arrange
    create_mock = mocker.patch(
        'external_offers.queue.helpers.create_already_published_kafka_message',
        autospec=True
    )
    kafka_mock = mocker.patch(
        'external_offers.queue.helpers.kafka_preposition_already_published_producer',
        autospec=True
    )
    warning_mock = mocker.patch(
        'external_offers.queue.helpers.logger.warning',
        autospec=True
    )
    kafka_mock.side_effect = KafkaProducerError()
    create_mock.return_value = CallsKafkaMessage(
        manager_id=1,
        source_user_id='1',
        user_id='1',
        phone='test',
        status='waiting',
        call_id='test',
        date=datetime.now(pytz.utc),
        source='source'
    )
    operator_user_id = 1
    client = mocker.MagicMock()
    offer = mocker.MagicMock()
    client.operator_user_id = operator_user_id
    offer.id = '1'

    # act
    with settings_stub(
        TEST_OPERATOR_IDS=[]
    ):

        await send_kafka_already_published_analytics_message_if_not_test(
            client=client,
            offer=offer,
            parsed_offer=mocker.sentinel.parsed_offer,
        )

    # assert
    warning_mock.assert_has_calls(
        [
            mocker.call(
                'Не удалось отправить событие аналитики для уже опубликованного объявления %s',
                offer.id
            )
        ]
    )
