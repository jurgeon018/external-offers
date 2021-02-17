import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers.entities.kafka import ParsedOfferKafkaMessage
from external_offers.queue.kafka import parsed_offers_change_producer
from external_offers.repositories.postgresql import get_parsed_offers_by_limit_and_offset


logger = logging.getLogger(__name__)


async def send_parsed_offers_to_kafka():
    offset = 0
    offers = await get_parsed_offers_by_limit_and_offset(
        limit=settings.PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT,
        offset=offset
    )

    while offers:
        now = datetime.now(pytz.utc)
        offers_processed = 0
        offers_success = 0
        offers_failed = 0

        for offer in offers:
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
                offers_failed += 1

        offers_processed = len(offers)
        offers_success = offers_processed - offers_failed

        statsd.incr(
            stat='send-parsed-offers-to-kafka.success',
            count=offers_success
        )

        statsd.incr(
            stat='send-parsed-offers-to-kafka.failed',
            count=offers_failed
        )

        offset += offers_processed
        offers = await get_parsed_offers_by_limit_and_offset(
            limit=settings.PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT,
            offset=offset
        )
