import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import ParsedOfferKafkaMessage
from external_offers.queue.kafka import parsed_offers_change_producer
from external_offers.repositories.postgresql import iterate_over_parsed_offers_sorted


logger = logging.getLogger(__name__)


async def send_parsed_offers_to_kafka():
    async with pg.get().transaction():
        async for offer in iterate_over_parsed_offers_sorted(
            prefetch=settings.PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT
        ):
            now = datetime.now(pytz.utc)

            try:
                await parsed_offers_change_producer(
                    message=ParsedOfferKafkaMessage(
                        offer=offer,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для объявления %s', offer.id)
                statsd.incr(
                    stat='send-parsed-offers-to-kafka.failed',
                )
            statsd.incr(
                stat='send-parsed-offers-to-kafka.success',
            )
