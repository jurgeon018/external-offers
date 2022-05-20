import logging
import uuid
from datetime import datetime

import pytz
from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError

from external_offers import pg
from external_offers.entities.kafka import DeletedOfferKafkaMessage
from external_offers.queue.kafka import deleted_offers_producer


logger = logging.getLogger(__name__)


async def send_deleted_offers_to_kafka(source_object_ids: list[str]) -> None:
    async with pg.get().transaction():

        for source_object_id in source_object_ids:
            now = datetime.now(pytz.utc)

            try:
                await deleted_offers_producer(
                    message=DeletedOfferKafkaMessage(
                        source_object_id=source_object_id,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=runtime_settings.get('DEFAULT_KAFKA_TIMEOUT', 1)
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для удаленного обьявления %s', source_object_id)
                statsd.incr(
                    stat='send-deleted-offers-to-kafka.failed',
                )
            statsd.incr(
                stat='send-deleted-offers-to-kafka.success',
            )
