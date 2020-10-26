import logging
from typing import List

from cian_kafka import KafkaConsumerMessage

from external_offers.schemas.parsaed_offers import ParsedOfferSchema
from external_offers.services.parsed_offers import save_parsed_offer


logger = logging.getLogger(__name__)


async def save_parsed_offers_callback(messages: List[KafkaConsumerMessage]):
    for msg in messages:
        offer_event, errors = ParsedOfferSchema().loads(msg.value)
        if errors:
            logger.warning('Error while parsing offers: %s', msg.value)
            continue

        await save_parsed_offer(offer=offer_event)
