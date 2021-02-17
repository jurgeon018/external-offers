import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers.entities.kafka import OfferForCallKafkaMessage
from external_offers.queue.kafka import offers_for_call_change_producer
from external_offers.repositories.postgresql import get_offers_by_limit_and_offset


logger = logging.getLogger(__name__)


async def send_offers_for_call_to_kafka():
    offset = 0
    offers = await get_offers_by_limit_and_offset(
        limit=settings.OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT,
        offset=offset
    )

    while offers:
        now = datetime.now(pytz.utc)
        offers_processed = 0
        offers_success = 0
        offers_failed = 0

        for offer in offers:
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
                offers_failed += 1

        offers_processed = len(offers)
        offers_success = offers_processed - offers_failed

        statsd.incr(
            stat='send-offers-for-call-to-kafka.success',
            count=offers_success
        )

        statsd.incr(
            stat='send-offers-for-call-to-kafka.failed',
            count=offers_failed
        )

        offset += offers_processed
        offers = await get_offers_by_limit_and_offset(
            limit=settings.OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT,
            offset=offset
        )
