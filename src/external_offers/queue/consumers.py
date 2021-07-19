import logging
from typing import List

from cian_core.runtime_settings import runtime_settings
from cian_kafka import EntityKafkaConsumerMessage

from external_offers import entities
from external_offers.services.parsed_offers import extract_source_from_source_object_id, save_parsed_offer


logger = logging.getLogger(__name__)


async def save_parsed_offers_callback(messages: List[EntityKafkaConsumerMessage[entities.ParsedOfferMessage]]):
    for msg in messages:
        offer_event = msg.data
        source_object_id = offer_event.source_object_id

        source = extract_source_from_source_object_id(source_object_id)
        if source not in runtime_settings.SUITABLE_EXTERNAL_SOURCES_FOR_SAVE:
            return

        logger.info('Save parsed offer: %s', offer_event.id)
        await save_parsed_offer(offer=offer_event)
