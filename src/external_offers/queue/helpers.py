import logging
import uuid
from datetime import datetime

import pytz
from cian_core.runtime_settings import runtime_settings
from cian_kafka._producer.exceptions import KafkaProducerError
from simple_settings import settings

from external_offers.entities import Client, Offer
from external_offers.entities.kafka import CallsKafkaMessage, OfferForCallKafkaMessage
from external_offers.enums import CallStatus
from external_offers.queue.kafka import kafka_preposition_calls_producer, offers_for_call_change_producer


logger = logging.getLogger(__name__)


async def send_kafka_calls_analytics_message_if_not_test(
    *,
    client: Client,
    offer: Offer,
    status: CallStatus,
) -> None:
    if client.operator_user_id in runtime_settings.TEST_OPERATOR_IDS or client.is_test:
        return

    calls_message = create_calls_kafka_message(
        client=client,
        offer=offer,
        status=status
    )
    offers_message = create_offers_kafka_message(
        offer=offer,
    )
    try:
        # https://jira.cian.tech/browse/CD-115234
        await offers_for_call_change_producer(
            message=offers_message,
            timeout=runtime_settings.OFFERS_FOR_CALL_CHANGE_KAFKA_TIMEOUT,
        )
    except KafkaProducerError:
        logger.warning('Не удалось отправить событие для задания %s', offer.id)
    try:
        await kafka_preposition_calls_producer(
            message=calls_message,
            timeout=runtime_settings.DEFAULT_KAFKA_TIMEOUT,
        )
    except KafkaProducerError:
        logger.warning('Не удалось отправить событие аналитики звонка для клиента %s', client.client_id)


def create_calls_kafka_message(
    *,
    client: Client,
    offer: Offer,
    status: CallStatus,
) -> CallsKafkaMessage:
    now = datetime.now(pytz.utc)

    return CallsKafkaMessage(
        manager_id=int(client.operator_user_id) if client.operator_user_id else None,
        source_user_id=client.avito_user_id,
        user_id=client.cian_user_id,
        phone=client.client_phones[0],
        status=status,
        call_id=offer.last_call_id,
        date=now,
        source=settings.AVITO_SOURCE_NAME
    )


def create_offers_kafka_message(
    *,
    offer: Offer,
) -> OfferForCallKafkaMessage:
    now = datetime.now(pytz.utc)

    return OfferForCallKafkaMessage(
        offer=offer,
        operation_id=str(uuid.uuid1()),
        date=now,
    )
