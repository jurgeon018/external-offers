import logging
from datetime import datetime

import pytz
from cian_kafka._producer.exceptions import KafkaProducerError
from simple_settings import settings

from external_offers.entities import Client
from external_offers.entities.kafka import CallsKafkaMessage
from external_offers.enums import ClientStatus
from external_offers.queue.kafka import kafka_preposition_calls_producer


logger = logging.getLogger(__name__)


async def send_kafka_calls_analytics_message_if_not_test(
    *,
    client: Client,
    status: ClientStatus,
    manager_id: int,
) -> None:
    if manager_id not in settings.TEST_OPERATOR_IDS:
        try:
            await kafka_preposition_calls_producer(
                message=create_calls_kafka_message(
                    client=client,
                    manager_id=manager_id,
                    status=status
                ),
                timeout=settings.DEFAULT_KAFKA_TIMEOUT
            )
        except KafkaProducerError:
            logger.warning('Не удалось отправить событие аналитики для клиента %s', client.client_id)


def create_calls_kafka_message(
    *,
    client: Client,
    manager_id: int,
    status: ClientStatus,
) -> CallsKafkaMessage:
    now = datetime.now(pytz.utc)

    return CallsKafkaMessage(
        manager_id=manager_id,
        source_user_id=client.avito_user_id,
        user_id=client.cian_user_id,
        phone=client.client_phones[0],
        status=status.value,
        date=now,
        source=settings.AVITO_SOURCE_NAME
    )
