import logging
from datetime import datetime

from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    ObjectModel,
    Status as PublicationStatus,
)
from external_offers.repositories.postgresql.clients import (
    set_client_unactivated_by_offer_cian_id,
    set_client_done_by_offer_cian_id,
)
from external_offers.repositories.postgresql.offers import (
    get_offer_row_version_by_offer_cian_id,
    set_offer_publication_status_by_offer_cian_id,
    set_offer_done_by_offer_cian_id,
)


logger = logging.getLogger(__name__)


async def process_announcement(object_model: ObjectModel, event_date: datetime) -> None:
    offer_cian_id = object_model.cian_id
    row_version = object_model.row_version
    publication_status = object_model.status
    if not row_version:
        return
    offer_row_version = await get_offer_row_version_by_offer_cian_id(offer_cian_id)
    if offer_row_version > row_version:
        return
    await set_offer_publication_status_by_offer_cian_id(
        offer_cian_id=offer_cian_id,
        publication_status=publication_status.value,
        row_version=row_version,
    )
    if publication_status == PublicationStatus.draft:
        await set_client_unactivated_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
        )
    elif publication_status == PublicationStatus.published:
        await set_client_done_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
        )
        await set_offer_done_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
        )
