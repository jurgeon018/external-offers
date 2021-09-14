from cian_schemas import EntitySchema

from external_offers.repositories.monolith_cian_announcementapi.entities import AnnouncementReportingChangedQueueMessage


class RabbitMQAnnouncementMessageSchema(EntitySchema):
    class Meta:
        entity = AnnouncementReportingChangedQueueMessage
