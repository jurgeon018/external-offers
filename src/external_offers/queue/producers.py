from datetime import datetime

import pytz
from cian_core.context import get_operation_id
from cian_core.rabbitmq.decorators import mq_producer_v2

from external_offers.helpers.schemas import get_entity_schema
from external_offers.queue.entities import AnnouncementDeletedMessage, AnnouncementMessage, SourceModel
from external_offers.queue.routing_keys import ExternalOffersV1RoutingKey
from external_offers.repositories.monolith_cian_announcementapi.entities import ObjectModel


async def _get_announcement_message(model: ObjectModel, source_model: SourceModel):
    return AnnouncementMessage(
        source_model=source_model,
        model=model,
        operation_id=get_operation_id(),
        date=datetime.now(tz=pytz.UTC),
    )


async def _get_announcement_deleted_message(source_object_id: str):
    return AnnouncementDeletedMessage(
        source_object_id=source_object_id,
        operation_id=get_operation_id(),
        date=datetime.now(tz=pytz.UTC),
    )


external_offers_change_producer = mq_producer_v2(
    schema=get_entity_schema(AnnouncementMessage),
    routing_key=ExternalOffersV1RoutingKey.changed.value,
)(_get_announcement_message)
