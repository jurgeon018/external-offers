from datetime import datetime

from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import ObjectModel
from external_offers.repositories.postgresql.offers import (
    get_offer_row_version_by_offer_cian_id,
    set_offer_publication_status_by_offer_cian_id,
)


async def process_announcement(object_model: ObjectModel, event_date: datetime) -> None:
    # todo: Затащить ручку коротая будет показывать был ли использован промокод на публикацию
    row_version = object_model.row_version
    cian_id = object_model.cian_id
    status = object_model.status
    offer_row_version = await get_offer_row_version_by_offer_cian_id(offer_cian_id=cian_id)
    if row_version <= offer_row_version:
        return
    await set_offer_publication_status_by_offer_cian_id(
        offer_cian_id=cian_id,
        publication_status=status.value,
        row_version=row_version,
    )
