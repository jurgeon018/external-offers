from datetime import datetime

from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import ObjectModel
from external_offers.repositories.postgresql.offers import set_offer_publication_status_by_offer_cian_id


async def process_announcement(object_model: ObjectModel, event_date: datetime) -> None:
    if object_model.row_version:
        await set_offer_publication_status_by_offer_cian_id(
            offer_cian_id=object_model.cian_id,
            publication_status=object_model.status.value,
            row_version=object_model.row_version,
        )
