import logging
from typing import List

from cian_kafka import EntityKafkaConsumerMessage

from external_offers import entities
from external_offers.services.parsed_offers import save_parsed_offer, send_parsed_offer_change_event


logger = logging.getLogger(__name__)


async def save_parsed_offers_callback(messages: List[EntityKafkaConsumerMessage[entities.ParsedOffer]]):
    for msg in messages:
        offer_event = msg.data
        logger.info('Save parsed offer: %s', offer_event.id)
        await save_parsed_offer(offer=offer_event)


async def send_change_event(messages: List[EntityKafkaConsumerMessage[entities.ParsedOffer]]):
    for msg in messages:
        offer_event = msg.data
        logger.info('Send change parsed offer event: %s', offer_event.id)
        await send_parsed_offer_change_event(offer=offer_event)
