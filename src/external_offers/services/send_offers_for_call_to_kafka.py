import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import OfferForCallKafkaMessage
from external_offers.queue.kafka import offers_for_call_change_producer
from external_offers.repositories.postgresql import iterate_over_offers_for_call_sorted


logger = logging.getLogger(__name__)


async def send_offers_for_call_to_kafka():
    async with pg.get().transaction():
        async for offer in iterate_over_offers_for_call_sorted(
            prefetch=settings.OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT
        ):
            now = datetime.now(pytz.utc)

            try:
                await offers_for_call_change_producer(
                    message=OfferForCallKafkaMessage(
                        offer=offer,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для задания %s', offer.id)
                statsd.incr(
                    stat='send-offers-for-call-to-kafka.failed',
                )
            statsd.incr(
                stat='send-offers-for-call-to-kafka.success',
            )
