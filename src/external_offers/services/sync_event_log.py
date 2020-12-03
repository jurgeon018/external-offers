import logging
from datetime import datetime
from typing import Optional

from simple_settings import settings

from external_offers.entities.kafka import CallsKafkaMessage, DraftAnnouncementsKafkaMessage
from external_offers.queue.kafka import kafka_preposition_calls_producer, kafka_preposition_drafts_producer
from external_offers.repositories.postgresql import (
    get_enriched_event_log_entries_for_calls_kafka_sync,
    get_enriched_event_log_entries_for_drafts_kafka_sync,
)


logger = logging.getLogger(__name__)


async def sync_event_log(date_from: Optional[str], date_to: Optional[str]):
    """ Отправить данные по аналитике в кафку за период на основе таблицы event_log """
    logger.info('Starting event_log -> kafka syncing for dates from %s to %s including', date_from, date_to)

    datetime_from = datetime.strptime(date_from, settings.SYNC_EVENT_LOG_DATE_FORMAT) if date_from else None
    datetime_to = datetime.strptime(date_to, settings.SYNC_EVENT_LOG_DATE_FORMAT) if date_to else None

    draft_events = await get_enriched_event_log_entries_for_drafts_kafka_sync(
        date_from=datetime_from,
        date_to=datetime_to
    )

    logger.info('Fetched %d draft events', len(draft_events))

    for draft_event in draft_events:
        await kafka_preposition_drafts_producer(DraftAnnouncementsKafkaMessage(
            manager_id=draft_event.operator_user_id,
            source_user_id=draft_event.avito_user_id,
            user_id=draft_event.cian_user_id,
            phone=draft_event.client_phones[0],
            date=draft_event.created_at,
            draft=draft_event.offer_cian_id
        ))
    

    client_events = await get_enriched_event_log_entries_for_calls_kafka_sync(
        date_from=datetime_from,
        date_to=datetime_to
    )

    logger.info('Fetched %d call events', len(client_events))

    for client_event in client_events:
        await kafka_preposition_calls_producer(CallsKafkaMessage(
            manager_id=client_event.operator_user_id,
            source_user_id=client_event.avito_user_id,
            user_id=client_event.cian_user_id,
            phone=client_event.client_phones[0],
            status=client_event.client_status.value,
            date=client_event.created_at,
            source=settings.AVITO_SOURCE_NAME
        ))
