from cian_kafka import KafkaProducerError
from cian_test_utils import future

from external_offers.services.send_parsed_offers_to_kafka import send_parsed_offers_to_kafka


async def test_send_offers_for_call__kafka_error__expect_warning(mocker):
    # arrange
    get_offers_by_limit_and_offset_mock = mocker.patch('external_offers.services.send_parsed_offers_to_kafka'
                                                       '.get_parsed_offers_by_limit_and_offset')

    parsed_offers_change_producer_mock = mocker.patch('external_offers.services.send_parsed_offers_to_kafka'
                                                      '.parsed_offers_change_producer')

    logger_mock = mocker.patch('external_offers.services.send_parsed_offers_to_kafka'
                               '.logger')

    error_sentinel = mocker.sentinel
    get_offers_by_limit_and_offset_mock.side_effect = [
        future(
            [
                mocker.sentinel,
                error_sentinel,
                mocker.sentinel,
            ],
        ),
        future([])
    ]

    parsed_offers_change_producer_mock.side_effect = [
        future(None),
        future(exception=KafkaProducerError()),
        future(None)
    ]

    # act
    await send_parsed_offers_to_kafka()

    # assert
    logger_mock.warning.assert_has_calls([
        mocker.call('Не удалось отправить событие для объявления %s', error_sentinel.id)
    ])


async def test_send_offers_for_call__producer_success_and_failed__expect_statsd_incr(mocker):
    # arrange
    get_offers_by_limit_and_offset_mock = mocker.patch('external_offers.services.send_parsed_offers_to_kafka'
                                                       '.get_parsed_offers_by_limit_and_offset')

    parsed_offers_change_producer_mock = mocker.patch('external_offers.services.send_parsed_offers_to_kafka'
                                                      '.parsed_offers_change_producer')

    statsd_incr_mock = mocker.patch('external_offers.services.'
                                    'send_parsed_offers_to_kafka.statsd.incr')

    error_sentinel = mocker.sentinel
    get_offers_by_limit_and_offset_mock.side_effect = [
        future(
            [
                mocker.sentinel,
                error_sentinel,
                mocker.sentinel,
            ],
        ),
        future([])
    ]

    parsed_offers_change_producer_mock.side_effect = [
        future(None),
        future(exception=KafkaProducerError()),
        future(None)
    ]

    # act
    await send_parsed_offers_to_kafka()

    # assert
    statsd_incr_mock.assert_has_calls([
        mocker.call(stat='send-parsed-offers-to-kafka.success', count=2),
        mocker.call(stat='send-parsed-offers-to-kafka.failed', count=1)
    ])
