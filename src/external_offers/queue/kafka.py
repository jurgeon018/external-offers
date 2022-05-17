from cian_core.kafka import get_kafka_entity_producer
from cian_kafka import EntityKafkaProducer

from external_offers.entities.kafka import (
    AlreadyPublishedKafkaMessage,
    CallsKafkaMessage,
    ClientKafkaMessage,
    DeletedOfferKafkaMessage,
    DraftAnnouncementsKafkaMessage,
    EventLogKafkaMessage,
    OfferForCallKafkaMessage,
    OperatorKafkaMessage,
    ParsedOfferKafkaMessage,
    TeamKafkaMessage,
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

clients_change_producer: EntityKafkaProducer[ClientKafkaMessage] = get_kafka_entity_producer(
    topic='external-offers-clients.change',
    message_type=ClientKafkaMessage,
)

event_logs_change_producer: EntityKafkaProducer[EventLogKafkaMessage] = get_kafka_entity_producer(
    topic='external-offers-event-logs.change',
    message_type=EventLogKafkaMessage,
)

operators_change_producer: EntityKafkaProducer[OperatorKafkaMessage] = get_kafka_entity_producer(
    topic='external-offers-operators.change',
    message_type=OperatorKafkaMessage,
)

teams_change_producer: EntityKafkaProducer[TeamKafkaMessage] = get_kafka_entity_producer(
    topic='external-offers-teams.change',
    message_type=TeamKafkaMessage,
)
deleted_offers_producer: EntityKafkaProducer[DeletedOfferKafkaMessage] = get_kafka_entity_producer(
    topic='external-offers.deleted-offers-for-call',
    message_type=DeletedOfferKafkaMessage,
)
