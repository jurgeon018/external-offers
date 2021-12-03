from unittest.mock import MagicMock

from cian_kafka import KafkaProducerError
from cian_test_utils import future

from external_offers.services.send_operators_to_kafka import send_operators_to_kafka


async def test_send_operators__kafka_error__expect_warning(mocker):
    # arrange
    iterate_over_operators_sorted_mock = mocker.patch(
        'external_offers.services.send_operators_to_kafka.iterate_over_operators_sorted'
    )

    operators_change_producer_mock = mocker.patch(
        'external_offers.services.send_operators_to_kafka.operators_change_producer'
    )

    logger_mock = mocker.patch(
        'external_offers.services.send_operators_to_kafka.logger'
    )

    error_sentinel = mocker.sentinel
    iterate_return_value = MagicMock()
    iterate_return_value.__aiter__.return_value = [
            mocker.sentinel,
            error_sentinel,
            mocker.sentinel,
    ]
    iterate_over_operators_sorted_mock.return_value = iterate_return_value

    operators_change_producer_mock.side_effect = [
        future(None),
        future(exception=KafkaProducerError()),
        future(None)
    ]

    # act
    await send_operators_to_kafka()

    # assert
    logger_mock.warning.assert_has_calls([
        mocker.call('Не удалось отправить событие для оператора %s', error_sentinel.operator_id)
    ])


async def test_send_operators__producer_success_and_failed__expect_statsd_incr(mocker):
    # arrange
    iterate_over_operators_sorted_mock = mocker.patch(
        'external_offers.services.send_operators_to_kafka.iterate_over_operators_sorted'
    )

    operators_change_producer_mock = mocker.patch(
        'external_offers.services.send_operators_to_kafka.operators_change_producer'
    )

    statsd_incr_mock = mocker.patch(
        'external_offers.services.send_operators_to_kafka.statsd.incr'
    )

    error_sentinel = mocker.sentinel
    iterate_return_value = MagicMock()
    iterate_return_value.__aiter__.return_value = [
            mocker.sentinel,
            error_sentinel,
            mocker.sentinel,
    ]
    iterate_over_operators_sorted_mock.return_value = iterate_return_value

    operators_change_producer_mock.side_effect = [
        future(None),
        future(exception=KafkaProducerError()),
        future(None)
    ]

    # act
    await send_operators_to_kafka()

    # assert
    statsd_incr_mock.assert_has_calls([
        mocker.call(stat='send-operators-to-kafka.success'),
        mocker.call(stat='send-operators-to-kafka.failed'),
        mocker.call(stat='send-operators-to-kafka.success'),
    ])
