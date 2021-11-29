from cian_core.kafka import get_kafka_entity_producer
from cian_kafka import EntityKafkaProducer

from external_offers.entities.kafka import (
    AlreadyPublishedKafkaMessage,
    CallsKafkaMessage,
    DraftAnnouncementsKafkaMessage,
    OfferForCallKafkaMessage,
    ParsedOfferKafkaMessage,
    ClientsKafkaMessage,
    EventLogsKafkaMessage,
    OperatorsKafkaMessage,
    TeamsKafkaMessage,
)


kafka_preposition_calls_producer: EntityKafkaProducer[CallsKafkaMessage] = get_kafka_entity_producer(
    topic='preposition-admin.calls',
    message_type=CallsKafkaMessage,
)

kafka_preposition_drafts_producer: EntityKafkaProducer[DraftAnnouncementsKafkaMessage] = get_kafka_entity_producer(
    topic='preposition-admin.draft-announcements',
    message_type=DraftAnnouncementsKafkaMessage,
)

offers_for_call_change_producer: EntityKafkaProducer[OfferForCallKafkaMessage] = get_kafka_entity_producer(
    topic='offers-for-call.change',
    message_type=OfferForCallKafkaMessage,
)

parsed_offers_change_producer: EntityKafkaProducer[ParsedOfferKafkaMessage] = get_kafka_entity_producer(
    topic='parsed-offers.change',
    message_type=ParsedOfferKafkaMessage,
)

clients_change_producer: EntityKafkaProducer[ClientsKafkaMessage] = get_kafka_entity_producer(
    topic='clients.change',
    message_type=ClientsKafkaMessage,
)

event_logs_change_producer: EntityKafkaProducer[EventLogsKafkaMessage] = get_kafka_entity_producer(
    topic='event_logs.change',
    message_type=EventLogsKafkaMessage,
)

operators_change_producer: EntityKafkaProducer[OperatorsKafkaMessage] = get_kafka_entity_producer(
    topic='operators.change',
    message_type=OperatorsKafkaMessage,
)

teams_change_producer: EntityKafkaProducer[TeamsKafkaMessage] = get_kafka_entity_producer(
    topic='teams.change',
    message_type=TeamsKafkaMessage,
)
