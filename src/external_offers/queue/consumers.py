import logging
from datetime import datetime
from typing import List
import pytz

from cian_core.runtime_settings import runtime_settings
from cian_core.context import new_operation_id
from cian_core.statsd import statsd
from cian_core.rabbitmq.consumer import Message
from cian_kafka import EntityKafkaConsumerMessage

from external_offers import entities
from external_offers.services.parsed_offers import extract_source_from_source_object_id, save_parsed_offer
from external_offers.queue.entities import AnnouncementMessage
from external_offers.helpers.time import get_aware_date
from external_offers.services.announcement import process_announcement


logger = logging.getLogger(__name__)


async def process_announcement_callback(messages: List[Message]) -> None:
    for message in messages:
        announcement_message: AnnouncementMessage = message.data
        object_model = announcement_message.model
        operation_id = announcement_message.operation_id
        routing_key = message.envelope.routing_key
        with new_operation_id(operation_id), statsd.timer(f'queue.{routing_key}'):
            try:
                await process_announcement(object_model=object_model, event_date=announcement_message.date)
            except:
                logger.exception('Process announcement error id: %s, key: %s', object_model.id, routing_key)
                raise
            finally:
                statsd.timing(
                    stat='process_announcement_delta',
                    delta=datetime.now(pytz.utc) - get_aware_date(announcement_message.date)
                )


async def save_parsed_offers_callback(messages: List[EntityKafkaConsumerMessage[entities.ParsedOfferMessage]]):
    for msg in messages:
        offer_event = msg.data
        source_object_id = offer_event.source_object_id

        source = extract_source_from_source_object_id(source_object_id)
        if source not in runtime_settings.SUITABLE_EXTERNAL_SOURCES_FOR_SAVE:
            return

        logger.info('Save parsed offer: %s', offer_event.id)
        await save_parsed_offer(offer=offer_event)
