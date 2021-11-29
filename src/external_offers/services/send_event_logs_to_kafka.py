import logging
import uuid
from datetime import datetime

import pytz
from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError

from external_offers import pg
from external_offers.entities.kafka import EventLogKafkaMessage
from external_offers.queue.kafka import event_logs_change_producer
from external_offers.repositories.postgresql.event_log import iterate_over_event_logs_sorted


logger = logging.getLogger(__name__)


async def send_event_logs_to_kafka():
    async with pg.get().transaction():
        async for event_log in iterate_over_event_logs_sorted(
            prefetch=runtime_settings.EVENT_LOGS_FOR_KAFKA_FETCH_LIMIT
        ):
            now = datetime.now(pytz.utc)

            try:
                await event_logs_change_producer(
                    message=EventLogKafkaMessage(
                        event_log=event_log,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=runtime_settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для лога %s', event_log.id)
                statsd.incr(
                    stat='send-event-logs-to-kafka.failed',
                )
            statsd.incr(
                stat='send-event-logs-to-kafka.success',
            )
