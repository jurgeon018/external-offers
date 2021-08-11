from cian_schemas import EntitySchema

from external_offers.queue.entities import AnnouncementMessage


class RabbitMQAnnouncementMessageSchema(EntitySchema):
    class Meta:
        entity = AnnouncementMessage
