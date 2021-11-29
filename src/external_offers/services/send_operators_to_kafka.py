import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import OperatorKafkaMessage
from external_offers.queue.kafka import operators_change_producer
from external_offers.repositories.postgresql import iterate_over_operators_sorted


logger = logging.getLogger(__name__)


async def send_operators_to_kafka():
    async with pg.get().transaction():
        async for operator in iterate_over_operators_sorted(
            prefetch=settings.OPERATORS_FOR_KAFKA_FETCH_LIMIT
        ):
            now = datetime.now(pytz.utc)

            try:
                await operators_change_producer(
                    message=OperatorKafkaMessage(
                        operator=operator,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для оператора %s', operator.id)
                statsd.incr(
                    stat='send-operators-to-kafka.failed',
                )
            statsd.incr(
                stat='send-operators-to-kafka.success',
            )
