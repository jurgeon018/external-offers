from cian_kafka import EntityKafkaConsumerMessage

from external_offers.entities import ParsedOffer
from external_offers.queue.consumers import save_parsed_offers_callback


async def test_save_parsed_offer__non_suitable_source__return_without_calls(
    mocker,
    fake_settings
):
    # assert
    parsed_offer_message = mocker.MagicMock(
        spec=ParsedOffer
    )
    parsed_offer_message.source_object_id = '1_1'

    message = mocker.MagicMock(
        spec=EntityKafkaConsumerMessage
    )
    message.data = parsed_offer_message

    await fake_settings.set(
        SUITABLE_EXTERNAL_SOURCES_FOR_SAVE=[]
    )
    save_mock = mocker.patch('external_offers.queue.consumers.'
                             'save_parsed_offer')

    # act
    await save_parsed_offers_callback(
        messages=[message]
    )

    # assert
    assert not save_mock.called

