import logging
from datetime import datetime

import pytz
from cian_kafka._producer.exceptions import KafkaProducerError
from simple_settings import settings

from external_offers.entities import Client, Offer, ParsedOffer
from external_offers.entities.kafka import AlreadyPublishedKafkaMessage, CallsKafkaMessage
from external_offers.enums import CallStatus
from external_offers.queue.kafka import kafka_preposition_already_published_producer, kafka_preposition_calls_producer


logger = logging.getLogger(__name__)


async def send_kafka_calls_analytics_message_if_not_test(
    *,
    client: Client,
    offer: Offer,
    status: CallStatus,
) -> None:
    if client.operator_user_id in settings.TEST_OPERATOR_IDS:
        return

    message = create_calls_kafka_message(
        client=client,
        offer=offer,
        status=status
    )
    try:
        await kafka_preposition_calls_producer(
            message=message,
            timeout=settings.DEFAULT_KAFKA_TIMEOUT
        )
    except KafkaProducerError:
        logger.warning('Не удалось отправить событие аналитики звонка для клиента %s', client.client_id)


async def send_kafka_already_published_analytics_message_if_not_test(
    *,
    client: Client,
    offer: Offer,
    parsed_offer: ParsedOffer,
) -> None:
    if client.operator_user_id in settings.TEST_OPERATOR_IDS:
        return

    message = create_already_published_kafka_message(
        client=client,
        offer=offer,
        parsed_offer=parsed_offer
    )
    try:
        await kafka_preposition_already_published_producer(
            message=message,
            timeout=settings.DEFAULT_KAFKA_TIMEOUT
        )
    except KafkaProducerError:
        logger.warning('Не удалось отправить событие аналитики для уже опубликованного объявления %s', offer.id)


def create_calls_kafka_message(
    *,
    client: Client,
    offer: Offer,
    status: CallStatus,
) -> CallsKafkaMessage:
    now = datetime.now(pytz.utc)

    return CallsKafkaMessage(
        manager_id=client.operator_user_id,
        source_user_id=client.avito_user_id,
        user_id=client.cian_user_id,
        phone=client.client_phones[0],
        status=status,
        call_id=offer.last_call_id,
        date=now,
        source=settings.AVITO_SOURCE_NAME
    )


def create_already_published_kafka_message(
    *,
    client: Client,
    offer: Offer,
    parsed_offer: ParsedOffer,
) -> CallsKafkaMessage:
    now = datetime.now(pytz.utc)

    return AlreadyPublishedKafkaMessage(
        manager_id=client.operator_user_id,
        source_object_id=parsed_offer.source_object_id,
        source_user_id=client.avito_user_id,
        phone=client.client_phones[0],
        call_id=offer.last_call_id,
        date=now,
    )
