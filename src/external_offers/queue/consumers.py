import logging
from typing import List

from cian_core.context import new_operation_id
from cian_core.runtime_settings import runtime_settings
from cian_kafka import EntityKafkaConsumerMessage

from external_offers import entities
from external_offers.services.parsed_offers import save_parsed_offer, send_parsed_offer_change_event


logger = logging.getLogger(__name__)


_SOURCE_AND_ID_DELIMETER = '_'
_SOURCE_INDEX = 0


def extract_source_from_source_object_id(source_object_id: str) -> str:
    return source_object_id.split(_SOURCE_AND_ID_DELIMETER)[_SOURCE_INDEX]


async def save_parsed_offers_callback(messages: List[EntityKafkaConsumerMessage[entities.ParsedOfferMessage]]):
    for msg in messages:
        offer_event = msg.data
        source_object_id = offer_event.source_object_id

        source = extract_source_from_source_object_id(source_object_id)
        if source not in runtime_settings.SUITABLE_EXTERNAL_SOURCES_FOR_SAVE:
            return

        logger.info('Save parsed offer: %s', offer_event.id)
        await save_parsed_offer(offer=offer_event)


async def send_change_event(messages: List[EntityKafkaConsumerMessage[entities.ParsedOfferMessage]]):
    for msg in messages:
        with new_operation_id():
            offer_event = msg.data
            source_object_id = offer_event.source_object_id

            source = extract_source_from_source_object_id(source_object_id)
            if source not in runtime_settings.SUITABLE_EXTERNAL_SOURCES_FOR_SEND:
                return

            logger.info('Send change parsed offer event: %s', offer_event.id)
            await send_parsed_offer_change_event(offer=offer_event)
