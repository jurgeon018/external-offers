import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import ClientKafkaMessage
from external_offers.queue.kafka import clients_change_producer
from external_offers.repositories.postgresql.clients import iterate_over_clients_sorted


logger = logging.getLogger(__name__)


async def send_clients_to_kafka():
    async with pg.get().transaction():
        async for client in iterate_over_clients_sorted(
            prefetch=settings.CLIENTS_FOR_KAFKA_FETCH_LIMIT
        ):
            now = datetime.now(pytz.utc)

            try:
                await clients_change_producer(
                    message=ClientKafkaMessage(
                        client=client,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для клиента %s', client.id)
                statsd.incr(
                    stat='send-clients-to-kafka.failed',
                )
            statsd.incr(
                stat='send-clients-to-kafka.success',
            )
