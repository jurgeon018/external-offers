from cian_core.kafka import get_kafka_entity_producer
from cian_kafka import EntityKafkaProducer

from external_offers.entities.kafka import (
    CallsKafkaMessage,
    DraftAnnouncementsKafkaMessage,
    OfferForCallKafkaMessage,
    ParsedOfferKafkaMessage,
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
    topic='parsed-offer.change',
    message_type=ParsedOfferKafkaMessage,
)
