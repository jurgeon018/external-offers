from cian_kafka import KafkaConsumerMessage
from cian_test_utils import future

from external_offers.queue.consumers import save_parsed_offers_callback


async def test_save_parsed_offers_callback(mocker):
    # arrange
    messages = [
        KafkaConsumerMessage(
            value=b'{}',
            topic='test',
            offset=1,
            partition=1
        )
    ]
    logger = mocker.patch('external_offers.queue.consumers.logger')

    save_parsed_offer = mocker.patch(
        'external_offers.queue.consumers.save_parsed_offer',
        return_value=future()
    )

    # act
    await save_parsed_offers_callback(messages=messages)

    # assert
    logger.warning.assert_called_with('Error while parsing offers: %s', b'{}')
    save_parsed_offer.assert_not_called()
