import logging
from typing import List

from cian_kafka import EntityKafkaConsumerMessage

from external_offers import entities
from external_offers.services.parsed_offers import save_parsed_offer


logger = logging.getLogger(__name__)


async def save_parsed_offers_callback(messages: List[EntityKafkaConsumerMessage[entities.ParsedOffer]]):
    for msg in messages:
        offer_event = msg.data
        logger.info('Save parsed offer: %s', offer_event.id)
        await save_parsed_offer(offer=offer_event)
