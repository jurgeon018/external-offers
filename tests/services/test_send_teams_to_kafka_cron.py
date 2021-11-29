from unittest.mock import MagicMock

from cian_kafka import KafkaProducerError
from cian_test_utils import future

from external_offers.services.send_teams_to_kafka import send_teams_to_kafka


async def test_send_teams__kafka_error__expect_warning(mocker):
    # arrange
    iterate_over_teams_sorted_mock = mocker.patch('external_offers.services.send_teams_to_kafka'
                                                          '.iterate_over_teams_sorted')

    teams_change_producer_mock = mocker.patch('external_offers.services.send_teams_to_kafka'
                                                      '.teams_change_producer')

    logger_mock = mocker.patch('external_offers.services.send_teams_to_kafka'
                               '.logger')

    error_sentinel = mocker.sentinel
    iterate_return_value = MagicMock()
    iterate_return_value.__aiter__.return_value = [
            mocker.sentinel,
            error_sentinel,
            mocker.sentinel,
    ]
    iterate_over_teams_sorted_mock.return_value = iterate_return_value

    teams_change_producer_mock.side_effect = [
        future(None),
        future(exception=KafkaProducerError()),
        future(None)
    ]

    # act
    await send_teams_to_kafka()

    # assert
    logger_mock.warning.assert_has_calls([
        mocker.call('Не удалось отправить событие для команды %s', error_sentinel.team_id)
    ])


async def test_send_teams__producer_success_and_failed__expect_statsd_incr(mocker):
    # arrange
    iterate_over_teams_sorted_mock = mocker.patch('external_offers.services.send_teams_to_kafka'
                                                          '.iterate_over_teams_sorted')

    teams_change_producer_mock = mocker.patch('external_offers.services.send_teams_to_kafka'
                                                      '.teams_change_producer')

    statsd_incr_mock = mocker.patch('external_offers.services.'
                                    'send_teams_to_kafka.statsd.incr')


    error_sentinel = mocker.sentinel
    iterate_return_value = MagicMock()
    iterate_return_value.__aiter__.return_value = [
            mocker.sentinel,
            error_sentinel,
            mocker.sentinel,
    ]
    iterate_over_teams_sorted_mock.return_value = iterate_return_value

    teams_change_producer_mock.side_effect = [
        future(None),
        future(exception=KafkaProducerError()),
        future(None)
    ]

    # act
    await send_teams_to_kafka()

    # assert
    statsd_incr_mock.assert_has_calls([
        mocker.call(stat='send-teams-to-kafka.success'),
        mocker.call(stat='send-teams-to-kafka.failed'),
        mocker.call(stat='send-teams-to-kafka.success'),
    ])
