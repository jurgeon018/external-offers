from cian_core.kafka import get_kafka_entity_producer
from cian_kafka import EntityKafkaProducer

from external_offers.entities.kafka import CallsKafkaMessage, DraftAnnouncementsKafkaMessage


kafka_preposition_admin_calls_producer: EntityKafkaProducer[CallsKafkaMessage] = get_kafka_entity_producer(
    topic='preposition-admin.calls',
    message_type=CallsKafkaMessage,
)

kafka_preposition_admin_drafts_producer: EntityKafkaProducer[DraftAnnouncementsKafkaMessage] = get_kafka_entity_producer(
    topic='preposition-admin.draft-announcements',
    message_type=DraftAnnouncementsKafkaMessage,
)

