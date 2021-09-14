import logging
from typing import List

from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.queue.helpers import create_offers_kafka_message
from external_offers.queue.kafka import offers_for_call_change_producer
from external_offers.repositories.postgresql import (
    iterate_over_offers_for_call_sorted,
    sync_offers_for_call_with_kafka_by_ids,
)


logger = logging.getLogger(__name__)


async def send_offers_for_call_to_kafka():
    async with pg.get().transaction():

        offer_ids: List[int] = []

        async for offer in iterate_over_offers_for_call_sorted(
            prefetch=settings.OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT
        ):

            try:
                await offers_for_call_change_producer(
                    message=create_offers_kafka_message(offer=offer),
                    timeout=settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для задания %s', offer.id)
                statsd.incr(
                    stat='send-offers-for-call-to-kafka.failed',
                )
            offer_ids.append(offer.id)
            statsd.incr(
                stat='send-offers-for-call-to-kafka.success',
            )

        await sync_offers_for_call_with_kafka_by_ids(offer_ids)
