import logging
from datetime import datetime
from typing import List, Optional

import pytz
from cian_core.context import new_operation_id
from cian_core.rabbitmq.consumer import Message
from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_kafka import EntityKafkaConsumerMessage

from external_offers import entities
from external_offers.helpers.time import get_aware_date
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    AnnouncementReportingChangedQueueMessage,
    SwaggerObjectModel,
)
from external_offers.repositories.postgresql.offers import update_offer_is_calltracking_by_parsed_ids
from external_offers.services.announcement import process_announcement
from external_offers.services.parsed_offers import extract_source_from_source_object_id, save_parsed_offer


logger = logging.getLogger(__name__)


async def _send_telemetry(date: datetime):
    aware_date = get_aware_date(date)
    statsd.timing(
        stat='process_announcement_delta',
        delta=datetime.now(pytz.utc) - aware_date if aware_date else 0
    )


async def process_announcement_callback(messages: List[Message]) -> None:
    for message in messages:
        announcement_message: AnnouncementReportingChangedQueueMessage = message.data
        object_model: Optional[SwaggerObjectModel] = announcement_message.model
        operation_id = announcement_message.operation_id
        routing_key = message.envelope.routing_key
        with new_operation_id(operation_id), statsd.timer(f'queue.{routing_key}'):
            await process_announcement(object_model=object_model)
            await _send_telemetry(announcement_message.date)


async def save_parsed_offers_callback(messages: List[EntityKafkaConsumerMessage[entities.ParsedOfferMessage]]):
    calltracking_parsed_ids = []
    non_calltracking_parsed_ids = []
    for msg in messages:
        offer_event = msg.data
        source_object_id = offer_event.source_object_id

        source = extract_source_from_source_object_id(source_object_id)
        if source not in runtime_settings.SUITABLE_EXTERNAL_SOURCES_FOR_SAVE:
            continue

        logger.info('Save parsed offer: %s', offer_event.id)
        parsed_offer_diff = await save_parsed_offer(offer=offer_event)
        if parsed_offer_diff:
            if parsed_offer_diff.is_calltracking is True:
                calltracking_parsed_ids.append(parsed_offer_diff.id)
            elif parsed_offer_diff.is_calltracking is False:
                non_calltracking_parsed_ids.append(parsed_offer_diff.id)
    await update_offer_is_calltracking_by_parsed_ids(
        parsed_ids=calltracking_parsed_ids,
        is_calltracking=True,
    )
    await update_offer_is_calltracking_by_parsed_ids(
        parsed_ids=non_calltracking_parsed_ids,
        is_calltracking=False,
    )
